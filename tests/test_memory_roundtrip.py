"""Round-trip tests against a REAL temporary Sibyl Memory database — not
a mock. Maps to SPEC-001 section 12: A2 (Session 1 persists the complete
case), invariant 8 (an immutable record is never overwritten).

Every test constructs its own MemoryStore.local() against a fresh
tempfile, so tests never share state or leak into
~/.sibyl-memory/memory.db.
"""

from __future__ import annotations

import json
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from finne.memory.client import IntegrityError, MemoryStore
from finne.memory.schema import (
    AuthorityEventRecord,
    CaseVersionRecord,
    OutcomeRecord,
    OwnerPolicySnapshot,
)
from finne.models import AuthorityState, Outcome, Proposal, RiskTier

BASELINE_FACTS = Proposal(
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    target_class="yield_vault_conservative",
    function="deposit",
    counterparty_risk_tier=RiskTier.LOW,
    amount=Decimal("25000.00"),
    proposed_at="2026-09-03T00:00:00Z",
)


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield MemoryStore.local(Path(tmpdir) / "test_memory.db")


def make_case_version(decision_version_id: str = "DV-001-V1", **overrides) -> CaseVersionRecord:
    fields = dict(
        decision_version_id=decision_version_id,
        facts=BASELINE_FACTS,
        authorized_amount=Decimal("10000.00"),
    )
    fields.update(overrides)
    return CaseVersionRecord(**fields)


# --- W1 / R2: case versions ------------------------------------------


def test_case_version_round_trips_exactly(store):
    record = make_case_version()
    store.write_case_version(record)
    assert store.read_case_version("DV-001-V1") == record


def test_case_version_is_write_once(store):
    """Invariant 8: an immutable record is never overwritten."""
    record = make_case_version()
    store.write_case_version(record)
    with pytest.raises(IntegrityError):
        store.write_case_version(make_case_version(authorized_amount=Decimal("99999.00")))
    # The original value must survive the attempted overwrite untouched.
    assert store.read_case_version("DV-001-V1").authorized_amount == Decimal("10000.00")


def test_missing_case_version_reads_as_none(store):
    assert store.read_case_version("DOES-NOT-EXIST") is None


def test_malformed_stored_case_version_reads_as_none_not_permission(store):
    """A record that fails validation is treated as absent, never as
    permission (PREREQ-003 section 4) — proven against the real store,
    not just the in-memory dataclass validation from seam (a)."""
    store._client.set_entity(
        "finne_case_version",
        "DV-CORRUPT",
        {"decision_version_id": "DV-CORRUPT", "authorized_amount": "not-a-decimal"},
    )
    assert store.read_case_version("DV-CORRUPT") is None


# --- W4: outcomes -------------------------------------------------------


def test_outcome_round_trips_exactly(store):
    record = OutcomeRecord(
        decision_version_id="DV-001-V1", outcome=Outcome.SUCCESS, base_tx_hash="0xabc123"
    )
    store.write_outcome(record)
    assert store.read_outcome("DV-001-V1") == record


def test_outcome_is_write_once(store):
    record = OutcomeRecord(
        decision_version_id="DV-001-V1", outcome=Outcome.SUCCESS, base_tx_hash="0xabc123"
    )
    store.write_outcome(record)
    with pytest.raises(IntegrityError):
        store.write_outcome(
            OutcomeRecord(decision_version_id="DV-001-V1", outcome=Outcome.FAILURE, base_tx_hash=None)
        )
    assert store.read_outcome("DV-001-V1").outcome == Outcome.SUCCESS


def test_missing_outcome_reads_as_none(store):
    assert store.read_outcome("DOES-NOT-EXIST") is None


# --- W2 / R5: owner-policy snapshots -------------------------------------


def make_snapshot(**overrides) -> OwnerPolicySnapshot:
    fields = dict(
        max_amount=Decimal("25000.00"),
        network="base",
        asset="USDC",
        action_class="capital_deployment",
        approved_target_classes=("demo_receipt", "yield_vault_conservative"),
        approved_functions=("recordAuthorization", "deposit"),
        cold_start_autonomous_amount=Decimal("0.00"),
    )
    fields.update(overrides)
    return OwnerPolicySnapshot(**fields)


def test_owner_policy_snapshot_round_trips_exactly(store):
    snapshot = make_snapshot()
    store.write_owner_policy_snapshot("DV-001-V1", snapshot)
    assert store.read_owner_policy_snapshot("DV-001-V1") == snapshot


def test_owner_policy_snapshot_is_write_once(store):
    store.write_owner_policy_snapshot("DV-001-V1", make_snapshot())
    with pytest.raises(IntegrityError):
        store.write_owner_policy_snapshot(
            "DV-001-V1", make_snapshot(max_amount=Decimal("99999.00"))
        )
    assert store.read_owner_policy_snapshot("DV-001-V1").max_amount == Decimal("25000.00")


def test_missing_owner_policy_snapshot_reads_as_none(store):
    assert store.read_owner_policy_snapshot("DOES-NOT-EXIST") is None


def test_malformed_stored_snapshot_reads_as_none(store):
    key = "owner_policy_snapshot/DV-CORRUPT"
    store._client.set_reference(key, json.dumps({"max_amount": "not-a-decimal"}))
    assert store.read_owner_policy_snapshot("DV-CORRUPT") is None


# --- W3 / R3: append-only authority events and folding --------------------


def test_fold_with_no_events_returns_none(store):
    assert store.fold_authority_state("DV-001-V1") is None


def test_fold_after_single_event(store):
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-001-V1",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner_as_decision_reviewer",
            reason="confirmation creates the draft",
        )
    )
    assert store.fold_authority_state("DV-001-V1") == AuthorityState.DRAFT


def test_fold_after_draft_then_active_returns_active(store):
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-001-V1",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner_as_decision_reviewer",
            reason="confirmation",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-001-V1",
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner_as_authority_steward",
            reason="activation",
        )
    )
    assert store.fold_authority_state("DV-001-V1") == AuthorityState.ACTIVE


def test_fold_orders_by_timestamp_not_write_order(store):
    """Events written with an explicit, deliberately non-monotonic `ts`
    must still fold in chronological order, not write order."""
    later_event = AuthorityEventRecord(
        decision_version_id="DV-TS",
        previous_status=AuthorityState.DRAFT,
        new_status=AuthorityState.ACTIVE,
        changed_by="owner",
        reason="activation",
    )
    earlier_event = AuthorityEventRecord(
        decision_version_id="DV-TS",
        previous_status=None,
        new_status=AuthorityState.DRAFT,
        changed_by="owner",
        reason="confirmation",
    )
    # Write the chronologically LATER event first.
    store._client.write_event(extra=later_event.to_extra(), ts="2026-01-02T00:00:00Z")
    store._client.write_event(extra=earlier_event.to_extra(), ts="2026-01-01T00:00:00Z")
    assert store.fold_authority_state("DV-TS") == AuthorityState.ACTIVE


def test_fold_excludes_events_for_a_different_decision_version(store):
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-001-V1",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="confirmation",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-999-V1",
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner",
            reason="activation",
        )
    )
    assert store.fold_authority_state("DV-001-V1") == AuthorityState.DRAFT


def test_fold_excludes_non_authority_journal_entries(store):
    """A journal entry that happens to text-match but isn't tagged as an
    authority event (e.g. a plain narrative event) must not be folded in."""
    store._client.write_event(acted=["DV-001-V1 mentioned in passing"])
    assert store.fold_authority_state("DV-001-V1") is None


def test_fold_excludes_malformed_authority_events(store):
    """A malformed authority event is treated as absent, not permission —
    it must not crash the fold or silently count as a valid transition."""
    store._client.write_event(
        extra={
            "kind": "finne_authority_event",
            "decision_version_id": "DV-001-V1",
            "new_status": "not-a-real-status",
            "changed_by": "owner",
            "reason": "r",
        }
    )
    assert store.fold_authority_state("DV-001-V1") is None


# --- R1: candidate search -------------------------------------------------


def test_search_cases_finds_matching_records(store):
    store.write_case_version(make_case_version("DV-001-V1"))
    store.write_case_version(
        make_case_version(
            "DV-005-V1",
            facts=Proposal(
                **{**BASELINE_FACTS.__dict__, "target_class": "yield_vault_aggressive"}
            ),
        )
    )
    results = store.search_cases("yield_vault_conservative")
    ids = {r.decision_version_id for r in results}
    assert ids == {"DV-001-V1"}


def test_search_cases_excludes_malformed_records(store):
    store.write_case_version(make_case_version("DV-001-V1"))
    store._client.set_entity(
        "finne_case_version",
        "DV-CORRUPT",
        {"decision_version_id": "DV-CORRUPT", "authorized_amount": "not-a-decimal"},
    )
    results = store.search_cases("base")
    ids = {r.decision_version_id for r in results}
    assert "DV-CORRUPT" not in ids
    assert "DV-001-V1" in ids


# --- Tenant isolation -----------------------------------------------------


def test_tenants_are_isolated_on_a_shared_database_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "shared.db"
        store_a = MemoryStore.local(path, tenant_id="11111111-1111-1111-1111-111111111111")
        store_b = MemoryStore.local(path, tenant_id="22222222-2222-2222-2222-222222222222")

        store_a.write_case_version(make_case_version("DV-SHARED"))

        assert store_a.read_case_version("DV-SHARED") is not None
        assert store_b.read_case_version("DV-SHARED") is None


# --- Second independent Codex review: transition matrix + chain validation,
# non-dict crash guards, schema_version enforcement, truncation detection,
# and write concurrency. All fixed below with regression tests.
# -----------------------------------------------------------------------


def test_no_prior_state_to_active_is_unconstructable():
    """The exact case the second review found folding silently accepted:
    a case must reach `active` only via `draft`, never directly."""
    with pytest.raises(Exception):
        AuthorityEventRecord(
            decision_version_id="DV-X",
            previous_status=None,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner",
            reason="illegal shortcut",
        )


def test_withdrawn_to_active_is_unconstructable():
    """The other exact case the second review found: withdrawn is
    terminal and must never transition to anything, including back to
    active."""
    with pytest.raises(Exception):
        AuthorityEventRecord(
            decision_version_id="DV-X",
            previous_status=AuthorityState.WITHDRAWN,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner",
            reason="illegal reactivation",
        )


def test_superseded_has_no_legal_outgoing_transition():
    """Terminal-state enforcement, checked against the full matrix rather
    than one example: no LEGAL_TRANSITIONS entry has superseded as a
    'from' state."""
    from finne.memory.schema import LEGAL_TRANSITIONS

    assert not any(frm == AuthorityState.SUPERSEDED for frm, _to in LEGAL_TRANSITIONS)
    assert not any(frm == AuthorityState.WITHDRAWN for frm, _to in LEGAL_TRANSITIONS)


def test_fold_stops_at_first_chain_inconsistency(store):
    """A legally-constructible event (draft -> active is a valid PAIR)
    whose previous_status does not match what the sequence actually
    accumulated (no draft event ever happened) must not be applied. The
    fold must return None here, not `active` — there is no valid draft
    event underneath it, only an isolated, inconsistent one."""
    orphaned_activation = AuthorityEventRecord(
        decision_version_id="DV-ORPHAN",
        previous_status=AuthorityState.DRAFT,
        new_status=AuthorityState.ACTIVE,
        changed_by="owner",
        reason="claims a draft that never happened",
    )
    store.append_authority_event(orphaned_activation)
    assert store.fold_authority_state("DV-ORPHAN") is None


def test_fold_uses_valid_prefix_before_a_chain_break(store):
    """Draft is correctly established, then a later event's claimed
    previous_status doesn't match (a fork/duplicate). The fold must keep
    `draft` — the valid prefix — not apply the inconsistent event."""
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-FORK",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="genuine confirmation",
        )
    )
    # This event's own previous_status claims ACTIVE, but the accumulated
    # state after the event above is DRAFT — inconsistent.
    store._client.write_event(
        extra={
            "kind": "finne_authority_event",
            "schema_version": 1,
            "decision_version_id": "DV-FORK",
            "previous_status": "active",
            "new_status": "questioned",
            "changed_by": "owner",
            "reason": "inconsistent fork",
        }
    )
    assert store.fold_authority_state("DV-FORK") == AuthorityState.DRAFT


def test_non_dict_journal_body_does_not_crash_the_fold(store):
    """set_entity/write_event's own signatures permit non-dict payloads.
    A list body must be excluded, not crash the fold with AttributeError
    from a bare .get() call."""
    store._client.write_event(extra=["not", "a", "mapping"])
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-MIXED",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="genuine event alongside the malformed one",
        )
    )
    # Must not raise, and must still find the one genuine event.
    assert store.fold_authority_state("DV-MIXED") == AuthorityState.DRAFT


def test_missing_schema_version_reads_as_none(store):
    store._client.set_entity(
        "finne_case_version",
        "DV-NOVERSION",
        {
            "decision_version_id": "DV-NOVERSION",
            "facts": {
                "network": "base",
                "asset": "USDC",
                "action_class": "capital_deployment",
                "target_class": "yield_vault_conservative",
                "function": "deposit",
                "counterparty_risk_tier": "low",
                "amount": "25000.00",
                "proposed_at": "2026-09-03T00:00:00Z",
            },
            "authorized_amount": "10000.00",
            # schema_version deliberately omitted
        },
    )
    assert store.read_case_version("DV-NOVERSION") is None


def test_wrong_schema_version_reads_as_none(store):
    record = make_case_version("DV-FUTURE")
    body = record.to_body()
    body["schema_version"] = 999
    store._client.set_entity("finne_case_version", "DV-FUTURE", body)
    assert store.read_case_version("DV-FUTURE") is None


def test_non_dict_stored_body_reads_as_none_not_crash(store):
    """set_entity's signature permits a list body. A stored list must be
    treated as absent, not crash with AttributeError from a bare .get()
    on schema_version."""
    store._client.set_entity("finne_case_version", "DV-LISTBODY", ["not", "a", "dict"])
    assert store.read_case_version("DV-LISTBODY") is None


def test_journal_search_truncation_is_detected_and_fails_safe(store, monkeypatch):
    """Reproduces the real, empirically-confirmed cap (limit // 4) at a
    small, fast scale by lowering the module's search-limit constant
    rather than writing thousands of real events — the underlying
    client behavior being exercised is identical, just at a size that
    runs in milliseconds instead of writing 8000+ real rows."""
    import finne.memory.client as client_module

    monkeypatch.setattr(client_module, "_JOURNAL_SEARCH_LIMIT", 20)
    monkeypatch.setattr(client_module, "_JOURNAL_SEARCH_EFFECTIVE_CAP", 5)

    # A legal cycle (draft -> active -> questioned -> active -> ...) to
    # generate six distinct, individually-valid events — one more than
    # the lowered effective cap — without violating the transition matrix.
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-TRUNC",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="event 0",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-TRUNC",
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner",
            reason="event 1",
        )
    )
    for i in range(4):
        current, nxt = (
            (AuthorityState.ACTIVE, AuthorityState.QUESTIONED)
            if i % 2 == 0
            else (AuthorityState.QUESTIONED, AuthorityState.ACTIVE)
        )
        store.append_authority_event(
            AuthorityEventRecord(
                decision_version_id="DV-TRUNC",
                previous_status=current,
                new_status=nxt,
                changed_by="owner",
                reason=f"event {i + 2}",
            )
        )

    with pytest.raises(client_module.MemoryTruncationError):
        store._authority_events_for("DV-TRUNC")
    # The public method fails safe instead of propagating the exception.
    assert store.fold_authority_state("DV-TRUNC") is None


def test_concurrent_writers_in_one_process_do_not_double_write():
    """The in-process write lock closes the check-then-write race for
    callers sharing one MemoryStore. Only one of two racing writers may
    succeed; the other must see IntegrityError, never a silent
    overwrite."""
    import threading

    with tempfile.TemporaryDirectory() as tmpdir:
        shared_store = MemoryStore.local(Path(tmpdir) / "race.db")
        results: list[str] = []

        def attempt(tag: str) -> None:
            try:
                shared_store.write_case_version(
                    make_case_version("DV-RACE", authorized_amount=Decimal(tag))
                )
                results.append(f"wrote:{tag}")
            except IntegrityError:
                results.append(f"blocked:{tag}")

        threads = [threading.Thread(target=attempt, args=(str(i),)) for i in range(1, 3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert sorted(r.split(":")[0] for r in results) == ["blocked", "wrote"]
        # The stored value matches whichever attempt actually won — no
        # partial or corrupted write occurred.
        final = shared_store.read_case_version("DV-RACE")
        assert final is not None
        winner_tag = next(r.split(":")[1] for r in results if r.startswith("wrote"))
        assert final.authorized_amount == Decimal(winner_tag)
