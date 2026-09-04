"""Property-based tests proving the authority engine's invariants hold
under generated, including adversarial, input — not just the documented
demo scenarios.

Maps to SPEC-001 section 12: A9, invariants 1-3, 5.
"""

from __future__ import annotations

from decimal import Decimal

from hypothesis import given, strategies as st

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

amounts = st.decimals(
    min_value="0.00", max_value="100000.00", places=2, allow_nan=False, allow_infinity=False
)
authority_states = st.sampled_from(list(AuthorityState))
outcomes = st.sampled_from(list(Outcome))
other_networks = st.sampled_from(["ethereum", "polygon", "optimism", "arbitrum", "solana"])


def in_scope_proposal(amount: Decimal, risk: RiskTier = RiskTier.LOW) -> Proposal:
    return Proposal(
        network="base",
        asset="USDC",
        action_class="capital_deployment",
        target_class="yield_vault_conservative",
        function="deposit",
        counterparty_risk_tier=risk,
        amount=amount,
        proposed_at="2026-09-03T00:00:00Z",
    )


def comparable_candidate(
    decision_version_id: str,
    authorized_amount: Decimal,
    authority_state: AuthorityState,
    outcome: Outcome,
) -> EvaluatedCandidate:
    return EvaluatedCandidate(
        decision_version_id=decision_version_id,
        authorized_amount=authorized_amount,
        authority_state=authority_state,
        outcome=outcome,
        comparability=Comparability(is_comparable=True),
    )


@st.composite
def candidate_lists(draw, min_size=0, max_size=6):
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    candidates = []
    for i in range(n):
        amount = draw(amounts)
        state = draw(authority_states)
        outcome = draw(outcomes)
        candidates.append(comparable_candidate(f"DV-TEST-{i:03d}", amount, state, outcome))
    return tuple(candidates)


# --- Invariant 1: authorized_amount never exceeds the owner ceiling,
# including under generated candidate sets whose authorized_amount may
# itself exceed the current ceiling (e.g. an owner ceiling lowered after
# an earlier precedent was set higher). ---


@given(
    proposal_amount=amounts,
    override=st.one_of(st.none(), amounts),
    candidates=candidate_lists(),
)
def test_authorized_amount_never_exceeds_owner_ceiling(proposal_amount, override, candidates):
    proposal = in_scope_proposal(proposal_amount)
    hard_policy = HardPolicy(max_amount_override=override)
    decision = derive_effective_authority(proposal, OWNER_POLICY, hard_policy, candidates)
    assert decision.authorized_amount <= OWNER_POLICY.max_amount


# --- A9: a request above the owner ceiling is blocked, regardless of
# any precedent, however favorable. ---


@given(
    proposal_amount=st.decimals(
        min_value="25000.01",
        max_value="100000.00",
        places=2,
        allow_nan=False,
        allow_infinity=False,
    ),
    candidates=candidate_lists(),
)
def test_above_ceiling_is_always_blocked(proposal_amount, candidates):
    proposal = in_scope_proposal(proposal_amount)
    decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, candidates)
    assert decision.result.value == "block"
    assert decision.authorized_amount == Decimal("0")


# --- Invariant 2: the engine never authorizes a network absent from the
# owner ceiling, regardless of the proposed amount. ---


in_ceiling_amounts = st.decimals(
    min_value="0.00", max_value="25000.00", places=2, allow_nan=False, allow_infinity=False
)


@given(network=other_networks, proposal_amount=in_ceiling_amounts)
def test_out_of_scope_network_is_never_authorized(network, proposal_amount):
    """Isolates the scope violation: amount stays within the owner
    ceiling, so the only problem is scope. See
    test_out_of_scope_and_over_ceiling_blocks_not_escalates for what
    happens when both are wrong at once."""
    proposal = Proposal(
        network=network,
        asset="USDC",
        action_class="capital_deployment",
        target_class="yield_vault_conservative",
        function="deposit",
        counterparty_risk_tier=RiskTier.LOW,
        amount=proposal_amount,
        proposed_at="2026-09-03T00:00:00Z",
    )
    decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, ())
    assert decision.authorized_amount == Decimal("0")
    assert decision.result.value == "escalate"


@given(
    network=other_networks,
    proposal_amount=st.decimals(
        min_value="25000.01",
        max_value="100000.00",
        places=2,
        allow_nan=False,
        allow_infinity=False,
    ),
)
def test_out_of_scope_and_over_ceiling_blocks_not_escalates(network, proposal_amount):
    """A proposal that is BOTH out of scope AND above the owner ceiling
    must BLOCK, not ESCALATE — the amount-ceiling check is an absolute
    violation and takes priority over the softer, owner-resolvable scope
    escalation. Found by Codex review: the engine previously checked
    scope first, which let an over-ceiling amount slip through as
    ESCALATE whenever the proposal was also out of scope."""
    proposal = Proposal(
        network=network,
        asset="USDC",
        action_class="capital_deployment",
        target_class="yield_vault_conservative",
        function="deposit",
        counterparty_risk_tier=RiskTier.LOW,
        amount=proposal_amount,
        proposed_at="2026-09-03T00:00:00Z",
    )
    decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, ())
    assert decision.result.value == "block"
    assert decision.authorized_amount == Decimal("0")


# --- Invariant 3: a hard-policy override — including one deliberately
# set above the owner ceiling — can only narrow effective authority,
# never widen it past the owner ceiling or past the proposal itself. ---


@given(
    proposal_amount=amounts,
    override=st.decimals(
        min_value="0.00", max_value="200000.00", places=2, allow_nan=False, allow_infinity=False
    ),
    candidates=candidate_lists(),
)
def test_hard_policy_override_cannot_exceed_owner_ceiling(proposal_amount, override, candidates):
    proposal = in_scope_proposal(proposal_amount)
    hard_policy = HardPolicy(max_amount_override=override)
    decision = derive_effective_authority(proposal, OWNER_POLICY, hard_policy, candidates)
    assert decision.authorized_amount <= OWNER_POLICY.max_amount
    assert decision.authorized_amount <= proposal_amount


# --- Invariant 5: a retrieval miss (fewer candidates than actually
# exist) can only narrow authority, never widen it. ---


@given(candidates=candidate_lists(min_size=1, max_size=6))
def test_fewer_candidates_never_widen_authority(candidates):
    proposal = in_scope_proposal(Decimal("25000.00"))
    full_decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, candidates)

    reduced = candidates[:-1]  # simulate a retrieval miss
    reduced_decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, reduced)

    assert reduced_decision.authorized_amount <= full_decision.authorized_amount


@given(candidates=candidate_lists())
def test_empty_candidates_falls_back_to_cold_start(candidates):
    proposal = in_scope_proposal(Decimal("25000.00"))
    empty_decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, ())
    assert empty_decision.authorized_amount <= OWNER_POLICY.cold_start_autonomous_amount


# --- Attribution correctness: escalation must blame whichever ceiling
# actually caused it, not always the learned constraint. Found by Codex
# review: a real, eligible precedent existed but a hard-policy override
# separately zeroed authority; the engine previously always reported
# "learned_constraint" as the reason, misattributing the cause. ---


def test_zero_ceiling_from_hard_policy_blames_hard_policy_not_precedent():
    proposal = in_scope_proposal(Decimal("25000.00"))
    real_precedent = comparable_candidate(
        "DV-001-V1",
        Decimal("10000.00"),
        AuthorityState.ACTIVE,
        Outcome.SUCCESS,
    )
    hard_policy_zero = HardPolicy(max_amount_override=Decimal("0.00"))

    decision = derive_effective_authority(
        proposal, OWNER_POLICY, hard_policy_zero, (real_precedent,)
    )

    assert decision.result.value == "escalate"
    assert decision.authorized_amount == Decimal("0")
    assert decision.binding_constraint == "current_hard_policy"
    # The eligible precedent is still surfaced for context, even though it
    # was not what bound the final result.
    assert decision.cited_precedents == ("DV-001-V1",)


def test_zero_ceiling_from_true_cold_start_blames_learned_constraint():
    """The original cold-start case, kept as a contrast to the test above:
    when no eligible precedent exists at all, the attribution is
    genuinely learned_constraint."""
    proposal = in_scope_proposal(Decimal("25000.00"))
    decision = derive_effective_authority(proposal, OWNER_POLICY, NO_OVERRIDE, ())
    assert decision.result.value == "escalate"
    assert decision.binding_constraint == "learned_constraint"
    assert decision.cited_precedents == ()
