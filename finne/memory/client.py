"""The Sibyl Memory adapter — the only module in this repository that
imports sibyl_memory_client, per PREREQ-003 section 17's module
boundary.

Enforces, above an underlying store that does not enforce them itself
(verified empirically against sibyl-memory-client 0.8.0 — set_entity
silently overwrites by default):

- Immutability: finne_case_version and finne_outcome records, and
  owner_policy_snapshot references, are write-once. An attempted
  overwrite raises IntegrityError rather than silently succeeding.
- Append-only authority history: current authority state is always
  DERIVED by folding every authority event for a decision version in
  chronological order — never read from, or written into, a mutable
  "current state" field.
- Validation on read: a stored record that fails schema validation is
  treated as absent, never as permission (PREREQ-003 section 4).

VERIFY-AT-BUILD result (see prompts/ for the session this was
confirmed in): sibyl-memory-client 0.8.0's real API differs from the
published README, which documents an older surface. Confirmed
empirically:

- MemoryClient.local(path) requires no `sibyl init` credentials for
  local operations — account_id/session_token/credentials_* are all
  optional kwargs defaulting to None. The stated need for browser
  auth applies to the CLI's cloud-tier features, not this library's
  core five-tier local API.
- get_entity raises NotFoundError for a missing name; get_reference
  and get_state return None instead.
- write_event(*, evaluated=None, acted=None, forward=None, extra=None,
  ts=None) has no dedicated "kind" field — authority events are tagged
  via extra["kind"] and identified that way on read.
- read_events(limit=...) returns entries in descending ts order and has
  no content filter, so it cannot reliably retrieve "every event for
  this decision version" once a tenant has more events than the limit.
  client.search(query, tiers=("journal",)) does content-filter the
  journal tier via FTS5 and was used instead — the AE-<sequence>
  fallback PREREQ-003 anticipated was not needed.
- get_reference's return shape differs from get_entity's: a dict passed
  to set_reference comes back JSON-stringified under a "body" key
  (`{"body": '{"a": 1}', "metadata": None, "updated_at": ...}`), not
  re-parsed into a nested dict the way get_entity's body is. This isn't
  in the README at all. read_owner_policy_snapshot below parses it.
- client.search(..., tiers=("journal",), limit=N) silently returns at
  most N // 4 real results, regardless of how many actually match —
  verified empirically across limit=20/100/400/1000 (5/25/100/250
  returned) and confirmed the ratio holds up to at least limit=100000.
  There is no pagination parameter to retrieve more. _authority_events_for
  requests a high limit and treats hitting the resulting effective cap
  as a truncation signal, per fold_authority_state below, rather than
  silently trusting a possibly-incomplete history.

Second independent Codex review (2026-09-04) found the first version of
this module did not validate the authority transition matrix or
cross-event chain consistency, crashed on a non-dict journal payload
instead of treating it as absent, silently accepted a missing or wrong
schema_version, and did not address concurrent-writer races. All fixed;
see LEGAL_TRANSITIONS in finne.memory.schema, the isinstance guards in
_authority_events_for, _require_current_schema_version in
finne.memory.schema, and the write lock below.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from sibyl_memory_client import MemoryClient, NotFoundError

from finne.memory.schema import (
    AUTHORITY_EVENT_KIND,
    LEGAL_TRANSITIONS,
    AuthorityEventRecord,
    CaseVersionRecord,
    OutcomeRecord,
    OwnerPolicySnapshot,
)
from finne.models import AuthorityState, ValidationError

CASE_VERSION_CATEGORY = "finne_case_version"
OUTCOME_CATEGORY = "finne_outcome"
DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# search(..., tiers=("journal",), limit=N) silently caps real results at
# N // 4 — verified empirically, undocumented, no pagination available.
# 8000 gives an effective cap of 2000 real events per decision version,
# far beyond any realistic corpus for this project, while remaining a
# real, detectable ceiling.
_JOURNAL_SEARCH_LIMIT = 8000
_JOURNAL_SEARCH_EFFECTIVE_CAP = _JOURNAL_SEARCH_LIMIT // 4


class IntegrityError(Exception):
    """Raised when code attempts to overwrite an immutable record.

    This is a programming-error signal, not a "malformed data" signal —
    it is never caught and downgraded to "absent." Overwriting an
    immutable record is a bug in the caller, and must be visible as one.
    """


class MemoryTruncationError(Exception):
    """Raised internally when a journal search returns at or above the
    empirically-observed cap, meaning the true event count is unknown
    and the retrieved set may be incomplete. fold_authority_state catches
    this and fails safe to None — an authority state that cannot be
    fully verified is treated the same as one that does not exist,
    never as permission."""


def _owner_policy_snapshot_key(decision_version_id: str) -> str:
    return f"owner_policy_snapshot/{decision_version_id}"


class MemoryStore:
    """Wraps a sibyl_memory_client.MemoryClient with the immutability,
    authority-folding, and read-validation guarantees this domain
    requires. Every method here is the load-bearing read or write
    boundary documented in PREREQ-003 section 3 (W1-W5, R1-R5).

    Concurrency: the check-then-write immutability enforcement below
    (get_entity/get_reference, then set_entity/set_reference) is not
    atomic against the underlying store — sibyl-memory-client exposes no
    compare-and-set primitive. A threading.Lock serializes writes made
    through the SAME MemoryStore instance, closing the race for
    concurrent callers within one process. It does not, and cannot,
    protect against two separate OS processes writing to the same
    database file concurrently. This is an accepted, explicit
    constraint, not an oversight: this project's architecture is
    single-writer-at-a-time by design — Session 1 fully exits before
    Session 2 starts (SPEC-001 section 4) — so cross-process concurrent
    writes to the same decision version are not a scenario this project
    needs to defend against.
    """

    def __init__(self, client: MemoryClient) -> None:
        self._client = client
        self._write_lock = threading.Lock()

    @classmethod
    def local(
        cls,
        path: str | Path = "~/.sibyl-memory/memory.db",
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> "MemoryStore":
        return cls(MemoryClient.local(path, tenant_id=tenant_id))

    # --- W1 / R2: immutable case versions -----------------------------

    def write_case_version(self, record: CaseVersionRecord) -> None:
        with self._write_lock:
            if self._entity_exists(CASE_VERSION_CATEGORY, record.decision_version_id):
                raise IntegrityError(
                    f"case version {record.decision_version_id!r} already exists; "
                    "immutable records are write-once"
                )
            self._client.set_entity(
                CASE_VERSION_CATEGORY, record.decision_version_id, record.to_body()
            )

    def read_case_version(self, decision_version_id: str) -> CaseVersionRecord | None:
        try:
            entity = self._client.get_entity(CASE_VERSION_CATEGORY, decision_version_id)
        except NotFoundError:
            return None
        try:
            return CaseVersionRecord.from_body(entity["body"])
        except (ValidationError, KeyError, ValueError, TypeError):
            # A malformed stored record is treated as absent, never as
            # permission — per PREREQ-003 section 4.
            return None

    # --- W4 / part of R4: execution outcomes ---------------------------

    def write_outcome(self, record: OutcomeRecord) -> None:
        with self._write_lock:
            if self._entity_exists(OUTCOME_CATEGORY, record.decision_version_id):
                raise IntegrityError(
                    f"outcome for {record.decision_version_id!r} already exists; "
                    "immutable records are write-once"
                )
            self._client.set_entity(
                OUTCOME_CATEGORY, record.decision_version_id, record.to_body()
            )

    def read_outcome(self, decision_version_id: str) -> OutcomeRecord | None:
        try:
            entity = self._client.get_entity(OUTCOME_CATEGORY, decision_version_id)
        except NotFoundError:
            return None
        try:
            return OutcomeRecord.from_body(entity["body"])
        except (ValidationError, KeyError, ValueError, TypeError):
            return None

    # --- W2 / R5: owner-policy snapshots --------------------------------

    def write_owner_policy_snapshot(
        self, decision_version_id: str, snapshot: OwnerPolicySnapshot
    ) -> None:
        key = _owner_policy_snapshot_key(decision_version_id)
        with self._write_lock:
            if self._client.get_reference(key) is not None:
                raise IntegrityError(
                    f"owner-policy snapshot for {decision_version_id!r} already exists; "
                    "immutable records are write-once"
                )
            self._client.set_reference(key, snapshot.to_body())

    def read_owner_policy_snapshot(
        self, decision_version_id: str
    ) -> OwnerPolicySnapshot | None:
        wrapper = self._client.get_reference(_owner_policy_snapshot_key(decision_version_id))
        if wrapper is None:
            return None
        # get_reference's return shape differs from get_entity's: the
        # dict passed to set_reference comes back JSON-stringified under
        # a "body" key, not re-parsed into a dict — verified empirically,
        # not documented anywhere. write_owner_policy_snapshot always
        # writes a dict, so the stored body is always a JSON object
        # string here.
        try:
            body = json.loads(wrapper["body"])
            return OwnerPolicySnapshot.from_body(body)
        except (ValidationError, KeyError, ValueError, TypeError, json.JSONDecodeError):
            return None

    # --- W3 / R3: append-only authority events --------------------------

    def append_authority_event(self, record: AuthorityEventRecord) -> None:
        self._client.write_event(extra=record.to_extra())

    def fold_authority_state(self, decision_version_id: str) -> AuthorityState | None:
        """Derive the current authority state by replaying every valid
        event for this decision version in chronological order, enforcing
        both the transition matrix (PREREQ-002) and cross-event chain
        consistency. Returns None if no event exists yet, if the journal
        search result may be truncated (fails safe rather than trusting
        an incomplete history), or if the very first event in the
        sequence is already invalid — never a default/assumed status."""
        try:
            events = self._authority_events_for(decision_version_id)
        except MemoryTruncationError:
            return None
        if not events:
            return None
        events.sort(key=lambda pair: pair[0])

        current_state: AuthorityState | None = None
        for _ts, event in events:
            # Cross-event consistency: this event's own claimed
            # previous_status must match what the sequence has actually
            # accumulated so far. A mismatch means a fork, gap, or
            # inconsistency in the recorded history — trust only the
            # valid prefix before it, not this event or anything after.
            if event.previous_status != current_state:
                break
            # Defense in depth: AuthorityEventRecord.__post_init__
            # already makes an illegal (previous, new) pair
            # unconstructable, but a future schema change or direct
            # storage tampering must not silently bypass this too.
            if (current_state, event.new_status) not in LEGAL_TRANSITIONS:
                break
            current_state = event.new_status
        return current_state

    def _authority_events_for(
        self, decision_version_id: str
    ) -> list[tuple[str, AuthorityEventRecord]]:
        results = self._client.search(
            decision_version_id, tiers=("journal",), limit=_JOURNAL_SEARCH_LIMIT
        )
        if len(results) >= _JOURNAL_SEARCH_EFFECTIVE_CAP:
            # FTS5 relevance ordering means truncation could drop ANY
            # subset of matches, not necessarily the oldest or newest —
            # we cannot tell whether this is the true, complete count or
            # a silent truncation at the server's undocumented cap.
            raise MemoryTruncationError(
                f"journal search for {decision_version_id!r} returned "
                f"{len(results)} results, at or above the empirically "
                f"observed cap of {_JOURNAL_SEARCH_EFFECTIVE_CAP}"
            )
        events: list[tuple[str, AuthorityEventRecord]] = []
        for item in results:
            body = item.get("body")
            if not isinstance(body, dict):
                continue
            extra = body.get("extra")
            if not isinstance(extra, dict):
                continue
            if extra.get("kind") != AUTHORITY_EVENT_KIND:
                continue
            # FTS5 relevance matching can be approximate; verify the
            # exact identifier rather than trusting the search hit.
            if extra.get("decision_version_id") != decision_version_id:
                continue
            ts = item.get("ts", "")
            try:
                events.append((ts, AuthorityEventRecord.from_extra(extra, ts)))
            except (ValidationError, KeyError, ValueError, TypeError):
                # A malformed event is treated as absent, not permission —
                # it is simply excluded from the fold.
                continue
        return events

    # --- R1: candidate precedent generation -----------------------------

    def search_cases(self, query: str, *, limit: int = 20) -> list[CaseVersionRecord]:
        results = self._client.search_entities(query, category=CASE_VERSION_CATEGORY, limit=limit)
        records: list[CaseVersionRecord] = []
        for item in results:
            try:
                records.append(CaseVersionRecord.from_body(item["body"]))
            except (ValidationError, KeyError, ValueError, TypeError):
                continue
        return records

    # --- W5: in-flight proposal working state ---------------------------
    # Deliberately not exposed here beyond the primitive set_state/
    # get_state already on MemoryClient: per PREREQ-003, this tier is
    # overwritable scratch space that must never be read across
    # sessions, so it carries none of this module's immutability or
    # fold guarantees and does not need a dedicated wrapper method.

    # --- demo/test reset only — NOT part of the load-bearing W1-W5/R1-R5
    # boundary, and deliberately not named like one -----------------------

    def clear_all_case_data_for_demo_reset(self, *, confirm_tenant_id: str) -> None:
        """Deletes every finne_case_version and finne_outcome entity for
        this store's tenant. This is a hard, permanent delete
        (MemoryClient.delete_entity), not the reversible archive_entity —
        appropriate only because it is scoped to a dedicated demo tenant,
        never to a tenant holding real data. `confirm_tenant_id` must
        match the tenant this MemoryStore was actually constructed
        against (verified via the underlying client, not merely echoed
        back), so a caller cannot invoke a permanent hard-delete against
        the wrong tenant by passing the wrong MemoryStore instance —
        this method is not restricted to any particular tenant value,
        so that guard is the only thing standing between it and
        accidental data loss.

        This method exists so scripts/reset_demo.py does not need to
        reach into this class's private _client attribute directly,
        preserving the module boundary that finne.memory.client is the
        only code that talks to sibyl_memory_client. It does NOT clear
        owner-policy-snapshot references or authority-event/relationship
        journal entries — sibyl-memory-client exposes no delete for
        either tier, so a decision version that has already been fully
        created (case, snapshot, and authority events) cannot be reset
        in place; see scripts/reset_demo.py's own pre-flight check."""
        actual_tenant_id = self._client.get_tenant()
        if confirm_tenant_id != actual_tenant_id:
            raise ValueError(
                f"refusing to clear case data: confirm_tenant_id "
                f"{confirm_tenant_id!r} does not match this store's actual "
                f"tenant {actual_tenant_id!r}"
            )
        for category in (CASE_VERSION_CATEGORY, OUTCOME_CATEGORY):
            for entity in self._client.list_entities(category=category, limit=1000):
                self._client.delete_entity(category, entity["name"])

    # --- internal ---------------------------------------------------------

    def _entity_exists(self, category: str, name: str) -> bool:
        try:
            self._client.get_entity(category, name)
            return True
        except NotFoundError:
            return False
