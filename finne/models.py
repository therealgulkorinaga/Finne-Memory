"""Frozen data models for the Finné Memory authority path.

No I/O anywhere in this module. Every amount is `decimal.Decimal` — float
arithmetic is prohibited in the authority path per DECISION-023.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

SCHEMA_VERSION = 1


class ValidationError(ValueError):
    """Raised when a model's invariants are violated.

    Per PREREQ-003 section 4: a record that fails validation is treated as
    absent, never as permission. Callers on the read path must catch this
    and degrade to "no candidate," not propagate partial trust.
    """


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def rank(self) -> int:
        return {"low": 0, "medium": 1, "high": 2}[self.value]

    def not_worse_than(self, other: "RiskTier") -> bool:
        """True if this tier is no riskier than `other` (self <= other)."""
        return self.rank <= other.rank


class AuthorityState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    QUESTIONED = "questioned"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class Outcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class AuthorizationResult(str, Enum):
    ALLOW = "allow"
    CONSTRAIN = "constrain"
    BLOCK = "block"
    ESCALATE = "escalate"


def require_finite_decimal(name: str, value: Decimal) -> None:
    """Reject anything that is not a genuinely finite `decimal.Decimal`.

    Float arithmetic is prohibited anywhere in the authority path
    (DECISION-023) — a `float`, including `float('nan')`, must never
    silently pass as a monetary amount. `Decimal('NaN')` and
    `Decimal('Infinity')` are valid `Decimal` instances but are rejected
    explicitly here, before any ordering comparison is attempted, because
    comparing NaN with `<` raises `decimal.InvalidOperation` rather than
    failing cleanly as a `ValidationError`.
    """
    if not isinstance(value, Decimal):
        raise ValidationError(
            f"{name} must be a decimal.Decimal, got {type(value).__name__}"
        )
    if not value.is_finite():
        raise ValidationError(f"{name} must be finite, got {value}")


def require_positive_or_zero(name: str, value: Decimal) -> None:
    require_finite_decimal(name, value)
    if value < 0:
        raise ValidationError(f"{name} must be >= 0, got {value}")


def require_nonempty(name: str, value: str) -> None:
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string, got {type(value).__name__}")
    if not value or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class OwnerPolicy:
    """The owner permission ceiling. Read-only to the application — no
    code path in this repository writes this back. Corresponds to `OP-001`
    in docs/product/ACTIVE_DEMO_DESIGN.md section 1."""

    max_amount: Decimal
    network: str
    asset: str
    action_class: str
    approved_target_classes: tuple[str, ...]
    approved_functions: tuple[str, ...]
    unknown_situation_behaviour: str
    cold_start_autonomous_amount: Decimal
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_positive_or_zero("max_amount", self.max_amount)
        require_positive_or_zero(
            "cold_start_autonomous_amount", self.cold_start_autonomous_amount
        )
        if self.cold_start_autonomous_amount > self.max_amount:
            raise ValidationError(
                "cold_start_autonomous_amount cannot exceed max_amount"
            )
        require_nonempty("network", self.network)
        require_nonempty("asset", self.asset)
        require_nonempty("action_class", self.action_class)
        if not self.approved_target_classes:
            raise ValidationError("approved_target_classes must be non-empty")
        if not self.approved_functions:
            raise ValidationError("approved_functions must be non-empty")
        if self.unknown_situation_behaviour not in ("escalate_to_owner",):
            raise ValidationError(
                f"unrecognized unknown_situation_behaviour: "
                f"{self.unknown_situation_behaviour!r}"
            )


@dataclass(frozen=True)
class HardPolicy:
    """A currently-active supplementary constraint, distinct from the
    static OwnerPolicy file. Defaults to a no-op (no additional
    restriction beyond OwnerPolicy) because no V1 scenario requires an
    active temporary override; see the design note in
    prompts/2026-09-03-task-001-and-seam-a-kickoff.md.

    max_amount_override, when set, can only narrow — never widen — the
    owner ceiling. This is enforced in finne.authority.engine, not here.
    """

    max_amount_override: Decimal | None = None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.max_amount_override is not None:
            require_positive_or_zero("max_amount_override", self.max_amount_override)


@dataclass(frozen=True)
class Proposal:
    """The action an agent is currently proposing."""

    network: str
    asset: str
    action_class: str
    target_class: str
    function: str
    counterparty_risk_tier: RiskTier
    amount: Decimal
    proposed_at: str  # ISO-8601 timestamp string; provenance only
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_nonempty("network", self.network)
        require_nonempty("asset", self.asset)
        require_nonempty("action_class", self.action_class)
        require_nonempty("target_class", self.target_class)
        require_nonempty("function", self.function)
        require_positive_or_zero("amount", self.amount)
        require_nonempty("proposed_at", self.proposed_at)


@dataclass(frozen=True)
class MaterialDifference:
    """One dimension on which a candidate differs from the current
    proposal, per the comparability rule in ACTIVE_DEMO_DESIGN.md section 3."""

    dimension: str
    precedent_value: str
    current_value: str


@dataclass(frozen=True)
class Comparability:
    """The result of comparing a proposal against one candidate case."""

    is_comparable: bool
    material_differences: tuple[MaterialDifference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.is_comparable and self.material_differences:
            raise ValidationError(
                "a comparable candidate cannot carry material differences"
            )
        if not self.is_comparable and not self.material_differences:
            raise ValidationError(
                "a non-comparable candidate must state at least one material difference"
            )


@dataclass(frozen=True)
class EvaluatedCandidate:
    """A retrieved prior case, already compared against the current
    proposal and with its authority state already folded from the
    append-only journal. This is the shape the pure authority engine
    consumes — it does not know or care how this was assembled."""

    decision_version_id: str
    authorized_amount: Decimal
    authority_state: AuthorityState
    outcome: Outcome
    comparability: Comparability
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_nonempty("decision_version_id", self.decision_version_id)
        require_positive_or_zero("authorized_amount", self.authorized_amount)

    def is_eligible(self) -> bool:
        """Eligible for learned-constraint derivation per LCP-001: must be
        comparable, active, and successful. Draft, questioned, superseded,
        and withdrawn cases are excluded here but remain retrievable and
        displayable by the caller — this method only gates derivation."""
        return (
            self.comparability.is_comparable
            and self.authority_state == AuthorityState.ACTIVE
            and self.outcome == Outcome.SUCCESS
        )


@dataclass(frozen=True)
class LearnedConstraint:
    """The output of finne.authority.derivation — the maximum amount
    earned from active, comparable, successful precedent, or the
    owner's cold-start default when no such precedent exists."""

    learned_max_amount: Decimal
    basis: str  # "cold_start" or "precedent"
    supporting_decision_version_ids: tuple[str, ...] = field(default_factory=tuple)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_positive_or_zero("learned_max_amount", self.learned_max_amount)
        if self.basis not in ("cold_start", "precedent"):
            raise ValidationError(f"unrecognized basis: {self.basis!r}")
        if self.basis == "precedent" and not self.supporting_decision_version_ids:
            raise ValidationError(
                "a precedent-basis constraint must name its supporting decision versions"
            )
        if self.basis == "cold_start" and self.supporting_decision_version_ids:
            raise ValidationError(
                "a cold-start-basis constraint cannot name supporting decision versions"
            )


@dataclass(frozen=True)
class AuthorizationDecision:
    """The deterministic, final output of the authority engine. This is
    the only thing that may authorize an action."""

    result: AuthorizationResult
    authorized_amount: Decimal
    binding_constraint: str
    cited_precedents: tuple[str, ...]
    material_differences: tuple[MaterialDifference, ...]
    explanation: str
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        require_positive_or_zero("authorized_amount", self.authorized_amount)
        if self.result == AuthorizationResult.BLOCK and self.authorized_amount != 0:
            raise ValidationError("a blocked decision must authorize zero")
        if self.result == AuthorizationResult.ESCALATE and self.authorized_amount != 0:
            raise ValidationError("an escalated decision must authorize zero")
