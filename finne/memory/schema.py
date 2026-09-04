"""Storage-shaped records and their JSON (de)serialization for Sibyl
Memory.

These are distinct from finne.models's authority-computation types
(OwnerPolicy, Proposal, EvaluatedCandidate, ...): this module defines
what actually gets written to and read from the memory substrate.
finne.memory.client assembles these into finne.models types for the
authority engine to consume.

Every record carries schema_version. Validation happens on both write
(fail loudly — a bug in this process) and read (fail safely — treat a
malformed stored record as absent, never as permission, per
PREREQ-003 section 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from finne.models import (
    AuthorityState,
    Outcome,
    Proposal,
    RiskTier,
    ValidationError,
    require_finite_decimal,
    require_nonempty,
)

SCHEMA_VERSION = 1


def _require_current_schema_version(body: Any) -> None:
    """A missing or non-matching schema_version is rejected, not
    defaulted. A record from a future or unknown schema must never be
    silently treated as if it were the current one — that is exactly the
    kind of ambiguity PREREQ-003 section 4's "malformed record is absent,
    never permission" rule exists to prevent.

    Also guards the non-dict case explicitly: set_entity's own signature
    permits a list body, and a corrupted or tampered record could be
    anything JSON-serializable. Every from_body/from_extra caller in this
    module calls this first, so this one check protects all of them —
    without it, `.get()` on a non-dict raises AttributeError, which none
    of the callers' except clauses catch, crashing the read instead of
    treating it as absent.
    """
    if not isinstance(body, dict):
        raise ValidationError(f"stored record body must be a dict, got {type(body).__name__}")
    version = body.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"schema_version {version!r} does not match the current "
            f"schema version {SCHEMA_VERSION}; record treated as absent"
        )


def _decimal_or_raise(field_name: str, value: Any) -> Decimal:
    """Parse a monetary field from a raw stored body. Only a string is
    accepted — the same Decimal-only-from-string discipline as
    finne.policy, for the same reason: a raw float or int surviving JSON
    round-tripping must never silently become a Decimal via binary
    approximation."""
    if not isinstance(value, str):
        raise ValidationError(
            f"{field_name} must be a string in stored records, got "
            f"{type(value).__name__}: {value!r}"
        )
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValidationError(f"{field_name} is not a valid decimal: {value!r}") from exc
    if not parsed.is_finite():
        raise ValidationError(f"{field_name} must be finite, got {value!r}")
    return parsed


def _facts_to_dict(facts: Proposal) -> dict[str, Any]:
    return {
        "network": facts.network,
        "asset": facts.asset,
        "action_class": facts.action_class,
        "target_class": facts.target_class,
        "function": facts.function,
        "counterparty_risk_tier": facts.counterparty_risk_tier.value,
        "amount": str(facts.amount),
        "proposed_at": facts.proposed_at,
    }


def _facts_from_dict(body: dict[str, Any]) -> Proposal:
    try:
        return Proposal(
            network=body["network"],
            asset=body["asset"],
            action_class=body["action_class"],
            target_class=body["target_class"],
            function=body["function"],
            counterparty_risk_tier=RiskTier(body["counterparty_risk_tier"]),
            amount=_decimal_or_raise("amount", body["amount"]),
            proposed_at=body["proposed_at"],
        )
    except (KeyError, ValueError) as exc:
        raise ValidationError(f"malformed matter facts: {exc}") from exc


@dataclass(frozen=True)
class CaseVersionRecord:
    """The immutable content of one decision version, per PREREQ-002's
    DecisionRecord (narrowed to what this domain needs). Written once to
    finne_case_version/<decision_version_id>; never overwritten."""

    decision_version_id: str
    facts: Proposal
    authorized_amount: Decimal
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_nonempty("decision_version_id", self.decision_version_id)
        require_finite_decimal("authorized_amount", self.authorized_amount)
        if not isinstance(self.facts, Proposal):
            raise ValidationError(
                f"facts must be a Proposal, got {type(self.facts).__name__}"
            )

    def to_body(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision_version_id": self.decision_version_id,
            "facts": _facts_to_dict(self.facts),
            "authorized_amount": str(self.authorized_amount),
        }

    @staticmethod
    def from_body(body: dict[str, Any]) -> "CaseVersionRecord":
        _require_current_schema_version(body)
        return CaseVersionRecord(
            decision_version_id=body["decision_version_id"],
            facts=_facts_from_dict(body["facts"]),
            authorized_amount=_decimal_or_raise("authorized_amount", body["authorized_amount"]),
            schema_version=body["schema_version"],
        )


@dataclass(frozen=True)
class OutcomeRecord:
    """The observed result of executing an authorized action, per W4.
    Written once to finne_outcome/<decision_version_id>."""

    decision_version_id: str
    outcome: Outcome
    base_tx_hash: str | None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_nonempty("decision_version_id", self.decision_version_id)
        if self.base_tx_hash is not None and not isinstance(self.base_tx_hash, str):
            raise ValidationError(
                f"base_tx_hash must be a string or None, got {type(self.base_tx_hash).__name__}"
            )

    def to_body(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision_version_id": self.decision_version_id,
            "outcome": self.outcome.value,
            "base_tx_hash": self.base_tx_hash,
        }

    @staticmethod
    def from_body(body: dict[str, Any]) -> "OutcomeRecord":
        _require_current_schema_version(body)
        return OutcomeRecord(
            decision_version_id=body["decision_version_id"],
            outcome=Outcome(body["outcome"]),
            base_tx_hash=body.get("base_tx_hash"),
            schema_version=body["schema_version"],
        )


@dataclass(frozen=True)
class OwnerPolicySnapshot:
    """A frozen copy of the owner policy in force when a decision was
    made, per W2. Written once to reference key
    owner_policy_snapshot/<decision_version_id>, so an audit can
    reconstruct which ceiling applied without trusting the current
    config/owner_policy.toml."""

    max_amount: Decimal
    network: str
    asset: str
    action_class: str
    approved_target_classes: tuple[str, ...]
    approved_functions: tuple[str, ...]
    cold_start_autonomous_amount: Decimal
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_finite_decimal("max_amount", self.max_amount)
        require_finite_decimal("cold_start_autonomous_amount", self.cold_start_autonomous_amount)
        require_nonempty("network", self.network)
        require_nonempty("asset", self.asset)
        require_nonempty("action_class", self.action_class)

    def to_body(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "max_amount": str(self.max_amount),
            "network": self.network,
            "asset": self.asset,
            "action_class": self.action_class,
            "approved_target_classes": list(self.approved_target_classes),
            "approved_functions": list(self.approved_functions),
            "cold_start_autonomous_amount": str(self.cold_start_autonomous_amount),
        }

    @staticmethod
    def from_body(body: dict[str, Any]) -> "OwnerPolicySnapshot":
        _require_current_schema_version(body)
        return OwnerPolicySnapshot(
            max_amount=_decimal_or_raise("max_amount", body["max_amount"]),
            network=body["network"],
            asset=body["asset"],
            action_class=body["action_class"],
            approved_target_classes=tuple(body["approved_target_classes"]),
            approved_functions=tuple(body["approved_functions"]),
            cold_start_autonomous_amount=_decimal_or_raise(
                "cold_start_autonomous_amount", body["cold_start_autonomous_amount"]
            ),
            schema_version=body["schema_version"],
        )


# The sentinel used in write_event(extra=...) to identify authority
# events among all journal entries, since write_event has no dedicated
# "kind" parameter of its own.
AUTHORITY_EVENT_KIND = "finne_authority_event"

# The authority transition matrix, per PREREQ-002's Authority Transitions
# table. None represents "no prior state." superseded and withdrawn are
# terminal — deliberately absent as a "from" state, so any transition
# out of them is rejected by construction, not by a separate check.
LEGAL_TRANSITIONS: frozenset[tuple[AuthorityState | None, AuthorityState]] = frozenset(
    {
        (None, AuthorityState.DRAFT),
        (AuthorityState.DRAFT, AuthorityState.ACTIVE),
        (AuthorityState.DRAFT, AuthorityState.WITHDRAWN),
        (AuthorityState.ACTIVE, AuthorityState.QUESTIONED),
        (AuthorityState.ACTIVE, AuthorityState.SUPERSEDED),
        (AuthorityState.ACTIVE, AuthorityState.WITHDRAWN),
        (AuthorityState.QUESTIONED, AuthorityState.ACTIVE),
        (AuthorityState.QUESTIONED, AuthorityState.SUPERSEDED),
        (AuthorityState.QUESTIONED, AuthorityState.WITHDRAWN),
    }
)


@dataclass(frozen=True)
class AuthorityEventRecord:
    """One append-only authority transition, per PREREQ-002's
    AuthorityEvent. Written via write_event(extra=...); never updated or
    deleted. Current authority state is derived by folding every event
    for a decision_version_id in chronological order — this record is
    never stored as, or overwritten into, a mutable "current state"
    field.

    __post_init__ enforces the transition matrix intrinsically: an event
    whose (previous_status, new_status) pair is not in LEGAL_TRANSITIONS
    cannot be constructed at all, whether from live code or deserialized
    from storage via from_extra. This is what makes "No prior state ->
    active" or "withdrawn -> active" impossible to represent as a valid
    event, rather than merely inconvenient to fold correctly.
    finne.memory.client.MemoryStore.fold_authority_state additionally
    verifies CROSS-event consistency — that each event's own
    previous_status actually matches the state accumulated from the
    events before it — which this single-record check cannot see.
    """

    decision_version_id: str
    previous_status: AuthorityState | None
    new_status: AuthorityState
    changed_by: str
    reason: str
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_nonempty("decision_version_id", self.decision_version_id)
        require_nonempty("changed_by", self.changed_by)
        require_nonempty("reason", self.reason)
        if (self.previous_status, self.new_status) not in LEGAL_TRANSITIONS:
            raise ValidationError(
                f"illegal authority transition: {self.previous_status!r} -> "
                f"{self.new_status!r} is not in the authorized transition matrix "
                "(PREREQ-002 Authority Transitions table)"
            )

    def to_extra(self) -> dict[str, Any]:
        return {
            "kind": AUTHORITY_EVENT_KIND,
            "schema_version": self.schema_version,
            "decision_version_id": self.decision_version_id,
            "previous_status": self.previous_status.value if self.previous_status else None,
            "new_status": self.new_status.value,
            "changed_by": self.changed_by,
            "reason": self.reason,
        }

    @staticmethod
    def from_extra(extra: dict[str, Any], ts: str) -> "AuthorityEventRecord":
        if not isinstance(extra, dict):
            raise ValidationError(f"authority event extra must be a dict, got {type(extra).__name__}")
        _require_current_schema_version(extra)
        previous = extra.get("previous_status")
        return AuthorityEventRecord(
            decision_version_id=extra["decision_version_id"],
            previous_status=AuthorityState(previous) if previous else None,
            new_status=AuthorityState(extra["new_status"]),
            changed_by=extra["changed_by"],
            reason=extra["reason"],
            schema_version=extra["schema_version"],
        )


# PrecedentRelationshipRecord (follows/distinguishes/questions/supersedes,
# per PREREQ-002's PrecedentRelationship) was implemented here in seam
# (c) round 1 and removed again in round 2: PREREQ-002's own contract
# requires fact_ids/citation_ids to reference real, human-validated
# CitationEdge/Fact entities with a rejection-audit path
# (CitationAttemptAuditEvent) — a genuine validated-reference subsystem,
# not a shape a few tuples of strings can satisfy. Building that is out
# of scope per SPEC-001 section 15 ("multi-domain precedent support"),
# is required by none of SPEC-001's fourteen acceptance criteria, and
# is not one of PREREQ-003 section 3's load-bearing W1-W5/R1-R5
# operations — removing it changes nothing about what invariant 6's
# memory-deleted control proves. Deferred; see ACTIVE_DEMO_DESIGN.md
# section 6.
