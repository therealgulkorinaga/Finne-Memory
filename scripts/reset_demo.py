#!/usr/bin/env python3
"""Reset the demo to a known starting state.

Clears the demo tenant's records from Sibyl Memory, then re-seeds
CASE-003 through CASE-008 as pre-existing history, exactly per
docs/product/ACTIVE_DEMO_DESIGN.md section 5.

CASE-001 and CASE-002 are deliberately never seeded here — CASE-001 is
created live by session1.py and CASE-002 by session2.py, so the
fresh-session recall in Session 2 is genuine rather than staged
(ACTIVE_DEMO_DESIGN.md section 9).

Not in scope for this script or this seam: PrecedentRelationship
objects and OwnerPolicySnapshot references for the SEEDED fixtures
(CASE-003..008) specifically. Neither is read by the authority engine
or derivation logic — only the authority STATE each fixture reaches
matters for the demo's numeric correctness, which this script does
establish correctly.

What this script CANNOT do: fully reset a tenant where session1.py
and/or session2.py have already run. sibyl-memory-client exposes no
delete for the reference tier (owner-policy snapshots) or the journal
tier (authority events, precedent relationships) — both are write-once
/ append-only by design (invariant 8), and MemoryStore never overwrites
or deletes them. clear_all_case_data_for_demo_reset only removes
finne_case_version/finne_outcome entities, so DV-001-V1/DV-002-V1's
snapshot and event history would survive a clear and collide with a
fresh session1.py run's write-once checks. The pre-flight check below
detects this and fails with an actionable message instead of leaving
that collision to surface later as a confusing IntegrityError. A true
full rehearsal, once either session script has run, requires a new
database file (--db-path pointed at a new path).
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

from finne.demo_config import DEMO_TENANT_ID
from finne.memory.client import MemoryStore
from finne.memory.schema import AuthorityEventRecord, CaseVersionRecord, OutcomeRecord
from finne.models import AuthorityState, Outcome, Proposal, RiskTier

# The only decision_version_ids ever created live by session1.py/
# session2.py — the ones whose owner-policy-snapshot reference cannot
# be cleared by this script (see module docstring).
_LIVE_CREATED_DECISION_VERSION_IDS = ("DV-001-V1", "DV-002-V1")

# The claim profile the demonstration turns on: an in-panel residential
# buildings claim for SUDDEN escape of water, where the handler is
# deciding whether to settle.
BASELINE_FACTS = Proposal(
    network="uk_retail_direct",
    asset="GBP",
    action_class="claim_assessment",
    target_class="escape_of_water_sudden",
    function="approve_settlement",
    counterparty_risk_tier=RiskTier.LOW,
    amount=Decimal("0.00"),  # facts-only fixture; amount is not a comparability dimension
    proposed_at="2026-09-01T00:00:00Z",
)

# A different peril entirely. Still in scope, still active precedent —
# but not comparable to an escape-of-water claim, which is the point of
# CASE-004: similarity and authority are separate questions.
STORM_FACTS = Proposal(
    **{**BASELINE_FACTS.__dict__, "target_class": "storm_damage"}
)

# The claim that looks the same and is not. GRADUAL escape of water is
# excluded by the policy wording, which covers sudden and accidental
# damage only. This is CASE-005, and it is the fixture that proves the
# engine distinguishes on causation rather than on surface similarity —
# the exact failure that produces a complaint when a handler classifies
# by appearance.
GRADUAL_FACTS = Proposal(
    **{**BASELINE_FACTS.__dict__, "target_class": "escape_of_water_gradual"}
)


def _confirm_then_activate(store: MemoryStore, decision_version_id: str) -> None:
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id=decision_version_id,
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner_as_decision_reviewer",
            reason="seed: reviewer confirms the decision record",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id=decision_version_id,
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner_as_authority_steward",
            reason="seed: authority steward signs it off as precedent",
        )
    )


def seed(store: MemoryStore) -> None:
    # CASE-003: identical claim profile, settled at 20000, later
    # OVERTURNED by the ombudsman. Retrievable, never authorizing.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-003-V1",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("20000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-003-V1", outcome=Outcome.SUCCESS, base_tx_hash=None)
    )
    _confirm_then_activate(store, "DV-003-V1")
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-003-V1",
            previous_status=AuthorityState.ACTIVE,
            new_status=AuthorityState.WITHDRAWN,
            changed_by="owner_as_authority_steward",
            reason="seed: overturned by the ombudsman on appeal",
        )
    )

    # CASE-004: storm damage. A different peril, so not comparable,
    # but a perfectly good active precedent for storm claims.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-004-V1",
            facts=STORM_FACTS,
            authorized_amount=Decimal("5000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-004-V1", outcome=Outcome.SUCCESS, base_tx_hash=None)
    )
    _confirm_then_activate(store, "DV-004-V1")

    # CASE-005: GRADUAL escape of water. Same peril family, same
    # everything else, excluded by the wording. The material-difference
    # fixture.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-005-V1",
            facts=GRADUAL_FACTS,
            authorized_amount=Decimal("10000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-005-V1", outcome=Outcome.SUCCESS, base_tx_hash=None)
    )
    _confirm_then_activate(store, "DV-005-V1")

    # CASE-006: identical claim profile, settled at 15000 under policy
    # wording v2, which has since been replaced by v4.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-006-V1",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("15000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-006-V1", outcome=Outcome.SUCCESS, base_tx_hash=None)
    )
    _confirm_then_activate(store, "DV-006-V1")
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-006-V1",
            previous_status=AuthorityState.ACTIVE,
            new_status=AuthorityState.SUPERSEDED,
            changed_by="owner_as_authority_steward",
            reason="seed: decided under policy wording v2, superseded by v4",
        )
    )

    # CASE-007: identical claim profile, settled at 12000, settlement
    # subsequently reversed, and now under complaint.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-007-V1",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("12000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-007-V1", outcome=Outcome.FAILURE, base_tx_hash=None)
    )
    _confirm_then_activate(store, "DV-007-V1")
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-007-V1",
            previous_status=AuthorityState.ACTIVE,
            new_status=AuthorityState.QUESTIONED,
            changed_by="owner_as_authority_steward",
            reason="seed: under complaint after the settlement was reversed",
        )
    )

    # CASE-008: identical claim profile, settled at 18000, recorded but
    # never signed off by the authority steward.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id="DV-008-V1",
            facts=BASELINE_FACTS,
            authorized_amount=Decimal("18000.00"),
        )
    )
    store.write_outcome(
        OutcomeRecord(decision_version_id="DV-008-V1", outcome=Outcome.SUCCESS, base_tx_hash=None)
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id="DV-008-V1",
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner_as_decision_reviewer",
            reason="seed: recorded as draft, never signed off",
        )
    )


def _check_no_live_created_residue(store: MemoryStore) -> list[str]:
    """Returns the subset of DV-001-V1/DV-002-V1 that already has ANY
    immutable trace — a case version (cleared by this script, but its
    mere presence signals a prior run happened here), an owner-policy
    snapshot, or authority-event history (neither reference nor journal
    entries can be cleared). Checking only the snapshot missed an
    interrupted run that got as far as W1/W3 but not W2 (Codex, seam c
    round 2) — checking all three is defense in depth against any write
    ordering, not just this script's current one. A non-empty result
    means this tenant/database cannot be fully reset in place; see the
    module docstring."""
    return [
        decision_version_id
        for decision_version_id in _LIVE_CREATED_DECISION_VERSION_IDS
        if store.read_case_version(decision_version_id) is not None
        or store.read_owner_policy_snapshot(decision_version_id) is not None
        or store.fold_authority_state(decision_version_id) is not None
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-path",
        default="~/.sibyl-memory/memory.db",
        help="Path to the Sibyl Memory database (default: the standard local path).",
    )
    args = parser.parse_args()

    store = MemoryStore.local(Path(args.db_path).expanduser(), tenant_id=DEMO_TENANT_ID)

    residual = _check_no_live_created_residue(store)
    if residual:
        print(
            f"Cannot fully reset: {', '.join(residual)} already has an immutable "
            "owner-policy snapshot (and/or authority-event history) from a prior "
            "session1.py/session2.py run. Sibyl Memory's reference and journal "
            "tiers are write-once/append-only and this adapter never overwrites "
            "or deletes them (invariant 8). To fully rehearse the demo again, "
            "point --db-path at a new file rather than reusing this one.",
            file=sys.stderr,
        )
        sys.exit(1)

    store.clear_all_case_data_for_demo_reset(confirm_tenant_id=DEMO_TENANT_ID)
    seed(store)
    print(
        f"Demo tenant {DEMO_TENANT_ID!r} reset: CASE-003 through CASE-008 seeded. "
        "CASE-001 and CASE-002 are not seeded — they are created live by "
        "session1.py and session2.py."
    )


if __name__ == "__main__":
    main()
