"""Proves the fresh-session claim by running the demo scripts as real,
separate OS subprocesses against a real temporary Sibyl Memory database
— not by importing session1.run()/session2.run() into this test
process. Importing would prove nothing about A3 (no carried-over
in-process state); a Python import shares interpreter state (module
caches, open handles) that a genuinely fresh process cannot have.

Per PREREQ-003 section 3's W4 row ("after the Base transaction
settles"), an outcome is never recorded until finne.base.adapter
reports attempted=True. While that adapter remains seam (d)'s stub
(attempted always False), DV-001-V1 genuinely has no recorded outcome
after session1.py runs, so it is not yet eligible as precedent
(finne.authority.derivation requires outcome == SUCCESS) and session2.py
honestly escalates too — this is NEG-07 working as designed, not a
gap in this test. What IS fully testable today, without seam (d):
that the authorization itself (W1-W3) persists correctly and that no
outcome is fabricated; and, by seeding a precedent's outcome directly
through MemoryStore exactly as reset_demo.py already does for its own
CASE-003..008 fixtures (a synthetic-but-honest stand-in for "seam (d)
already recorded a real success here"), that session2.py's own
constrain/cite logic is correct and ready. PrecedentRelationship
persistence (ACTIVE_DEMO_DESIGN.md section 6/7) is deferred from this
seam — see finne/memory/schema.py's module-level note — so it is not
tested here.

Covers: A1, A3, A6, A14, invariant 6, and (via the seeded-outcome test)
the session2.py logic underlying A4/A5, which cannot be exercised live
by session1.py -> session2.py alone until seam (d) exists.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from finne.demo_config import (
    DEMO_ACTION_CLASS,
    DEMO_ASSET,
    DEMO_FUNCTION,
    DEMO_NETWORK,
    DEMO_TARGET_CLASS,
    DEMO_TENANT_ID,
)
from finne.memory.client import MemoryStore
from finne.memory.schema import (
    AuthorityEventRecord,
    CaseVersionRecord,
    OutcomeRecord,
    OwnerPolicySnapshot,
)
from finne.models import AuthorityState, Outcome, Proposal, RiskTier

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_script(script: str, db_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script), "--db-path", str(db_path), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "fresh_session_test.db"


def reset(db_path: Path) -> subprocess.CompletedProcess:
    result = run_script("reset_demo.py", db_path)
    assert result.returncode == 0, result.stderr
    return result


def test_reset_seeds_known_state_and_leaves_case_001_unseeded(db_path):
    # A14: the demo resets to a known, asserted state before each run —
    # this is the setup phase SPEC-001 section 12 requires test_fresh_session.py
    # to perform, not a side effect of some other test. Reading the seeded
    # state back through MemoryStore (rather than parsing reset_demo.py's
    # summary line) is what actually proves the state landed correctly.
    reset(db_path)
    store = MemoryStore.local(db_path, tenant_id=DEMO_TENANT_ID)
    expected_states = {
        "DV-003-V1": AuthorityState.WITHDRAWN,
        "DV-004-V1": AuthorityState.ACTIVE,
        "DV-005-V1": AuthorityState.ACTIVE,
        "DV-006-V1": AuthorityState.SUPERSEDED,
        "DV-007-V1": AuthorityState.QUESTIONED,
        "DV-008-V1": AuthorityState.DRAFT,
    }
    for decision_version_id, expected_state in expected_states.items():
        assert store.fold_authority_state(decision_version_id) == expected_state
        assert store.read_case_version(decision_version_id) is not None

    assert store.fold_authority_state("DV-001-V1") is None
    assert store.read_case_version("DV-001-V1") is None


def test_session1_escalates_and_persists_authorization_without_a_premature_outcome(db_path):
    # A1: no comparable active precedent exists yet, so Session 1 must
    # escalate rather than silently authorizing the full 25,000 proposal.
    # BLOCKER (Codex, seam c round 1): the owner's 10,000 approval must
    # persist (W1-W3) without waiting on Base, but no outcome (W4) may be
    # recorded until a real Base attempt exists — verified by reading the
    # store directly, not just parsing stdout.
    reset(db_path)
    result = run_script("session1.py", db_path)
    assert result.returncode == 0, result.stderr
    assert "escalate" in result.stdout
    assert "Owner approves constrained authority: 10000.00" in result.stdout
    assert "No outcome recorded" in result.stdout
    assert "Process exiting completely" in result.stdout

    store = MemoryStore.local(db_path, tenant_id=DEMO_TENANT_ID)
    case = store.read_case_version("DV-001-V1")
    assert case is not None
    assert case.authorized_amount == Decimal("10000.00")
    assert store.read_owner_policy_snapshot("DV-001-V1") is not None
    assert store.fold_authority_state("DV-001-V1") == AuthorityState.ACTIVE
    assert store.read_outcome("DV-001-V1") is None


def test_session2_honestly_escalates_when_precedent_has_no_recorded_outcome(db_path):
    # A3: session1.py and session2.py are launched as two independent
    # subprocess.run() calls — the second has no access to any Python
    # object, module cache, or variable the first created; the only
    # channel between them is the on-disk Sibyl Memory database.
    #
    # With no seam (d), DV-001-V1 has an active authority state but no
    # recorded outcome, so it is correctly not retrieved as a candidate
    # (finne.retrieval requires an outcome record) and Session 2
    # honestly escalates too, rather than fabricating a constrain result
    # off an unproven precedent.
    reset(db_path)
    first = run_script("session1.py", db_path)
    assert first.returncode == 0, first.stderr

    second = run_script("session2.py", db_path)
    assert second.returncode == 0, second.stderr
    assert "DV-001-V1" not in second.stdout
    assert "escalate" in second.stdout
    assert "Nothing authorized" in second.stdout

    store = MemoryStore.local(db_path, tenant_id=DEMO_TENANT_ID)
    assert store.read_case_version("DV-002-V1") is None


def _seed_dv_001_v1_with_outcome(store: MemoryStore) -> None:
    """Seeds DV-001-V1 exactly as session1.py does (case, owner-policy
    snapshot, draft -> active authority events), PLUS a SUCCESS outcome
    — a synthetic-but-honest stand-in for "seam (d) already recorded a
    real Base success here." This isolates and proves session2.py's own
    constrain/cite logic without requiring seam (d) to exist.

    Uses a clearly-synthetic, non-empty tx_hash rather than None:
    real seam (d) success always carries a real transaction reference
    (BaseExecutionResult.__post_init__ now enforces this), so a SUCCESS
    outcome with base_tx_hash=None is a shape only reset_demo.py's
    pre-existing historical fixtures should use, never a stand-in for a
    live seam-(d) result (Codex, seam c round 2, NICE-TO-HAVE)."""
    facts = Proposal(
        network=DEMO_NETWORK,
        asset=DEMO_ASSET,
        action_class=DEMO_ACTION_CLASS,
        target_class=DEMO_TARGET_CLASS,
        function=DEMO_FUNCTION,
        counterparty_risk_tier=RiskTier.LOW,
        amount=Decimal("25000.00"),
        proposed_at="2026-09-01T00:00:00Z",
    )
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-001-V1", facts=facts, authorized_amount=Decimal("10000.00")
        )
    )
    store.write_owner_policy_snapshot(
        "DV-001-V1",
        OwnerPolicySnapshot(
            max_amount=Decimal("25000.00"),
            network=DEMO_NETWORK,
            asset=DEMO_ASSET,
            action_class=DEMO_ACTION_CLASS,
            approved_target_classes=(DEMO_TARGET_CLASS, "demo_receipt"),
            approved_functions=(DEMO_FUNCTION, "recordAuthorization"),
            cold_start_autonomous_amount=Decimal("0.00"),
        ),
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-001-V1",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner_as_decision_reviewer",
            reason="seed: confirmation creates the draft",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-001-V1",
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner_as_authority_steward",
            reason="seed: activation",
        )
    )
    store.write_outcome(
        OutcomeRecord(
            decision_version_id="DV-001-V1",
            outcome=Outcome.SUCCESS,
            base_tx_hash="synthetic-test-fixture-not-a-real-tx",
        )
    )


def test_session2_constrains_and_cites_precedent_once_precedent_has_a_recorded_outcome(db_path):
    # Proves A4/A5's underlying logic directly: once DV-001-V1 has the
    # SUCCESS outcome a real seam (d) attempt will eventually produce,
    # a genuinely fresh session2.py process retrieves it, constrains
    # 25,000 -> 10,000, and names DV-001-V1 as the binding precedent on
    # screen. PrecedentRelationship persistence is deferred (see module
    # docstring) and not asserted here.
    reset(db_path)
    store = MemoryStore.local(db_path, tenant_id=DEMO_TENANT_ID)
    _seed_dv_001_v1_with_outcome(store)

    second = run_script("session2.py", db_path)
    assert second.returncode == 0, second.stderr
    assert "25000.00 proposed -> 10000.00 authorized" in second.stdout
    assert "constrain" in second.stdout
    assert "citing DV-001-V1" in second.stdout

    case = store.read_case_version("DV-002-V1")
    assert case is not None
    assert case.authorized_amount == Decimal("10000.00")
    assert store.read_owner_policy_snapshot("DV-002-V1") is not None
    assert store.fold_authority_state("DV-002-V1") == AuthorityState.DRAFT
    assert store.read_outcome("DV-002-V1") is None  # W4 still pending seam (d)


def test_no_memory_control_escalates_and_cannot_execute(db_path):
    # A6, invariant 6: with the tenant emptied (this test's stand-in for
    # "the load-bearing memory reads are removed"), retrieval finds
    # nothing and Session 2 must fall back to escalation — proving
    # autonomous execution above the cold-start floor is impossible
    # without memory, not merely improbable.
    reset(db_path)
    first = run_script("session1.py", db_path)
    assert first.returncode == 0, first.stderr

    second = run_script("session2.py", db_path, "--no-memory")
    assert second.returncode == 0, second.stderr
    assert "Retrieved 0 candidate(s)" in second.stdout
    assert "escalate" in second.stdout
    assert "Nothing authorized" in second.stdout
    assert "DV-001-V1" not in second.stdout


def test_reset_refuses_when_prior_session_data_exists(db_path):
    # BLOCKER (Codex, seam c round 1): reset_demo.py must not describe a
    # same-tenant reset as working when session1.py has already created
    # write-once records it cannot clear. It must fail with an
    # actionable message, not crash confusingly on the next session1.py
    # run's IntegrityError.
    reset(db_path)
    first = run_script("session1.py", db_path)
    assert first.returncode == 0, first.stderr

    second = run_script("reset_demo.py", db_path)
    assert second.returncode == 1
    assert "Cannot fully reset" in second.stderr
    assert "DV-001-V1" in second.stderr
    assert "new file rather than reusing this one" in second.stderr


def test_demo_resets_and_rehearses_repeatably(db_path):
    # A14: a full rehearsal (reset, then the entire session1 -> session2
    # sequence) produces the same observable outcome every time it is
    # repeated from a clean starting point. DV-001-V1's owner-policy
    # snapshot and authority-event journal entries are write-once by
    # design (invariant 8) and Sibyl Memory exposes no reference/journal
    # delete — reset_demo.py's own clear only covers the reseedable
    # CASE-003..008 fixtures, not a live-created case's history (see
    # test_reset_refuses_when_prior_session_data_exists above). A
    # genuinely clean full rehearsal is therefore a fresh database file,
    # exactly as a real re-take of the demo would start one.
    for _ in range(2):
        if db_path.exists():
            db_path.unlink()
        reset(db_path)
        first = run_script("session1.py", db_path)
        assert first.returncode == 0, first.stderr
        assert "Owner approves constrained authority: 10000.00" in first.stdout
        second = run_script("session2.py", db_path)
        assert second.returncode == 0, second.stderr
        assert "Nothing authorized" in second.stdout
