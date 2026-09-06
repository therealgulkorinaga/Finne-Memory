"""Tests for finne/explain.py — the only module PERMITTED to call a
model, which after four rounds of independent review no longer does.

The property that matters is negative and is now structural rather than
behavioural: the authorization is unchanged by any model because no
model participates, and `explain()` is exactly
`deterministic_explanation()`. A10 and NEG-05 ("results are identical
with no model API key present") hold by construction — there is no key
to have and nothing that reads one.

The whole suite runs with no ANTHROPIC_API_KEY present, per PREREQ-003
section 13.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import finne.explain as explain_module
from finne.explain import deterministic_explanation, explain
from finne.models import (
    AuthorizationDecision,
    AuthorizationResult,
    MaterialDifference,
)


def _decision(
    result=AuthorizationResult.CONSTRAIN,
    amount="10000.00",
    cited=("DV-001-V1",),
    differences=(),
    explanation="Proposed amount 25000.00 constrained to 10000.00, bound by learned_constraint.",
    binding_constraint="learned_constraint",
):
    return AuthorizationDecision(
        result=result,
        authorized_amount=Decimal(amount),
        binding_constraint=binding_constraint,
        cited_precedents=cited,
        material_differences=differences,
        explanation=explanation,
    )


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch):
    # Explicit, not incidental: every test below starts from the
    # no-model state PREREQ-003 requires the demo to run in.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# --- the deterministic path ---


def test_deterministic_explanation_is_pure_and_repeatable():
    decision = _decision()
    assert deterministic_explanation(decision) == deterministic_explanation(decision)


def test_deterministic_explanation_states_result_amount_and_citation():
    text = deterministic_explanation(_decision())
    assert "RESULT: CONSTRAIN" in text.upper()
    assert "10000.00" in text
    assert "DV-001-V1" in text


def test_deterministic_explanation_names_absence_of_precedent_explicitly():
    text = deterministic_explanation(_decision(result=AuthorizationResult.ESCALATE, amount="0", cited=()))
    assert "none" in text.lower()


def test_deterministic_explanation_states_material_differences():
    difference = MaterialDifference(
        dimension="target_class",
        precedent_value="yield_vault_aggressive",
        current_value="yield_vault_conservative",
    )
    text = deterministic_explanation(_decision(differences=(difference,)))
    assert "target_class" in text
    assert "yield_vault_aggressive" in text


def test_material_differences_are_labelled_as_other_candidates():
    """The fix for a real legibility bug found by running the demo, not
    by inspection: `material_differences` aggregates across every
    non-comparable candidate, so on a CONSTRAIN they describe why OTHER
    cases were excluded. Rendered unlabelled they sit directly beneath
    "Citing precedent: DV-001-V1" and read as if the CITED precedent
    were mismatched — on the one frame the demo exists to show.

    Independent review noted the assertion above checks the values but
    not the label that disambiguates them, so the regression this
    guards against could return silently."""
    difference = MaterialDifference(
        dimension="target_class",
        precedent_value="yield_vault_aggressive",
        current_value="yield_vault_conservative",
    )
    text = deterministic_explanation(_decision(cited=("DV-001-V1",), differences=(difference,)))
    label_line = next(line for line in text.splitlines() if "material difference" in line.lower())
    assert "other candidates" in label_line.lower()
    assert "not the cited one" in label_line.lower()
    # The label must precede the differences it labels.
    assert text.index(label_line) < text.index("target_class")


def test_every_result_kind_renders():
    for result, amount in [
        (AuthorizationResult.ALLOW, "25000.00"),
        (AuthorizationResult.CONSTRAIN, "10000.00"),
        (AuthorizationResult.BLOCK, "0"),
        (AuthorizationResult.ESCALATE, "0"),
    ]:
        text = deterministic_explanation(_decision(result=result, amount=amount))
        assert result.value.upper() in text.upper()


# --- model-optional behaviour (A10, NEG-05) ---


def test_explain_without_api_key_is_exactly_the_deterministic_explanation():
    decision = _decision()
    assert explain(decision) == deterministic_explanation(decision)


def test_explain_never_constructs_a_model_client(monkeypatch):
    """Installs a fake `anthropic` module that explodes if any part of
    it is touched, then runs the real code path — with an API key
    present, which is the stronger case now that nothing reads one. If
    explain() reached an SDK at all, this would raise."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    import sys
    import types

    exploding = types.ModuleType("anthropic")

    def _explode(*_args, **_kwargs):
        raise AssertionError("no model client may be constructed without an API key")

    exploding.Anthropic = _explode
    monkeypatch.setitem(sys.modules, "anthropic", exploding)

    decision = _decision()
    assert explain(decision) == deterministic_explanation(decision)


# --- no model path exists (A10, NEG-05 by construction) ---
#
# There is nothing here to validate any more, and that is the point.
# Four review rounds found four different ways for model-influenced text
# to state something false beside a correct decision: a numbers
# allowlist admitted the proposed amount as the authorized one; a
# digits-and-scale-words ban admitted "ten grand" and "permitted in
# full"; selection keyed on (result, cited) mis-attributed a
# hard-policy constraint to a precedent; and adding binding_constraint
# still left a tie, where the learned and hard ceilings are equal and
# the engine labels it learned_constraint. Round 4 recommended deleting
# the mechanism rather than repairing it a fourth time. See
# finne/explain.py's module docstring for the full record.


def test_explain_is_exactly_the_deterministic_explanation():
    for result, amount in [
        (AuthorizationResult.ALLOW, "25000.00"),
        (AuthorizationResult.CONSTRAIN, "10000.00"),
        (AuthorizationResult.BLOCK, "0"),
        (AuthorizationResult.ESCALATE, "0"),
    ]:
        decision = _decision(result=result, amount=amount)
        assert explain(decision) == deterministic_explanation(decision)


def test_explain_ignores_the_environment_entirely(monkeypatch):
    """A10/NEG-05 restated for a module that no longer reads a key:
    setting one changes nothing, because nothing looks."""
    decision = _decision()
    without = explain(decision)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    assert explain(decision) == without


def test_no_model_sdk_is_reachable_from_this_module():
    """Structural, not behavioural: the module must not import an AI SDK
    at all, at import time or lazily inside a function.

    tests/test_import_boundaries.py enforces the architecture's rule
    (only finne/explain.py MAY import one). This asserts the stronger
    fact that is now true: it does not."""
    import ast
    import pathlib

    source = pathlib.Path(explain_module.__file__).read_text()
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not imported & {"anthropic", "openai", "os", "urllib", "requests", "httpx"}, imported


def test_the_module_does_not_read_or_write_anything():
    """Purity, asserted the only way that survives refactoring: the
    module's entire import set is checked, not just the ones a reviewer
    thought to look for."""
    import ast
    import pathlib

    source = pathlib.Path(explain_module.__file__).read_text()
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "finne"}, imported
