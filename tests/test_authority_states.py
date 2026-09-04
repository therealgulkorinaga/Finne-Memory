"""Tests proving only `active` precedents support learned authority.

Maps to SPEC-001 section 12: A7 (a withdrawn precedent is displayed but
never raises authority), invariant 4 (a non-active precedent can never
raise authority).

Also reproduces the full CASE-001..CASE-008 corpus from
docs/product/ACTIVE_DEMO_DESIGN.md section 5 directly against the
authority engine, proving the documented "25,000 proposed -> 10,000
authorized" outcome holds at the engine level before retrieval or memory
exist (seams b/c).
"""

from __future__ import annotations

from decimal import Decimal

from finne.authority.comparability import compare
from finne.authority.derivation import derive_learned_constraint
from finne.authority.engine import derive_effective_authority
from finne.models import (
    AuthorityState,
    Comparability,
    EvaluatedCandidate,
    HardPolicy,
    Outcome,
    OwnerPolicy,
    Proposal,
    RiskTier,
)

OWNER_POLICY = OwnerPolicy(
    max_amount=Decimal("25000.00"),
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    approved_target_classes=("demo_receipt", "yield_vault_conservative"),
    approved_functions=("recordAuthorization", "deposit"),
    unknown_situation_behaviour="escalate_to_owner",
    cold_start_autonomous_amount=Decimal("0.00"),
)
NO_OVERRIDE = HardPolicy(max_amount_override=None)

BASELINE_FACTS = Proposal(
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    target_class="yield_vault_conservative",
    function="deposit",
    counterparty_risk_tier=RiskTier.LOW,
    amount=Decimal("0.00"),  # facts-only; amount irrelevant to comparability
    proposed_at="2026-09-03T00:00:00Z",
)


def candidate_against(proposal: Proposal, case_facts: Proposal, **kwargs) -> EvaluatedCandidate:
    return EvaluatedCandidate(
        comparability=compare(proposal, case_facts),
        **kwargs,
    )


def test_withdrawn_precedent_never_raises_authority():
    """A7: CASE-003 style — identical facts, withdrawn, authorized well
    above the active baseline. Must not raise the learned maximum."""
    proposal = Proposal(**{**BASELINE_FACTS.__dict__, "amount": Decimal("25000.00")})
    active_baseline = candidate_against(
        proposal,
        BASELINE_FACTS,
        decision_version_id="DV-001-V1",
        authorized_amount=Decimal("10000.00"),
        authority_state=AuthorityState.ACTIVE,
        outcome=Outcome.SUCCESS,
    )
    withdrawn_higher = candidate_against(
        proposal,
        BASELINE_FACTS,
        decision_version_id="DV-003-V1",
        authorized_amount=Decimal("20000.00"),
        authority_state=AuthorityState.WITHDRAWN,
        outcome=Outcome.SUCCESS,
    )
    learned = derive_learned_constraint((active_baseline, withdrawn_higher), OWNER_POLICY)
    assert learned.learned_max_amount == Decimal("10000.00")
    assert learned.supporting_decision_version_ids == ("DV-001-V1",)


def test_only_withdrawn_match_falls_back_to_cold_start():
    """NEG-02: only a withdrawn match exists. Result must escalate, never
    silently authorize the withdrawn case's amount."""
    proposal = Proposal(**{**BASELINE_FACTS.__dict__, "amount": Decimal("25000.00")})
    withdrawn_only = candidate_against(
        proposal,
        BASELINE_FACTS,
        decision_version_id="DV-003-V1",
        authorized_amount=Decimal("20000.00"),
        authority_state=AuthorityState.WITHDRAWN,
        outcome=Outcome.SUCCESS,
    )
    decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, (withdrawn_only,))
    assert decision.result.value == "escalate"
    assert decision.authorized_amount == Decimal("0")


def test_full_active_demo_corpus_yields_documented_outcome():
    """Reproduces docs/product/ACTIVE_DEMO_DESIGN.md CASE-001..CASE-008
    directly against the engine. Every non-CASE-001 fixture carries an
    authorized_amount deliberately above 10,000 so broken filtering fails
    loudly, per that document's own design note."""
    session2_proposal = Proposal(**{**BASELINE_FACTS.__dict__, "amount": Decimal("25000.00")})

    aggressive_target_facts = Proposal(
        **{**BASELINE_FACTS.__dict__, "target_class": "yield_vault_aggressive"}
    )
    demo_receipt_facts = Proposal(
        **{
            **BASELINE_FACTS.__dict__,
            "target_class": "demo_receipt",
            "function": "recordAuthorization",
        }
    )

    case_001 = candidate_against(
        session2_proposal,
        BASELINE_FACTS,
        decision_version_id="DV-001-V1",
        authorized_amount=Decimal("10000.00"),
        authority_state=AuthorityState.ACTIVE,
        outcome=Outcome.SUCCESS,
    )
    case_003_withdrawn = candidate_against(
        session2_proposal,
        BASELINE_FACTS,
        decision_version_id="DV-003-V1",
        authorized_amount=Decimal("20000.00"),
        authority_state=AuthorityState.WITHDRAWN,
        outcome=Outcome.SUCCESS,
    )
    case_004_less_similar = candidate_against(
        session2_proposal,
        demo_receipt_facts,
        decision_version_id="DV-004-V1",
        authorized_amount=Decimal("5000.00"),
        authority_state=AuthorityState.ACTIVE,
        outcome=Outcome.SUCCESS,
    )
    case_005_target_mismatch = candidate_against(
        session2_proposal,
        aggressive_target_facts,
        decision_version_id="DV-005-V1",
        authorized_amount=Decimal("10000.00"),
        authority_state=AuthorityState.ACTIVE,
        outcome=Outcome.SUCCESS,
    )
    case_006_superseded = candidate_against(
        session2_proposal,
        BASELINE_FACTS,
        decision_version_id="DV-006-V1",
        authorized_amount=Decimal("15000.00"),
        authority_state=AuthorityState.SUPERSEDED,
        outcome=Outcome.SUCCESS,
    )
    case_007_questioned_failure = candidate_against(
        session2_proposal,
        BASELINE_FACTS,
        decision_version_id="DV-007-V1",
        authorized_amount=Decimal("12000.00"),
        authority_state=AuthorityState.QUESTIONED,
        outcome=Outcome.FAILURE,
    )
    case_008_draft = candidate_against(
        session2_proposal,
        BASELINE_FACTS,
        decision_version_id="DV-008-V1",
        authorized_amount=Decimal("18000.00"),
        authority_state=AuthorityState.DRAFT,
        outcome=Outcome.SUCCESS,
    )

    candidates = (
        case_001,
        case_003_withdrawn,
        case_004_less_similar,
        case_005_target_mismatch,
        case_006_superseded,
        case_007_questioned_failure,
        case_008_draft,
    )

    decision = derive_effective_authority(session2_proposal, OWNER_POLICY, NO_OVERRIDE, candidates)

    assert decision.result.value == "constrain"
    assert decision.authorized_amount == Decimal("10000.00")
    assert decision.cited_precedents == ("DV-001-V1",)
    assert decision.binding_constraint == "learned_constraint"
    # CASE-005's exclusion must be reported as a material difference,
    # not silently dropped.
    assert any(
        d.dimension == "target_class" for d in decision.material_differences
    )
