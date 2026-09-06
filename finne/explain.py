"""Readable explanation of an AuthorizationDecision.

Deterministic, and only deterministic: no model call, no network, no
environment reads, no I/O of any kind. `explain()` is the module's
public entry point and returns exactly `deterministic_explanation()`.

PREREQ-003 section 17 still designates this module as the ONLY one
permitted to call a model, and tests/test_import_boundaries.py still
enforces that no other module imports an AI SDK. This module no longer
exercises that permission, and the reason belongs here because the code
alone cannot show it.

Four rounds of independent review found four different ways for
model-influenced text to state something false beside a correct
decision:

  1. An allowlist of numbers appearing in the decision admitted "the
     agent was authorized 25,000.00" — a true number saying a false
     thing, because the PROPOSED amount is in the decision too.
  2. A ban on digits and scale words admitted "one zero zero zero
     zero", "ten grand", "twice the safe limit", and — needing no
     quantity at all — "the proposal was permitted in full".
  3. Selecting among pre-written sentences keyed on (result, cited)
     offered "it held itself to a limit an earlier decision
     established" for a constraint bound by current hard policy.
  4. Adding `binding_constraint` to the key still left a reachable tie:
     when the learned ceiling and the hard ceiling are equal the engine
     labels it `learned_constraint`, and "rather than from a standing
     restriction" is false there.

Each fix was sound against the previous round and wrong in a way the
next round found. The value at stake was one sentence of prose beside
an explanation that already states every fact; the demo and the whole
test suite run with no API key present regardless. Removing the
mechanism removes the entire class of failure, and is what independent
review recommended after round 4 rather than a fifth repair.

If a model is ever reinstated here, the property to hold is not "the
output passes validation" — three attempts at that failed. It is that
no model output can be displayed at all unless something deterministic
proves it true of THIS decision.
"""

from __future__ import annotations

from finne.models import AuthorizationDecision, AuthorizationResult

_RESULT_HEADLINES = {
    AuthorizationResult.ALLOW: "ALLOWED as proposed",
    AuthorizationResult.CONSTRAIN: "CONSTRAINED below the proposed amount",
    AuthorizationResult.BLOCK: "BLOCKED outright",
    AuthorizationResult.ESCALATE: "ESCALATED to the owner",
}


def deterministic_explanation(decision: AuthorizationDecision) -> str:
    """The authoritative explanation. Pure: no I/O, no model, no
    environment reads. Every number in it comes straight from the
    decision the engine already produced."""
    lines = [
        f"Result: {decision.result.value.upper()} — {_RESULT_HEADLINES[decision.result]}.",
        f"Authorized amount: {decision.authorized_amount}",
        f"Bound by: {decision.binding_constraint}",
    ]
    if decision.cited_precedents:
        lines.append(f"Citing precedent: {', '.join(decision.cited_precedents)}")
    else:
        lines.append("Citing precedent: none — no eligible precedent supported this proposal")
    if decision.material_differences:
        # AuthorizationDecision.material_differences aggregates across
        # every NON-comparable candidate the engine saw, so these
        # describe why OTHER cases were excluded — they are never
        # differences in the cited precedent, which by definition had
        # none. Labelling this explicitly matters: unlabelled, these
        # lines render directly beneath "Citing precedent: DV-001-V1"
        # and read as if the cited precedent itself were mismatched,
        # on the single frame the demo exists to show.
        lines.append("Excluded by material difference (these are other candidates, not the cited one):")
        for difference in decision.material_differences:
            lines.append(
                f"  - {difference.dimension}: "
                f"precedent {difference.precedent_value!r} vs current {difference.current_value!r}"
            )
    lines.append(decision.explanation)
    return "\n".join(lines)


def explain(decision: AuthorizationDecision) -> str:
    """The explanation shown to a viewer.

    Identical to `deterministic_explanation()`, and kept as a separate
    public name because it is what the session scripts and SPEC-001
    section 7 call, and because the distinction it once drew — between
    the authoritative text and an optional model-written addition — is
    the thing this module deliberately no longer has. A10 and NEG-05
    ("results are identical with no model API key present") are now
    true by construction rather than by validation: there is no key to
    have, and nothing reads one.
    """
    return deterministic_explanation(decision)
