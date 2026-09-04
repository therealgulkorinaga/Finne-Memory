"""The deterministic authority engine.

The single place that computes effective authority and the final
allow/constrain/block/escalate result. Pure: no I/O, no clock, no
network, no imports from finne.memory or finne.base. This is what makes
the invariants provable by property test rather than by trust.

Owns, per DECISION-023 and SPEC-001 section 9: the owner ceiling,
effective action authority, permission intersection, amount limits,
approved scope, authority-state eligibility, and the final result. A
model may never influence any value this module computes.

effective_authority is the strict intersection of:
  1. owner_permission_ceiling  (OwnerPolicy.max_amount)
  2. current_hard_policy       (HardPolicy, clamped to never exceed the owner ceiling)
  3. active_precedent_constraints  (encoded via EvaluatedCandidate.is_eligible)
  4. learned_constraint        (finne.authority.derivation)
  5. current_action_scope      (the proposal itself; also gates scope entirely)

The exact control flow below may differ from a literal five-way min(), but
the invariant is absolute: authorized_amount can never exceed
owner_policy.max_amount, and the intersection can only narrow.
"""

from __future__ import annotations

from decimal import Decimal

from finne.authority.derivation import derive_learned_constraint
from finne.models import (
    AuthorizationDecision,
    AuthorizationResult,
    EvaluatedCandidate,
    HardPolicy,
    OwnerPolicy,
    Proposal,
)

_ZERO = Decimal("0")


def _in_approved_scope(proposal: Proposal, owner_policy: OwnerPolicy) -> bool:
    return (
        proposal.network == owner_policy.network
        and proposal.asset == owner_policy.asset
        and proposal.action_class == owner_policy.action_class
        and proposal.target_class in owner_policy.approved_target_classes
        and proposal.function in owner_policy.approved_functions
    )


def derive_effective_authority(
    proposal: Proposal,
    owner_policy: OwnerPolicy,
    hard_policy: HardPolicy,
    candidates: tuple[EvaluatedCandidate, ...],
) -> AuthorizationDecision:
    all_material_differences = tuple(
        diff
        for candidate in candidates
        for diff in candidate.comparability.material_differences
    )

    # A request above the owner ceiling is blocked outright, regardless of
    # precedent AND regardless of anything else wrong with the proposal —
    # invariant 1. Checked first, before the scope check, so an
    # out-of-scope-and-over-ceiling proposal is never let off with the
    # softer ESCALATE (owner-resolvable) path when the harder, absolute
    # BLOCK applies.
    if proposal.amount > owner_policy.max_amount:
        return AuthorizationDecision(
            result=AuthorizationResult.BLOCK,
            authorized_amount=_ZERO,
            binding_constraint="owner_permission_ceiling",
            cited_precedents=(),
            material_differences=all_material_differences,
            explanation=(
                f"Proposed amount {proposal.amount} exceeds the owner "
                f"permission ceiling {owner_policy.max_amount}. Blocked "
                f"regardless of any precedent or other scope issue."
            ),
        )

    # Out-of-scope proposals never reach the numeric intersection at all —
    # the owner's unknown_situation_behaviour governs, regardless of any
    # precedent. Currently the only defined behaviour is escalate.
    if not _in_approved_scope(proposal, owner_policy):
        return AuthorizationDecision(
            result=AuthorizationResult.ESCALATE,
            authorized_amount=_ZERO,
            binding_constraint="current_action_scope",
            cited_precedents=(),
            material_differences=all_material_differences,
            explanation=(
                f"Proposal falls outside owner-approved scope "
                f"(network={proposal.network!r}, asset={proposal.asset!r}, "
                f"action_class={proposal.action_class!r}, "
                f"target_class={proposal.target_class!r}, "
                f"function={proposal.function!r}). "
                f"Owner policy requires: {owner_policy.unknown_situation_behaviour}."
            ),
        )

    learned = derive_learned_constraint(candidates, owner_policy)

    # Hard policy can only narrow the owner ceiling, never widen it —
    # invariant 3. A malicious or malformed override above the owner
    # ceiling is clamped down, not honored.
    hard_ceiling = (
        hard_policy.max_amount_override
        if hard_policy.max_amount_override is not None
        else owner_policy.max_amount
    )
    hard_ceiling = min(hard_ceiling, owner_policy.max_amount)

    effective_ceiling = min(owner_policy.max_amount, hard_ceiling, learned.learned_max_amount)
    authorized_amount = min(proposal.amount, effective_ceiling)

    if authorized_amount == proposal.amount:
        # Full allow. Also correctly covers a zero-amount proposal, which
        # is trivially within any ceiling rather than a false escalation.
        return AuthorizationDecision(
            result=AuthorizationResult.ALLOW,
            authorized_amount=authorized_amount,
            binding_constraint="current_action_scope",
            cited_precedents=learned.supporting_decision_version_ids,
            material_differences=all_material_differences,
            explanation=(
                f"Proposed amount {proposal.amount} is within every "
                f"applicable constraint. Allowed in full."
            ),
        )

    # Something narrowed the proposal below its own amount. Identify which
    # of the three ceilings actually drove effective_ceiling down — used
    # for BOTH the escalate-at-zero and constrain-above-zero cases below,
    # so a hard-policy override that happens to zero out real, eligible
    # precedent is correctly attributed to current_hard_policy rather than
    # being misreported as "no precedent existed."
    if effective_ceiling == learned.learned_max_amount:
        binding = "learned_constraint"
    elif effective_ceiling == hard_ceiling:
        binding = "current_hard_policy"
    else:
        binding = "owner_permission_ceiling"

    if authorized_amount <= _ZERO:
        # Real demand (proposal.amount > 0) but no autonomous authority.
        # Never silently allow the full amount here.
        return AuthorizationDecision(
            result=AuthorizationResult.ESCALATE,
            authorized_amount=_ZERO,
            binding_constraint=binding,
            cited_precedents=learned.supporting_decision_version_ids,
            material_differences=all_material_differences,
            explanation=(
                f"No autonomous authority available for this proposal "
                f"(bound by {binding}). "
                + (
                    "No active, comparable, successful precedent supports it, "
                    "and the owner's cold-start autonomous amount is zero."
                    if binding == "learned_constraint"
                    else "A tighter current restriction reduced authority to zero "
                    "even though eligible precedent exists."
                )
                + " Escalating to the owner rather than silently authorizing "
                "the full amount."
            ),
        )

    return AuthorizationDecision(
        result=AuthorizationResult.CONSTRAIN,
        authorized_amount=authorized_amount,
        binding_constraint=binding,
        cited_precedents=learned.supporting_decision_version_ids,
        material_differences=all_material_differences,
        explanation=(
            f"Proposed amount {proposal.amount} constrained to "
            f"{authorized_amount}, bound by {binding} "
            f"(citing {', '.join(learned.supporting_decision_version_ids) or 'no precedent'})."
        ),
    )
