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
import traceback
import uuid
from decimal import Decimal
from pathlib import Path

from finne import cli
from finne.authority.engine import derive_effective_authority
from finne.base.adapter import record_authorization
from finne.explain import explain
from finne.demo_config import (
    DEMO_ACTION_CLASS,
    DEMO_ASSESSED_VALUE,
    DEMO_ASSET,
    DEMO_FUNCTION,
    DEMO_NETWORK,
    DEMO_CASE_SUMMARY,
    DEMO_TARGET_CLASS,
    DEMO_TENANT_ID,
)
from finne.memory.client import MemoryStore, is_memory_unavailable
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

def proposal_source(agent_mode: str) -> str:
    """What to show on screen about where the proposal came from."""
    if agent_mode != "model":
        return "fixed demo value — no model called (use --agent=model for the live agent)"
    from finne.agent import LAST_MODEL_USED

    return f"claims agent — {LAST_MODEL_USED or 'model'} via OpenRouter (live)"


def obtain_proposal(agent_mode: str, assessed_value: Decimal) -> Proposal:
    """Where the proposal comes from.

    `fixed` is the default and is byte-identical to the behaviour before
    SPEC-002: a deterministic proposal, no key, no network. The suite and
    the organiser's deletion gate both run this path.

    `model` calls the assessing agent. Note what is passed: the loss
    adjuster's assessed value, never `owner_policy.max_amount`. The agent
    cannot see the ceiling and cannot reach the policy module — that is
    SPEC-002 invariant 11, enforced structurally by
    tests/test_import_boundaries.py, and it is what makes the
    demonstration honest. The bound comes from Finné Memory, not from
    the agent's restraint.
    """
    if agent_mode == "fixed":
        return build_proposal(assessed_value)
    from finne.agent import CaseUnderAssessment, propose

    return propose(
        CaseUnderAssessment(
            summary=DEMO_CASE_SUMMARY,
            assessed_value=assessed_value,
            network=DEMO_NETWORK,
            asset=DEMO_ASSET,
            action_class=DEMO_ACTION_CLASS,
            target_class=DEMO_TARGET_CLASS,
            function=DEMO_FUNCTION,
        )
    )


def run(db_path: Path, *, no_memory: bool, agent_mode: str = "fixed") -> int:
    # No in-process state is carried over from session1.py — this is a
    # separate OS process. no_memory uses a fresh, never-seeded tenant
    # instead of touching the real demo data, reproducing the
    # organiser's deletion test without destroying Session 1's case.
    tenant_id = f"empty-{uuid.uuid4()}" if no_memory else DEMO_TENANT_ID
    owner_policy = load_owner_policy()
    hard_policy = default_hard_policy()

    try:
        proposal = obtain_proposal(agent_mode, DEMO_ASSESSED_VALUE)
    except Exception as exc:  # noqa: BLE001 — shown, never swallowed
        # SPEC-002 section 8: an agent failure is a visible failure.
        # There is deliberately no fallback to a fixed proposal — that
        # would make the demonstration appear to work while proving
        # nothing about the agent.
        cli.warn(f"Agent could not produce a proposal: {type(exc).__name__}: {exc}")
        print(f"[Session 2] agent failure: {exc}", file=sys.stderr)
        return 1

    cli.session_header("Session 2", "a materially similar claim — a genuinely fresh process")
    cli.proposal_panel(proposal, owner_policy.max_amount, source=proposal_source(agent_mode))

    # NEG-01 / PREREQ-003 section 19, same handling as session1.py: a
    # memory failure is displayed as an escalation, never as the empty
    # corpus --no-memory produces. The traceback goes to stderr, not to
    # the frame the viewer reads.
    # --no-memory is a real, readable, EMPTY tenant; this branch is the
    # case where nothing could be read at all.
    try:
        store = MemoryStore.local(db_path, tenant_id=tenant_id)
        candidates = find_candidates(proposal, store)
    except Exception as exc:  # noqa: BLE001 — classified, not swallowed
        # is_memory_unavailable() walks the __cause__ chain rather than
        # type-testing the outermost exception: the memory client wraps
        # a caller defect (SQL misuse) in its own StorageError, and a
        # genuinely corrupt database file surfaces as a raw
        # sqlite3.DatabaseError. No flat tuple of types separates those,
        # which independent review demonstrated in both directions.
        # A bug re-raises and stays visible; only a real outage becomes
        # the displayed escalation.
        if not is_memory_unavailable(exc):
            raise
        # The traceback goes to stderr so a real failure stays
        # diagnosable; the screen shows the clean, safe outcome.
        traceback.print_exc()
        cli.memory_failure(f"{type(exc).__name__}: {exc}")
        return 1
    cli.candidates_table(candidates)

    decision = derive_effective_authority(proposal, owner_policy, hard_policy, candidates)

    if decision.authorized_amount <= 0:
        # Nothing was autonomously authorized. Session 2 has no "owner
        # override" path the way Session 1 does — it exists specifically
        # to prove autonomous behavior, so an escalated (or blocked)
        # result means the run stops here. Nothing is submitted to Base
        # and no case is persisted for CASE-002, matching "stop
        # execution on non-authorizing decisions": persisting a case
        # with a zero-authority decision would misrepresent that
        # something was authorized when nothing was.
        cli.decision_panel(decision, proposal, explain(decision))
        cli.warn("Nothing authorized. The handler cannot proceed without sign-off.")
        return 0

    # explain() is presentation only and cannot change `decision` — it
    # is called after the decision is already final, and its output is
    # never read back (A10/NEG-05: identical authorization with or
    # without a model API key).
    cli.decision_panel(decision, proposal, explain(decision))

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

    cli.note(f"Authorization persisted to Sibyl Memory as {DECISION_VERSION_ID} (draft).")

    base_result = record_authorization(decision, proposal, DECISION_VERSION_ID)
    if not base_result.attempted:
        # base_result.detail states the actual reason (refused
        # pre-flight, connection failure, or a detected NEG-08
        # duplicate) — never assumed here.
        cli.note(base_result.detail)
        cli.note("No outcome recorded.")
        return 0

    if not base_result.success:
        if not base_result.outcome_confirmed:
            # Broadcast accepted, confirmation unknown — not a
            # confirmed failure. See scripts/session1.py's matching
            # branch for the full rationale (W4 is write-once).
            print(f"[Session 2] {base_result.detail}", file=sys.stderr)
            print(
                f"[Session 2] No outcome recorded. Once you know whether it landed, run:\n"
                f"  python scripts/reconcile_outcome.py {DECISION_VERSION_ID} --tx-hash {base_result.tx_hash}",
                file=sys.stderr,
            )
            return 1
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
    cli.note(f"Base transaction: {base_result.tx_hash}")
    cli.note(f"Outcome persisted to Sibyl Memory as {DECISION_VERSION_ID}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default="~/.sibyl-memory/memory.db")
    parser.add_argument("--no-memory", action="store_true")
    parser.add_argument(
        "--agent",
        choices=("fixed", "model"),
        default="fixed",
        help="Where the proposal comes from. `fixed` (default) is deterministic and needs "
             "no key or network. `model` asks the proposing agent (SPEC-002).",
    )
    args = parser.parse_args()
    sys.exit(run(Path(args.db_path).expanduser(), no_memory=args.no_memory, agent_mode=args.agent))


if __name__ == "__main__":
    main()
