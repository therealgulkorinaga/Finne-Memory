"""NEG-01 through NEG-09 from docs/product/ACTIVE_DEMO_DESIGN.md section 8.

One of the nine test files PREREQ-003 section 14 specifies (eight
originally; `test_explain.py` was added with seam (e)). Every
negative case resolves to a NARROWER authority — constrain, block, or
escalate — and none widens. That is the property this file exists to
hold: not that failures are handled, but that no failure mode is a
path to more authority than the owner granted.

Covers: A9, A10, A12, invariant 7, and NEG-01 through NEG-07 plus
NEG-09.

NEG-08 and A13 (duplicate execution rejected at both the application
and contract level) are deliberately NOT here: they need the Base
adapter and the deployed contract, so they live in
tests/test_base_adapter.py, which owns both the mocked pre-flight
refusal and the opt-in live test proving the contract's own `require`
rejects a duplicate independently. Claiming them here would be the
kind of coverage overclaim earlier review rounds kept catching in the
governing documents.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from finne.authority.engine import derive_effective_authority
from finne.base.adapter import BaseExecutionResult
from finne.explain import deterministic_explanation, explain
from finne.memory.client import MemoryStore
from finne.memory.schema import AuthorityEventRecord, CaseVersionRecord, OutcomeRecord
from finne.models import (
    AuthorityState,
    AuthorizationResult,
    Comparability,
    EvaluatedCandidate,
    MaterialDifference,
    Outcome,
    OwnerPolicy,
    Proposal,
    RiskTier,
)
from finne.policy import default_hard_policy
from finne.retrieval import find_candidates

REPO_ROOT = Path(__file__).resolve().parent.parent

# A path whose parent is a FILE, not a directory: any attempt to open a
# database here fails at the OS level, which is the closest reproducible
# stand-in for "Sibyl Memory is unavailable" that needs no network and
# no mocking of the code under test.
UNUSABLE_DB_PATH = "/dev/null/unusable.db"

OWNER_POLICY = OwnerPolicy(
    max_amount=Decimal("25000.00"),
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    approved_target_classes=("yield_vault_conservative", "demo_receipt"),
    approved_functions=("deposit", "recordAuthorization"),
    unknown_situation_behaviour="escalate_to_owner",
    cold_start_autonomous_amount=Decimal("0.00"),
)

BASELINE_FACTS = Proposal(
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    target_class="yield_vault_conservative",
    function="deposit",
    counterparty_risk_tier=RiskTier.LOW,
    amount=Decimal("25000.00"),
    proposed_at="2026-09-02T00:00:00Z",
)


def _proposal(**overrides) -> Proposal:
    fields = {**BASELINE_FACTS.__dict__}
    fields.pop("schema_version", None)
    fields.update(overrides)
    return Proposal(**fields)


def _candidate(
    decision_version_id="DV-001-V1",
    amount="10000.00",
    state=AuthorityState.ACTIVE,
    outcome=Outcome.SUCCESS,
    comparable=True,
    differences=None,
) -> EvaluatedCandidate:
    if comparable:
        comparability = Comparability(is_comparable=True)
    else:
        comparability = Comparability(
            is_comparable=False,
            material_differences=differences
            or (
                MaterialDifference(
                    dimension="target_class",
                    precedent_value="yield_vault_aggressive",
                    current_value="yield_vault_conservative",
                ),
            ),
        )
    return EvaluatedCandidate(
        decision_version_id=decision_version_id,
        authorized_amount=Decimal(amount),
        authority_state=state,
        outcome=outcome,
        comparability=comparability,
    )


def _decide(proposal, candidates):
    return derive_effective_authority(proposal, OWNER_POLICY, default_hard_policy(), candidates)


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield MemoryStore.local(Path(tmpdir) / "negative_cases.db")


# --- NEG-01: memory absent or empty ---


def test_neg_01_empty_memory_escalates_never_allows(store):
    candidates = find_candidates(_proposal(), store)
    assert candidates == []
    decision = _decide(_proposal(), candidates)
    assert decision.result == AuthorizationResult.ESCALATE
    assert decision.authorized_amount == Decimal("0.00")


def test_neg_01_unreadable_memory_is_absence_not_permission(store, monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("memory unavailable")

    monkeypatch.setattr(store, "search_cases", boom)
    with pytest.raises(RuntimeError):
        find_candidates(_proposal(), store)
    # The failure propagates at the LIBRARY layer rather than silently
    # yielding "no constraints" — a caller cannot mistake a broken read
    # for an empty corpus, which is the only way an outage could widen
    # authority. The session scripts are what turn that propagated
    # failure into the visible escalation PREREQ-003 section 19
    # requires; the two tests below hold that end.


def _run_session(script: str, *extra_args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "FINNE_BASE_DRY_RUN": "1", "FINNE_PLAIN_OUTPUT": "1"}
    env.pop("ANTHROPIC_API_KEY", None)
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / script),
            "--db-path",
            UNUSABLE_DB_PATH,
            *extra_args,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


@pytest.mark.parametrize("script", ["session1.py", "session2.py"])
def test_neg_01_unavailable_memory_escalates_visibly_and_never_crashes(script):
    """PREREQ-003 section 19: memory unavailable resolves to `escalate`,
    "stated on screen as a memory failure, never as an allow".

    Found by independent review as a real gap: the exception propagated
    all the way out of the session script, so the required behaviour was
    a traceback on screen. A traceback is not an allow, but it is also
    not the specified fallback, and it is not legible as a safe outcome
    to anyone watching.

    The traceback is still PRODUCED, on stderr — round 2 of the same
    review pointed out that discarding it hides real failures from
    diagnosis. What changed is that it no longer displaces the outcome.
    """
    completed = _run_session(script)

    assert completed.returncode != 0
    # The screen shows the safe outcome, and only that.
    assert "RESULT: ESCALATE" in completed.stdout
    assert "MEMORY FAILURE" in completed.stdout
    assert "Traceback" not in completed.stdout, completed.stdout
    # The diagnostic detail survives, out of the way, for whoever has to
    # work out why memory was unreachable.
    assert "Traceback" in completed.stderr
    # An unread corpus must never be reported as an empty one.
    assert "Retrieved 0 candidate(s)" not in completed.stdout
    # Nothing may be presented as authorized.
    assert "authorized (citing" not in completed.stdout


# --- NEG-02: only a withdrawn case matches ---


def test_neg_02_withdrawn_precedent_never_authorizes():
    withdrawn = _candidate(decision_version_id="DV-003-V1", amount="20000.00", state=AuthorityState.WITHDRAWN)
    decision = _decide(_proposal(), [withdrawn])
    assert decision.result == AuthorizationResult.ESCALATE
    assert decision.authorized_amount == Decimal("0.00")
    assert decision.authorized_amount != Decimal("20000.00")


# --- NEG-03: materially different from every active case ---


def test_neg_03_material_difference_is_never_silently_followed():
    different = _candidate(decision_version_id="DV-005-V1", amount="10000.00", comparable=False)
    decision = _decide(_proposal(), [different])
    assert decision.result == AuthorizationResult.ESCALATE
    assert decision.authorized_amount == Decimal("0.00")


# --- NEG-04 / A9: above the owner ceiling ---


def test_neg_04_above_ceiling_is_blocked_regardless_of_precedent():
    generous = _candidate(amount="25000.00")
    decision = _decide(_proposal(amount=Decimal("40000.00")), [generous])
    assert decision.result == AuthorizationResult.BLOCK
    assert decision.authorized_amount == Decimal("0.00")


def test_neg_04_block_holds_even_with_many_supporting_precedents():
    supportive = [_candidate(decision_version_id=f"DV-{i:03d}-V1", amount="25000.00") for i in range(1, 6)]
    decision = _decide(_proposal(amount=Decimal("40000.00")), supportive)
    assert decision.result == AuthorizationResult.BLOCK


# --- NEG-05 / A10: no model API key ---


def test_neg_05_authorization_is_identical_with_and_without_a_model(monkeypatch):
    proposal = _proposal()
    candidates = [_candidate()]

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    without_key = _decide(proposal, candidates)

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    with_key = _decide(proposal, candidates)

    # The engine never reads the environment at all; this asserts the
    # observable consequence of that design.
    assert without_key == with_key


def test_neg_05_explanation_degrades_to_a_deterministic_template(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    decision = _decide(_proposal(), [_candidate()])
    assert explain(decision) == deterministic_explanation(decision)


# --- NEG-06: malformed or contradictory memory ---


def test_neg_06_case_with_no_outcome_is_absent_not_permission(store):
    """A case with an active authority state but no recorded outcome
    cannot be judged eligible, so it must not appear as a candidate at
    all — absence, never permission."""
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-NO-OUTCOME",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("20000.00"),
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-NO-OUTCOME",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="seed",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-NO-OUTCOME",
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner",
            reason="seed",
        )
    )
    candidates = find_candidates(_proposal(), store)
    assert [c.decision_version_id for c in candidates] == []
    assert _decide(_proposal(), candidates).result == AuthorizationResult.ESCALATE


def test_neg_06_case_with_no_authority_events_is_absent(store):
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-NO-EVENTS",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("20000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-NO-EVENTS", outcome=Outcome.SUCCESS, base_tx_hash=None)
    )
    assert find_candidates(_proposal(), store) == []


def test_neg_06_contradictory_chain_after_activation_is_absent_not_permission(store):
    """The gap independent review found: the fold previously kept the
    VALID PREFIX before a contradiction, so a chain that had already
    reached `active` stayed authorizing on evidence already known to be
    inconsistent. PREREQ-003 section 19 requires the most restrictive
    interpretation to win, and NEG-06 requires a contradictory record to
    be treated as absent, not as permission.
    """
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-CONTRADICTED",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("20000.00"),
        )
    )
    for previous, new in (
        (None, AuthorityState.DRAFT),
        (AuthorityState.DRAFT, AuthorityState.ACTIVE),
    ):
        store.append_authority_event(
            AuthorityEventRecord(
                decision_version_id="DV-CONTRADICTED",
                previous_status=previous,
                new_status=new,
                changed_by="owner",
                reason="genuine",
            )
        )
    # A later event whose claimed previous_status (draft) contradicts
    # what the chain actually accumulated (active) — a fork or a
    # duplicated history. Written through the raw journal because
    # AuthorityEventRecord itself is a legal (draft -> withdrawn) pair;
    # the contradiction is cross-event, not within this one record.
    store._client.write_event(
        extra={
            "kind": "finne_authority_event",
            "schema_version": 1,
            "decision_version_id": "DV-CONTRADICTED",
            "previous_status": "draft",
            "new_status": "withdrawn",
            "changed_by": "owner",
            "reason": "contradicts the accumulated chain",
        }
    )

    assert store.fold_authority_state("DV-CONTRADICTED") is None
    # Absent, therefore not assemblable as a candidate at all — the
    # 20000.00 it once claimed authorizes nothing.
    assert find_candidates(_proposal(), store) == []
    decision = _decide(_proposal(), find_candidates(_proposal(), store))
    assert decision.result == AuthorizationResult.ESCALATE
    assert decision.authorized_amount == Decimal("0.00")


def test_neg_06_illegal_transition_event_fails_the_whole_chain_closed(store, caplog):
    """The round-2 finding: an ILLEGAL transition never reached the
    fold's illegal-transition check at all. `AuthorityEventRecord`
    rejects `active -> draft` in __post_init__, and the deserialization
    loop caught that rejection with the same except-and-continue it uses
    for entries that are simply irrelevant — so the event vanished and a
    valid draft -> active chain folded to `active`, silently.

    A journal entry that claims to be an authority event for THIS
    decision and is not a valid one is evidence the history cannot be
    trusted. It is not absence.
    """
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-ILLEGAL",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("20000.00"),
        )
    )
    for previous, new_status in (
        (None, AuthorityState.DRAFT),
        (AuthorityState.DRAFT, AuthorityState.ACTIVE),
    ):
        store.append_authority_event(
            AuthorityEventRecord(
                decision_version_id="DV-ILLEGAL",
                previous_status=previous,
                new_status=new_status,
                changed_by="owner",
                reason="genuine",
            )
        )
    store._client.write_event(
        extra={
            "kind": "finne_authority_event",
            "schema_version": 1,
            "decision_version_id": "DV-ILLEGAL",
            "previous_status": "active",
            "new_status": "draft",
            "changed_by": "whoever",
            "reason": "not in the transition matrix",
        }
    )

    with caplog.at_level("WARNING"):
        assert store.fold_authority_state("DV-ILLEGAL") is None
    assert any("DV-ILLEGAL" in record.getMessage() for record in caplog.records)
    assert find_candidates(_proposal(), store) == []


def test_neg_06_an_invalid_event_for_another_decision_is_still_just_absent(store):
    """The other half of the same rule: fail-closed must be scoped to
    the decision whose history is actually corrupt. An invalid event for
    some other decision version is irrelevant, not evidence about this
    one — otherwise a single bad record anywhere would zero out the
    whole corpus."""
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-CLEAN",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="genuine",
        )
    )
    store._client.write_event(
        extra={
            "kind": "finne_authority_event",
            "schema_version": 1,
            "decision_version_id": "DV-SOMEONE-ELSE",
            "previous_status": "active",
            "new_status": "draft",
            "changed_by": "whoever",
            "reason": "corrupt, but not this decision's problem",
        }
    )
    assert store.fold_authority_state("DV-CLEAN") == AuthorityState.DRAFT


def test_neg_06_contradictory_chain_is_surfaced_not_silent(store, caplog):
    """PREREQ-003 section 19 requires the conflict to be SURFACED, not
    merely absorbed. Logged rather than raised: one corrupt chain must
    narrow that case to nothing without aborting retrieval of every
    other case beside it."""
    store._client.write_event(
        extra={
            "kind": "finne_authority_event",
            "schema_version": 1,
            "decision_version_id": "DV-ORPHANED",
            "previous_status": "draft",
            "new_status": "active",
            "changed_by": "owner",
            "reason": "claims a draft that never happened",
        }
    )
    with caplog.at_level("WARNING"):
        assert store.fold_authority_state("DV-ORPHANED") is None
    messages = [record.getMessage() for record in caplog.records]
    assert any("DV-ORPHANED" in message for message in messages), messages
    assert any("integrity" in message for message in messages), messages


def test_neg_06_failed_outcome_never_authorizes():
    failed = _candidate(decision_version_id="DV-007-V1", amount="12000.00", outcome=Outcome.FAILURE)
    assert _decide(_proposal(), [failed]).result == AuthorizationResult.ESCALATE


# --- NEG-07 / A12: Base revert or pre-broadcast rejection ---


def test_neg_07_confirmed_failure_carries_no_fabricated_reference():
    reverted = BaseExecutionResult(
        attempted=True, success=False, outcome_confirmed=True, tx_hash="0xreverted", detail="reverted"
    )
    assert reverted.success is False
    # A confirmed failure may cite the real reverted transaction, but a
    # SUCCESS may never exist without one.
    with pytest.raises(ValueError):
        BaseExecutionResult(
            attempted=True, success=True, outcome_confirmed=True, tx_hash=None, detail="fabricated"
        )


def test_neg_07_unattempted_result_can_never_claim_success():
    with pytest.raises(ValueError):
        BaseExecutionResult(
            attempted=False, success=True, outcome_confirmed=True, tx_hash=None, detail="impossible"
        )


# --- NEG-09: broadcast accepted, confirmation unknown ---


def test_neg_09_unknown_outcome_is_distinguishable_from_confirmed_failure():
    """The distinction NEG-09 exists for: an unresolved transaction is
    not a failed one. Outcome records are write-once, so conflating
    them would permanently misrepresent a case that may still succeed."""
    unknown = BaseExecutionResult(
        attempted=True, success=False, outcome_confirmed=False, tx_hash="0xpending", detail="timed out"
    )
    confirmed_failure = BaseExecutionResult(
        attempted=True, success=False, outcome_confirmed=True, tx_hash="0xreverted", detail="reverted"
    )
    assert unknown.outcome_confirmed != confirmed_failure.outcome_confirmed


def test_neg_09_unknown_outcome_must_carry_a_reconcilable_reference():
    with pytest.raises(ValueError):
        BaseExecutionResult(
            attempted=True, success=False, outcome_confirmed=False, tx_hash=None, detail="unreconcilable"
        )


def test_neg_01_classifier_separates_outages_from_defects_through_the_cause_chain():
    """What the session scripts consult before displaying a memory
    outage. A flat tuple of exception types could not do this job, in
    either direction: the memory client wraps a caller defect (SQL
    misuse) in its own StorageError, and a genuinely corrupt database
    file surfaces as a raw sqlite3.DatabaseError whose only admissible
    supertype is ProgrammingError's parent. Both reproduced by
    independent review."""
    import sqlite3

    from sibyl_memory_client import StorageError

    from finne.memory.client import is_memory_unavailable

    # A defect wrapped in an outage-shaped type is still a defect.
    try:
        try:
            raise sqlite3.ProgrammingError("parameter binding is wrong")
        except sqlite3.ProgrammingError as cause:
            raise StorageError("storage operation failed") from cause
    except StorageError as wrapped:
        assert not is_memory_unavailable(wrapped)

    # A corrupt database file is a genuine outage, not a defect.
    assert is_memory_unavailable(sqlite3.DatabaseError("file is not a database"))

    assert is_memory_unavailable(StorageError("disk unavailable"))
    assert is_memory_unavailable(OSError("no such file"))

    # An exception can carry BOTH a cause and a context: `raise X from
    # cause` inside an except block records the handled exception as
    # __context__ too. Following only __cause__ skipped the other
    # branch and classified this as an outage.
    try:
        try:
            raise TypeError("the real bug")
        except TypeError:
            try:
                raise OSError("disk gone")
            except OSError as cause:
                raise StorageError("storage failed") from cause
    except StorageError as both:
        assert not is_memory_unavailable(both)

    # Cycles terminate rather than hanging the session.
    first, second = ValueError("a"), ValueError("b")
    first.__cause__, second.__cause__ = second, first
    assert not is_memory_unavailable(first)
    for defect in (TypeError("bug"), AttributeError("bug"), sqlite3.IntegrityError("write-once")):
        assert not is_memory_unavailable(defect)


# --- presentation failure never becomes an authorization failure ---
#
# finne/cli.py is presentation only, so nothing here can change a
# decision. What it CAN do is abort a session script mid-run, after an
# authorization has already been persisted to Sibyl Memory and possibly
# settled on Base — leaving the process dead between two writes for a
# reason as trivial as a bracket in a string. These live in this file
# rather than a new one because that is the failure mode they belong to.


def test_rendering_never_parses_caller_text_as_markup():
    """`[/x]` in a fact value or an explanation previously raised
    rich.errors.MarkupError from inside a print call. Text is rendered
    literally now."""
    from finne import cli

    hostile = "precedent ['a'] vs [/closing] and [bold]not a style[/bold]"
    rendered = cli._text(hostile).plain
    assert rendered == hostile
    cli.note(hostile)  # must not raise


def test_rendering_strips_control_sequences_that_could_rewrite_the_screen():
    from finne import cli

    assert "\x1b" not in cli._text("\x1b[2J\x1b[H cleared").plain
    assert "\r" not in cli._text("done\r        undone").plain
    assert "\x7f" not in cli._text("done\x7f\x7f\x7fundone").plain
    # Newlines are content, not control: multi-line explanations survive.
    assert cli._text("line one\nline two").plain == "line one\nline two"


def test_rendering_escapes_combining_marks_without_conflating_values():
    """Combining marks can strike through or bury a glyph, so they must
    not render as themselves. They must not be silently DELETED either,
    and the text must not be normalised: independent review showed NFC
    made a decomposed and a precomposed decision-version id display
    identically — two distinct exact references shown as one, in a
    system whose whole claim is auditable citation."""
    import unicodedata

    from finne import cli

    struck = cli._text("1" + chr(0x338) + "0").plain
    assert chr(0x338) not in struck
    assert "U+0338" in struck

    decomposed = "DV-" + unicodedata.normalize("NFD", "é") + "-1"
    precomposed = "DV-" + unicodedata.normalize("NFC", "é") + "-1"
    assert decomposed != precomposed
    assert cli._text(decomposed).plain != cli._text(precomposed).plain


def test_output_failure_after_persistence_does_not_abort_the_session(monkeypatch, capsys):
    """A closed pipe or an unwritable terminal must not raise out of a
    presentation call. By the time most of them run, W1-W3 are already
    written and a Base transaction may already be settled."""
    from rich.console import Console

    from finne import cli

    def refuse(*_args, **_kwargs):
        raise OSError("terminal went away")

    monkeypatch.setattr(Console, "print", refuse)
    cli.note("still needs to be said")
    cli.warn("and this")
    cli.memory_failure("and this")
    # Fell back to the plainest possible write rather than raising.
    assert "still needs to be said" in capsys.readouterr().out


def _break_every_output(monkeypatch):
    import builtins

    from rich.console import Console

    def refuse(*_args, **_kwargs):
        raise OSError("no sink at all")

    monkeypatch.setattr(Console, "print", refuse)
    monkeypatch.setattr(builtins, "print", refuse)


def test_the_decision_frame_fails_closed_when_it_cannot_be_shown(monkeypatch):
    """Round-2 finding: best-effort output applied to the decision panel
    too, so a session could persist and submit an authorization while
    displaying nothing — exiting 0 having satisfied none of the
    acceptance criteria the demo exists to meet. The two frames whose
    purpose is to be seen now fail closed."""
    from finne import cli

    decision = _decide(_proposal(), [_candidate()])
    _break_every_output(monkeypatch)

    with pytest.raises(cli.PresentationError):
        cli.decision_panel(decision, _proposal(), "explanation")
    with pytest.raises(cli.PresentationError):
        cli.memory_failure("memory is gone")


def test_non_critical_output_still_degrades_quietly_when_nothing_can_be_written(monkeypatch):
    """The other side of the same rule: a note or a warning that cannot
    be written must still not abort a run that has already persisted an
    authorization."""
    from finne import cli

    _break_every_output(monkeypatch)
    cli.note("nowhere to put this")
    cli.warn("nor this")
    cli.candidates_table([])


# --- invariant 7: every failure narrows, none widens ---


@pytest.mark.parametrize(
    "candidates",
    [
        [],
        [_candidate(state=AuthorityState.WITHDRAWN)],
        [_candidate(state=AuthorityState.SUPERSEDED)],
        [_candidate(state=AuthorityState.QUESTIONED)],
        [_candidate(state=AuthorityState.DRAFT)],
        [_candidate(outcome=Outcome.FAILURE)],
        [_candidate(comparable=False)],
    ],
)
def test_invariant_7_no_failure_mode_authorizes_more_than_the_ceiling(candidates):
    decision = _decide(_proposal(), candidates)
    assert decision.authorized_amount <= OWNER_POLICY.max_amount
    assert decision.result in (AuthorizationResult.ESCALATE, AuthorizationResult.BLOCK)
    assert decision.authorized_amount == Decimal("0.00")
