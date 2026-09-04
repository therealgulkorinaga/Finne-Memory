"""Learned-constraint derivation (LCP-001), per
docs/product/ACTIVE_DEMO_DESIGN.md section 4.

eligible = cases that are materially comparable
           AND authority_state == "active"
           AND outcome == "success"

learned_max_amount = max(authorized_amount of eligible)  if eligible is non-empty
                   = cold_start_autonomous_amount        if eligible is empty

Only `active` precedents enter `eligible`. `draft`, `questioned`,
`superseded`, and `withdrawn` cases are excluded from derivation while
remaining retrievable and displayable by the caller.

No I/O. Pure function of already-evaluated candidates.
"""

from __future__ import annotations

from finne.models import EvaluatedCandidate, LearnedConstraint, OwnerPolicy


def derive_learned_constraint(
    candidates: tuple[EvaluatedCandidate, ...], owner_policy: OwnerPolicy
) -> LearnedConstraint:
    eligible = [c for c in candidates if c.is_eligible()]

    if not eligible:
        return LearnedConstraint(
            learned_max_amount=owner_policy.cold_start_autonomous_amount,
            basis="cold_start",
        )

    max_amount = max(c.authorized_amount for c in eligible)
    supporting = tuple(
        c.decision_version_id for c in eligible if c.authorized_amount == max_amount
    )
    return LearnedConstraint(
        learned_max_amount=max_amount,
        basis="precedent",
        supporting_decision_version_ids=supporting,
    )
