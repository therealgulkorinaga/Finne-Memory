"""Tests for the deterministic comparability rule.

Maps to SPEC-001 section 12: A8 (a materially different proposal against
an otherwise comparable precedent is not silently followed).
"""

from __future__ import annotations

from decimal import Decimal

from finne.authority.comparability import compare
from finne.models import Proposal, RiskTier

BASE_FACTS = dict(
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    target_class="yield_vault_conservative",
    function="deposit",
    counterparty_risk_tier=RiskTier.LOW,
    proposed_at="2026-09-03T00:00:00Z",
)


def make_proposal(amount: str = "25000.00", **overrides) -> Proposal:
    fields = {**BASE_FACTS, **overrides, "amount": Decimal(amount)}
    return Proposal(**fields)


def test_identical_facts_are_comparable():
    proposal = make_proposal()
    case = make_proposal(amount="10000.00")  # amount never affects comparability
    result = compare(proposal, case)
    assert result.is_comparable is True
    assert result.material_differences == ()


def test_target_class_mismatch_excludes_case005_style():
    """The exact CASE-005 fixture: identical to the baseline except
    target_class. Must be excluded — this is the scenario the corpus
    was redesigned around after the risk-tier direction was found
    self-contradictory during SPEC-001 review."""
    proposal = make_proposal()
    case = make_proposal(target_class="yield_vault_aggressive")
    result = compare(proposal, case)
    assert result.is_comparable is False
    assert any(d.dimension == "target_class" for d in result.material_differences)


def test_network_mismatch_excludes():
    proposal = make_proposal()
    case = make_proposal(network="ethereum")
    result = compare(proposal, case)
    assert result.is_comparable is False
    assert any(d.dimension == "network" for d in result.material_differences)


def test_function_mismatch_excludes():
    proposal = make_proposal()
    case = make_proposal(function="recordAuthorization")
    result = compare(proposal, case)
    assert result.is_comparable is False
    assert any(d.dimension == "function" for d in result.material_differences)


def test_riskier_current_proposal_excludes_safer_precedent():
    """A high-risk current proposal cannot inherit a low-risk precedent's
    authority — the directional exclusion invariant."""
    proposal = make_proposal(counterparty_risk_tier=RiskTier.HIGH)
    case = make_proposal(counterparty_risk_tier=RiskTier.LOW)
    result = compare(proposal, case)
    assert result.is_comparable is False
    assert any(d.dimension == "counterparty_risk_tier" for d in result.material_differences)


def test_safer_current_proposal_remains_comparable_to_riskier_precedent():
    """The other direction: a low-risk current proposal IS comparable to
    a high-risk precedent — a successful high-risk case is at least as
    strong grounds for a lower-risk one. This is the exact direction that
    was previously self-contradictory in the corpus fixture and was
    corrected during SPEC-001 review."""
    proposal = make_proposal(counterparty_risk_tier=RiskTier.LOW)
    case = make_proposal(counterparty_risk_tier=RiskTier.HIGH)
    result = compare(proposal, case)
    assert result.is_comparable is True
    assert result.material_differences == ()


def test_equal_risk_tier_is_comparable():
    proposal = make_proposal(counterparty_risk_tier=RiskTier.MEDIUM)
    case = make_proposal(counterparty_risk_tier=RiskTier.MEDIUM)
    result = compare(proposal, case)
    assert result.is_comparable is True


def test_multiple_material_differences_all_reported():
    proposal = make_proposal(network="ethereum", function="recordAuthorization")
    case = make_proposal()
    result = compare(proposal, case)
    assert result.is_comparable is False
    dims = {d.dimension for d in result.material_differences}
    assert dims == {"network", "function"}
