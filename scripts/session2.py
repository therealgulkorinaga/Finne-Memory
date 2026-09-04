#!/usr/bin/env python3
"""Session 2 — memory changes behaviour.

A genuinely fresh process (run this as its own `python` invocation, not
an import from session1.py) proposes the same 25,000 USDC action.
Unlike Session 1, once Sibyl Memory holds CASE-001 as an active, SUCCESSFUL
precedent (i.e. once seam (d) has recorded a real Base outcome for it),
the engine constrains the proposal to 10,000 USDC instead of escalating
— the change is attributable to the recalled memory, not to anything
hardcoded in this script.

Until DV-001-V1 has a recorded outcome, this run will honestly escalate
too, exactly like the --no-memory control below: an escalated decision
authorizes nothing, so this script stops without submitting anything to
Base or persisting a case for CASE-002 (per PREREQ-003 section 3, W1-W4
only apply to an authorization that actually happened; there is no
"owner override" path in Session 2 the way there is in Session 1 —
Session 2 exists specifically to prove autonomous behavior).

--no-memory reproduces the organiser's deletion test: it points at a
fresh, never-seeded tenant instead of the demo tenant, so retrieval
finds nothing and the engine falls back to cold-start escalation —
proving memory is load-bearing without destructively deleting the real
demo data.

Run: python scripts/session2.py [--db-path PATH] [--no-memory]
"""

from __future__ import annotations

import argparse
import sys
import uuid
from decimal import Decimal
from pathlib import Path

from finne.authority.engine import derive_effective_authority
from finne.base.adapter import record_authorization
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
from finne.policy import default_hard_policy, load_owner_policy
from finne.retrieval import find_candidates

DECISION_VERSION_ID = "DV-002-V1"


def build_proposal(amount: Decimal) -> Proposal:
    return Proposal(
        network=DEMO_NETWORK,
        asset=DEMO_ASSET,
        action_class=DEMO_ACTION_CLASS,
        target_class=DEMO_TARGET_CLASS,
        function=DEMO_FUNCTION,
        counterparty_risk_tier=RiskTier.LOW,
        amount=amount,
        proposed_at="2026-09-02T00:00:00Z",
    )


def run(db_path: Path, *, no_memory: bool) -> int:
    # No in-process state is carried over from session1.py — this is a
    # separate OS process. no_memory uses a fresh, never-seeded tenant
    # instead of touching the real demo data, reproducing the
    # organiser's deletion test without destroying Session 1's case.
    tenant_id = f"empty-{uuid.uuid4()}" if no_memory else DEMO_TENANT_ID
    store = MemoryStore.local(db_path, tenant_id=tenant_id)
    owner_policy = load_owner_policy()
    hard_policy = default_hard_policy()

    proposal = build_proposal(owner_policy.max_amount)
    print(f"[Session 2] Fresh process. Owner ceiling: {owner_policy.max_amount} {owner_policy.asset}")
    print(f"[Session 2] Agent proposes: {proposal.amount} {proposal.asset}")

    candidates = find_candidates(proposal, store)
    print(f"[Session 2] Retrieved {len(candidates)} candidate(s) from Sibyl Memory.")
    for c in candidates:
        tag = "eligible" if c.is_eligible() else f"excluded ({c.authority_state.value}/{c.outcome.value}/comparable={c.comparability.is_comparable})"
        print(f"[Session 2]   {c.decision_version_id}: authorized={c.authorized_amount} [{tag}]")

    decision = derive_effective_authority(proposal, owner_policy, hard_policy, candidates)
    print(f"[Session 2] Deterministic result: {decision.result.value} — {decision.explanation}")

    if decision.authorized_amount <= 0:
        # Nothing was autonomously authorized. Session 2 has no "owner
        # override" path the way Session 1 does — it exists specifically
        # to prove autonomous behavior, so an escalated (or blocked)
        # result means the run stops here. Nothing is submitted to Base
        # and no case is persisted for CASE-002, matching "stop
        # execution on non-authorizing decisions": persisting a case
        # with a zero-authority decision would misrepresent that
        # something was authorized when nothing was.
        print("[Session 2] Nothing authorized; the agent cannot proceed autonomously.")
        return 0

    print(
        f"[Session 2] Action changes: {proposal.amount} proposed -> "
        f"{decision.authorized_amount} authorized "
        f"(citing {', '.join(decision.cited_precedents) or 'no precedent'})"
    )

    # W1 + W2 + W3: the authorization itself is written now — per
    # PREREQ-003 section 3, none of these wait on Base, only W4 does.
    # DV-002-V1 is deliberately left at draft (ACTIVE_DEMO_DESIGN.md
    # section 7 step 11: "it does not activate DV-002-V1 ... promoting
    # it to active is out of scope for this slice") — a single
    # Decision-Reviewer confirmation event, no Authority-Steward
    # activation event.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id=DECISION_VERSION_ID,
            facts=proposal,
            authorized_amount=decision.authorized_amount,
        )
    )
    store.write_owner_policy_snapshot(
        DECISION_VERSION_ID,
        OwnerPolicySnapshot(
            max_amount=owner_policy.max_amount,
            network=owner_policy.network,
            asset=owner_policy.asset,
            action_class=owner_policy.action_class,
            approved_target_classes=owner_policy.approved_target_classes,
            approved_functions=owner_policy.approved_functions,
            cold_start_autonomous_amount=owner_policy.cold_start_autonomous_amount,
        ),
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id=DECISION_VERSION_ID,
            previous_status=None,
            new_status=AuthorityState.DRAFT,
            changed_by="owner_as_decision_reviewer",
            reason="Owner confirms creation of the autonomously-constrained case.",
        )
    )

    # ACTIVE_DEMO_DESIGN.md section 7 step 11 also describes the Owner,
    # as Authority Steward, confirming follows/distinguishes
    # PrecedentRelationship records once DV-002-V1 exists. Deferred from
    # this seam: PREREQ-002's own contract requires fact_ids/citation_ids
    # to reference real, human-validated CitationEdge/Fact entities with
    # a rejection-audit path, not a shape a few tuples of strings can
    # satisfy — out of scope per SPEC-001 section 15, required by none
    # of the fourteen acceptance criteria, and not part of PREREQ-003
    # section 3's load-bearing W1-W5/R1-R5 set. See finne/memory/schema.py.

    print(f"[Session 2] Authorization persisted to Sibyl Memory as {DECISION_VERSION_ID} (draft).")

    base_result = record_authorization(decision, DECISION_VERSION_ID)
    if not base_result.attempted:
        print(f"[Session 2] {base_result.detail}")
        print("[Session 2] No outcome recorded — Base execution is pending seam (d).")
        return 0

    if not base_result.success:
        store.write_outcome(
            OutcomeRecord(
                decision_version_id=DECISION_VERSION_ID,
                outcome=Outcome.FAILURE,
                base_tx_hash=base_result.tx_hash,
            )
        )
        print(f"[Session 2] Base execution failed: {base_result.detail}", file=sys.stderr)
        return 1

    store.write_outcome(
        OutcomeRecord(
            decision_version_id=DECISION_VERSION_ID,
            outcome=Outcome.SUCCESS,
            base_tx_hash=base_result.tx_hash,
        )
    )
    print(f"[Session 2] Base transaction: {base_result.tx_hash}")
    print(f"[Session 2] Outcome persisted to Sibyl Memory as {DECISION_VERSION_ID}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default="~/.sibyl-memory/memory.db")
    parser.add_argument("--no-memory", action="store_true")
    args = parser.parse_args()
    sys.exit(run(Path(args.db_path).expanduser(), no_memory=args.no_memory))


if __name__ == "__main__":
    main()
