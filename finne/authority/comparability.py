"""Deterministic comparability rule.

A prior case is materially comparable to a current proposal per
docs/product/ACTIVE_DEMO_DESIGN.md section 3. No model participates in
this determination — a model may only explain a difference this module
has already found, never invent or waive one.

No I/O. Pure function of two fact sets.
"""

from __future__ import annotations

from finne.models import Comparability, MaterialDifference, Proposal

_EXACT_MATCH_DIMENSIONS = ("network", "asset", "action_class", "target_class", "function")


def compare(proposal: Proposal, case_facts: Proposal) -> Comparability:
    """Compare `proposal` (the current action) against `case_facts` (a
    prior case's recorded facts).

    Comparable iff every exact-match dimension is identical AND the
    proposal's risk tier is not worse than the case's. Amount never
    affects comparability — it is the value being constrained, not a
    comparability dimension.
    """
    differences: list[MaterialDifference] = []

    for dimension in _EXACT_MATCH_DIMENSIONS:
        current_value = getattr(proposal, dimension)
        precedent_value = getattr(case_facts, dimension)
        if current_value != precedent_value:
            differences.append(
                MaterialDifference(
                    dimension=dimension,
                    precedent_value=precedent_value,
                    current_value=current_value,
                )
            )

    # Directional: a proposal riskier than its precedent cannot inherit
    # that precedent's authority. A precedent riskier than the current
    # proposal remains comparable (a successful high-risk case is at
    # least as strong grounds for a lower-risk one).
    if not proposal.counterparty_risk_tier.not_worse_than(case_facts.counterparty_risk_tier):
        differences.append(
            MaterialDifference(
                dimension="counterparty_risk_tier",
                precedent_value=case_facts.counterparty_risk_tier.value,
                current_value=proposal.counterparty_risk_tier.value,
            )
        )

    if differences:
        return Comparability(is_comparable=False, material_differences=tuple(differences))
    return Comparability(is_comparable=True)
