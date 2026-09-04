"""Adversarial tests proving the models reject non-Decimal, NaN, and
infinite monetary values at every boundary — not just negative ones.

Found by Codex review: nothing previously checked that a monetary field
was actually a `decimal.Decimal` rather than a Python `float`, so a float
(including `float('nan')`, which passes a naive `< 0` check silently)
could leak all the way into a final AuthorizationDecision.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from finne.models import (
    AuthorityState,
    AuthorizationDecision,
    AuthorizationResult,
    Comparability,
    EvaluatedCandidate,
    HardPolicy,
    LearnedConstraint,
    Outcome,
    OwnerPolicy,
    Proposal,
    RiskTier,
    ValidationError,
)

VALID_PROPOSAL_KWARGS = dict(
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    target_class="yield_vault_conservative",
    function="deposit",
    counterparty_risk_tier=RiskTier.LOW,
    proposed_at="2026-09-03T00:00:00Z",
)

BAD_MONETARY_VALUES = [
    25000.0,  # plain float
    float("nan"),  # float NaN — passes naive `< 0` checks silently
    float("inf"),  # float infinity
    Decimal("NaN"),  # Decimal NaN — raises InvalidOperation on `< 0`, not ValidationError
    Decimal("Infinity"),
    Decimal("-Infinity"),
    "25000.00",  # a string, not a Decimal
    None,
]


@pytest.mark.parametrize("bad_value", BAD_MONETARY_VALUES)
def test_proposal_amount_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        Proposal(**{**VALID_PROPOSAL_KWARGS, "amount": bad_value})


@pytest.mark.parametrize("bad_value", BAD_MONETARY_VALUES)
def test_owner_policy_max_amount_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        OwnerPolicy(
            max_amount=bad_value,
            network="base",
            asset="USDC",
            action_class="capital_deployment",
            approved_target_classes=("demo_receipt",),
            approved_functions=("deposit",),
            unknown_situation_behaviour="escalate_to_owner",
            cold_start_autonomous_amount=Decimal("0.00"),
        )


@pytest.mark.parametrize("bad_value", BAD_MONETARY_VALUES)
def test_owner_policy_cold_start_autonomous_amount_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        OwnerPolicy(
            max_amount=Decimal("25000.00"),
            network="base",
            asset="USDC",
            action_class="capital_deployment",
            approved_target_classes=("demo_receipt",),
            approved_functions=("deposit",),
            unknown_situation_behaviour="escalate_to_owner",
            cold_start_autonomous_amount=bad_value,
        )


@pytest.mark.parametrize("bad_value", [v for v in BAD_MONETARY_VALUES if v is not None])
def test_hard_policy_override_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        HardPolicy(max_amount_override=bad_value)


def test_hard_policy_none_override_is_still_valid():
    HardPolicy(max_amount_override=None)  # must not raise


@pytest.mark.parametrize("bad_value", [v for v in BAD_MONETARY_VALUES if v is not None])
def test_evaluated_candidate_authorized_amount_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        EvaluatedCandidate(
            decision_version_id="DV-TEST-001",
            authorized_amount=bad_value,
            authority_state=AuthorityState.ACTIVE,
            outcome=Outcome.SUCCESS,
            comparability=Comparability(is_comparable=True),
        )


@pytest.mark.parametrize("bad_value", [v for v in BAD_MONETARY_VALUES if v is not None])
def test_learned_constraint_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        LearnedConstraint(learned_max_amount=bad_value, basis="cold_start")


@pytest.mark.parametrize("bad_value", [v for v in BAD_MONETARY_VALUES if v is not None])
def test_authorization_decision_authorized_amount_rejects_non_finite_decimal(bad_value):
    with pytest.raises(ValidationError):
        AuthorizationDecision(
            result=AuthorizationResult.ALLOW,
            authorized_amount=bad_value,
            binding_constraint="current_action_scope",
            cited_precedents=(),
            material_differences=(),
            explanation="test",
        )


def test_decimal_nan_raises_validation_error_not_invalid_operation():
    """Regression guard: comparing Decimal('NaN') with `<` raises
    decimal.InvalidOperation directly, not the ValidationError the
    'treat as absent' contract requires callers to catch. The finiteness
    check must run before any ordering comparison is attempted."""
    with pytest.raises(ValidationError):
        Proposal(**{**VALID_PROPOSAL_KWARGS, "amount": Decimal("NaN")})
