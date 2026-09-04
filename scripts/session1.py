#!/usr/bin/env python3
"""Session 1 — establish experience.

Per docs/product/ACTIVE_DEMO_DESIGN.md section 7 and SPEC-001 section 4:
the agent proposes 25,000 USDC against the 25,000 USDC owner ceiling.
With no comparable active precedent yet, the engine escalates rather
than silently authorizing the full amount. The owner approves a
constrained 10,000 USDC. The agent executes within that bound and the
complete case is persisted to Sibyl Memory. The process then exits
completely — Session 2 must be a genuinely fresh process, not a
continuation of this one.

W1 (case version), W2 (owner-policy snapshot), and W3 (draft -> active
authority events) are written immediately once the owner approves —
PREREQ-003 section 3 places all three "after the owner constrains
authority" / "on owner confirmation," independent of Base. W4 (the
outcome) is written only "after the Base transaction settles" — i.e.
only when record_authorization() reports attempted=True. While
finne/base/adapter.py remains seam (d)'s stub (attempted always
False), this script persists a complete, genuine authorization record
with no outcome yet, rather than fabricating one — DV-001-V1 is
therefore not yet eligible as precedent (finne.authority.derivation
requires outcome == SUCCESS) until a real Base attempt exists.

Run: python scripts/session1.py [--db-path PATH] [--owner-approved-amount N]
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
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
from finne.models import (
    AuthorityState,
    AuthorizationResult,
    Outcome,
    Proposal,
    RiskTier,
)
from finne.policy import default_hard_policy, load_owner_policy
from finne.retrieval import find_candidates

DECISION_VERSION_ID = "DV-001-V1"


def build_proposal(amount: Decimal) -> Proposal:
    return Proposal(
        network=DEMO_NETWORK,
        asset=DEMO_ASSET,
        action_class=DEMO_ACTION_CLASS,
        target_class=DEMO_TARGET_CLASS,
        function=DEMO_FUNCTION,
        counterparty_risk_tier=RiskTier.LOW,
        amount=amount,
        proposed_at="2026-09-01T00:00:00Z",
    )


def run(db_path: Path, owner_approved_amount: Decimal) -> int:
    store = MemoryStore.local(db_path, tenant_id=DEMO_TENANT_ID)
    owner_policy = load_owner_policy()
    hard_policy = default_hard_policy()

    proposal = build_proposal(owner_policy.max_amount)
    print(f"[Session 1] Owner ceiling: {owner_policy.max_amount} {owner_policy.asset}")
    print(f"[Session 1] Agent proposes: {proposal.amount} {proposal.asset}")

    candidates = find_candidates(proposal, store)
    print(f"[Session 1] Retrieved {len(candidates)} candidate(s) from Sibyl Memory.")

    decision = derive_effective_authority(proposal, owner_policy, hard_policy, candidates)
    print(f"[Session 1] Deterministic result: {decision.result.value} — {decision.explanation}")

    if decision.result == AuthorizationResult.BLOCK:
        # A blocked decision means the raw proposal itself would violate
        # a hard boundary (e.g. NEG-04, above the owner ceiling) — there
        # is nothing for the owner to approve; overriding it would
        # violate invariant 1. Stop; nothing is submitted or persisted.
        print("[Session 1] Proposal blocked outright; refusing to proceed.", file=sys.stderr)
        return 1
    if decision.result != AuthorizationResult.ESCALATE:
        print(
            "[Session 1] UNEXPECTED: cold start did not escalate. Refusing to "
            "proceed rather than silently authorize an unreviewed amount.",
            file=sys.stderr,
        )
        return 1

    # The owner reviews the escalation and approves a constrained amount.
    # ACTIVE_DEMO_DESIGN.md section 7 fixes this at 10,000 USDC as the
    # documented demo scenario, not a live judgment call each run —
    # encoded here as the script's own deterministic default so the demo
    # is reproducible and test_fresh_session.py can run it
    # non-interactively. --owner-approved-amount lets a live demo
    # recording show this being entered on camera instead, if desired.
    if owner_approved_amount <= 0:
        # A zero or negative "approval" authorizes nothing — activating
        # it as an ACTIVE precedent would misrepresent that a genuine
        # authorization occurred. Codex (seam c round 2) reproduced this
        # against a live database: --owner-approved-amount 0 previously
        # activated DV-001-V1 with authorized_amount=0.
        print(
            f"[Session 1] Refusing: owner-approved amount {owner_approved_amount} "
            "authorizes nothing; a genuine approval must be positive.",
            file=sys.stderr,
        )
        return 1
    if owner_approved_amount > owner_policy.max_amount:
        print(
            f"[Session 1] Refusing: owner-approved amount {owner_approved_amount} "
            f"would exceed the owner ceiling {owner_policy.max_amount}.",
            file=sys.stderr,
        )
        return 1
    print(f"[Session 1] Owner approves constrained authority: {owner_approved_amount} {owner_policy.asset}")

    # The engine's own decision authorized nothing (escalate, amount 0)
    # — that decision must never be the thing submitted to Base or
    # persisted as what happened. The owner's manual approval is an
    # explicit, distinct, auditable authorization in its own right,
    # constructed here (not by finne.authority.engine, which stays pure
    # and unaware of human overrides) so what gets submitted and
    # recorded accurately reflects what was actually authorized.
    owner_decision = replace(
        decision,
        result=AuthorizationResult.CONSTRAIN,
        authorized_amount=owner_approved_amount,
        binding_constraint="owner_manual_approval",
        explanation=(
            f"Owner manually approved {owner_approved_amount} {owner_policy.asset} "
            "after the deterministic engine escalated this proposal "
            f"(engine explanation: {decision.explanation})"
        ),
    )

    # W1 + W2 + W3: the authorization itself — case version, the
    # owner-policy snapshot in force, and the draft -> active authority
    # events — are written now, per PREREQ-003 section 3 ("after the
    # owner constrains authority" / "on owner confirmation"). None of
    # these wait on Base; only W4 (the outcome) does.
    store.write_case_version(
        CaseVersionRecord(
            decision_version_id=DECISION_VERSION_ID,
            facts=proposal,
            authorized_amount=owner_approved_amount,
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
            reason="Owner confirms the constrained authorization.",
        )
    )
    store.append_authority_event(
        AuthorityEventRecord(
            decision_version_id=DECISION_VERSION_ID,
            previous_status=AuthorityState.DRAFT,
            new_status=AuthorityState.ACTIVE,
            changed_by="owner_as_authority_steward",
            reason="Owner activates the case as precedent.",
        )
    )
    print(f"[Session 1] Authorization persisted to Sibyl Memory as {DECISION_VERSION_ID} (draft -> active).")

    base_result = record_authorization(owner_decision, DECISION_VERSION_ID)
    if not base_result.attempted:
        # W4 has not happened yet — the outcome genuinely does not exist
        # (PREREQ-003 section 3: written "after the Base transaction
        # settles"). Recording SUCCESS here, with no transaction, would
        # be exactly the fabrication NEG-07 forbids. DV-001-V1 is
        # correctly not yet eligible as precedent until a real attempt
        # exists — that is seam (d)'s job, not this script's.
        print(f"[Session 1] {base_result.detail}")
        print("[Session 1] No outcome recorded — Base execution is pending seam (d).")
        print("[Session 1] Process exiting completely.")
        return 0

    if not base_result.success:
        # NEG-07: a real, attempted Base failure must never be reported
        # as a success. The authorization above is still a true,
        # complete record of what the owner approved; W4 now records
        # that the attempted execution failed.
        store.write_outcome(
            OutcomeRecord(
                decision_version_id=DECISION_VERSION_ID,
                outcome=Outcome.FAILURE,
                base_tx_hash=base_result.tx_hash,
            )
        )
        print(f"[Session 1] Base execution failed: {base_result.detail}", file=sys.stderr)
        return 1

    store.write_outcome(
        OutcomeRecord(
            decision_version_id=DECISION_VERSION_ID,
            outcome=Outcome.SUCCESS,
            base_tx_hash=base_result.tx_hash,
        )
    )
    print(f"[Session 1] Base transaction: {base_result.tx_hash}")
    print(f"[Session 1] Complete case persisted to Sibyl Memory as {DECISION_VERSION_ID}.")
    print("[Session 1] Process exiting completely.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default="~/.sibyl-memory/memory.db")
    parser.add_argument("--owner-approved-amount", default="10000.00")
    args = parser.parse_args()
    sys.exit(
        run(Path(args.db_path).expanduser(), Decimal(args.owner_approved_amount))
    )


if __name__ == "__main__":
    main()
