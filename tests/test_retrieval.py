"""Tests for candidate precedent generation (R1), against real temporary
Sibyl Memory databases — not mocks. Proves the safety property that a
retrieval miss can only narrow, never widen, the candidates the engine
sees, and that assembly correctly excludes cases that cannot yet be
judged (no confirmed authority state, no recorded outcome) while still
surfacing withdrawn/superseded/questioned/draft cases as retrievable.
"""

from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from finne.memory.client import MemoryStore
from finne.memory.schema import AuthorityEventRecord, CaseVersionRecord, OutcomeRecord
from finne.models import AuthorityState, Outcome, Proposal, RiskTier
from finne.retrieval import find_candidates

BASELINE_FACTS = Proposal(
    network="base",
    asset="USDC",
    action_class="capital_deployment",
    target_class="yield_vault_conservative",
    function="deposit",
    counterparty_risk_tier=RiskTier.LOW,
    amount=Decimal("25000.00"),
    proposed_at="2026-09-03T00:00:00Z",
)


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield MemoryStore.local(Path(tmpdir) / "test_memory.db")


def confirm_active(store: MemoryStore, decision_version_id: str) -> None:
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id=decision_version_id,
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner",
            reason="confirm",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id=decision_version_id,
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner",
            reason="activate",
        )
    )


def write_full_case(
    store: MemoryStore,
    decision_version_id: str,
    *,
    facts: Proposal = BASELINE_FACTS,
    authorized_amount: Decimal = Decimal("10000.00"),
    outcome: Outcome = Outcome.SUCCESS,
    authority_state: AuthorityState = AuthorityState.ACTIVE,
) -> None:
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id=decision_version_id, facts=facts, authorized_amount=authorized_amount
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id=decision_version_id, outcome=outcome, base_tx_hash="0xabc")
    )
    if authority_state == AuthorityState.ACTIVE:
        confirm_active(store, decision_version_id)
    elif authority_state == AuthorityState.DRAFT:
        store.append_authority_event(
            AuthorityEventRecord(
                decision_version_id=decision_version_id,
                previous_status=None,
                new_status=AuthorityState.DRAFT,
                changed_by="owner",
                reason="confirm only",
            )
        )
    elif authority_state == AuthorityState.WITHDRAWN:
        confirm_active(store, decision_version_id)
        store.append_authority_event(
            AuthorityEventRecord(
                decision_version_id=decision_version_id,
                previous_status=AuthorityState.ACTIVE,
                new_status=AuthorityState.WITHDRAWN,
                changed_by="owner",
                reason="withdraw",
            )
        )
    else:
        raise NotImplementedError(authority_state)


def test_finds_a_fully_confirmed_active_case(store):
    write_full_case(store, "DV-001-V1")
    candidates = find_candidates(BASELINE_FACTS, store)
    ids = [c.decision_version_id for c in candidates]
    assert ids == ["DV-001-V1"]
    assert candidates[0].is_eligible() is True


def test_excludes_case_with_no_recorded_outcome(store):
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-NOOUTCOME", facts=BASELINE_FACTS, authorized_amount=Decimal("5000.00")
        )
    )
    confirm_active(store, "DV-NOOUTCOME")
    candidates = find_candidates(BASELINE_FACTS, store)
    assert candidates == []


def test_excludes_case_with_no_confirmed_authority_state(store):
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-UNCONFIRMED",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("5000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-UNCONFIRMED", outcome=Outcome.SUCCESS, base_tx_hash="0xabc")
    )
    # No authority event appended at all.
    candidates = find_candidates(BASELINE_FACTS, store)
    assert candidates == []


def test_withdrawn_case_is_still_retrieved_and_displayable(store):
    """PREREQ-002: withdrawn cases remain retrievable and displayable —
    only ineligible for derivation, which is finne.authority's job to
    decide, not retrieval's."""
    write_full_case(store, "DV-003-V1", authority_state=AuthorityState.WITHDRAWN)
    candidates = find_candidates(BASELINE_FACTS, store)
    assert len(candidates) == 1
    assert candidates[0].authority_state == AuthorityState.WITHDRAWN
    assert candidates[0].is_eligible() is False


def test_draft_case_is_still_retrieved_and_displayable(store):
    write_full_case(store, "DV-008-V1", authority_state=AuthorityState.DRAFT)
    candidates = find_candidates(BASELINE_FACTS, store)
    assert len(candidates) == 1
    assert candidates[0].authority_state == AuthorityState.DRAFT
    assert candidates[0].is_eligible() is False


def test_material_difference_case_is_still_retrieved(store):
    """A case with a different target_class is still surfaced as a
    candidate — comparability exclusion happens on the candidate object,
    not by hiding it from retrieval, so the demo can display it and
    explain why it was excluded."""
    different_facts = Proposal(
        **{**BASELINE_FACTS.__dict__, "target_class": "yield_vault_aggressive"}
    )
    write_full_case(store, "DV-005-V1", facts=different_facts)
    candidates = find_candidates(BASELINE_FACTS, store)
    assert len(candidates) == 1
    assert candidates[0].comparability.is_comparable is False
    assert candidates[0].is_eligible() is False


def test_no_candidates_on_empty_memory(store):
    assert find_candidates(BASELINE_FACTS, store) == []


def test_finds_all_corpus_style_fixtures_regardless_of_target_class(store):
    """The search query is deliberately coarse (network/asset/action_class
    only) precisely so less-similar-but-still-relevant cases like this
    one are retrieved for comparability to judge, not silently dropped
    by an overly narrow search."""
    demo_receipt_facts = Proposal(
        **{
            **BASELINE_FACTS.__dict__,
            "target_class": "demo_receipt",
            "function": "recordAuthorization",
        }
    )
    write_full_case(store, "DV-004-V1", facts=demo_receipt_facts, authorized_amount=Decimal("5000.00"))
    candidates = find_candidates(BASELINE_FACTS, store)
    assert len(candidates) == 1
    assert candidates[0].decision_version_id == "DV-004-V1"


def test_retrieval_miss_only_narrows_never_widens_derivation():
    """The stated safety property: simulate a retrieval miss (fewer
    candidates surfaced) and confirm the resulting learned constraint can
    only be lower or equal, never higher, than with the full candidate
    set — proven at the retrieval+derivation boundary, complementing the
    pure-engine version of this property already proven in
    test_authority_invariants.py."""
    from finne.authority.derivation import derive_learned_constraint
    from finne.models import OwnerPolicy

    owner_policy = OwnerPolicy(
        max_amount=Decimal("25000.00"),
        network="base",
        asset="USDC",
        action_class="capital_deployment",
        approved_target_classes=("yield_vault_conservative",),
        approved_functions=("deposit",),
        unknown_situation_behaviour="escalate_to_owner",
        cold_start_autonomous_amount=Decimal("0.00"),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore.local(Path(tmpdir) / "miss.db")
        write_full_case(store, "DV-001-V1", authorized_amount=Decimal("10000.00"))
        write_full_case(store, "DV-002-V1", authorized_amount=Decimal("18000.00"))

        full_candidates = find_candidates(BASELINE_FACTS, store)
        full_learned = derive_learned_constraint(tuple(full_candidates), owner_policy)

        missed_candidates = [c for c in full_candidates if c.decision_version_id != "DV-002-V1"]
        missed_learned = derive_learned_constraint(tuple(missed_candidates), owner_policy)

        assert missed_learned.learned_max_amount <= full_learned.learned_max_amount
