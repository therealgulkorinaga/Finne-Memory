#!/usr/bin/env python3
"""Reconciles a decision version left pending after a Base receipt-wait
timeout (BaseExecutionResult.outcome_confirmed=False) — session1.py and
session2.py correctly refuse to write an immutable Outcome.FAILURE for
a transaction that might still land and succeed, but that means
nothing ever automatically completes W4 (the outcome) for a pending
case. This script is that completion step, run manually once you know
whether enough time has passed to check: it queries the ORIGINAL
transaction's own receipt directly (via finne.base.adapter.reconcile_pending,
not just get_receipt, so "still pending" and "confirmed reverted" are
distinguished rather than both looking like "not found") and writes
the resulting outcome to Sibyl Memory — exactly once, since
write_outcome is itself write-once and refuses a second write.

The session script that hit the timeout prints the exact command to
run this with, including the decision_version_id and tx_hash it
already has.

Run: python scripts/reconcile_outcome.py <decision_version_id> --tx-hash <hash> [--db-path PATH]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from finne.base.adapter import ReconciliationMismatch, reconcile_pending
from finne.demo_config import DEMO_TENANT_ID
from finne.memory.client import MemoryStore
from finne.memory.schema import OutcomeRecord
from finne.models import Outcome


def reconcile(db_path: Path, decision_version_id: str, tx_hash: str) -> int:
    store = MemoryStore.local(db_path, tenant_id=DEMO_TENANT_ID)

    existing = store.read_outcome(decision_version_id)
    if existing is not None:
        print(f"{decision_version_id!r} already has a recorded outcome: {existing.outcome.value}")
        return 0

    if store.read_case_version(decision_version_id) is None:
        print(f"Refusing: {decision_version_id!r} has no case version — nothing to reconcile.", file=sys.stderr)
        return 1

    try:
        result = reconcile_pending(decision_version_id, tx_hash)
    except ReconciliationMismatch as exc:
        # The transaction cannot be bound to this decision at all — an
        # operator error about which hash to use, NOT a fact about the
        # decision's outcome. Nothing is written; treating this as a
        # confirmed failure is exactly the bug this path now prevents.
        print(f"Refusing: {exc}", file=sys.stderr)
        return 1

    print(result.detail)
    if not result.outcome_confirmed:
        print("Still unresolved. Nothing written; try again later.")
        return 1

    store.write_outcome(
        OutcomeRecord(
            decision_version_id=decision_version_id,
            outcome=Outcome.SUCCESS if result.success else Outcome.FAILURE,
            base_tx_hash=tx_hash,
        )
    )
    print(f"Reconciled {decision_version_id!r}: {'SUCCESS' if result.success else 'FAILURE'}, tx {tx_hash}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision_version_id")
    parser.add_argument("--tx-hash", required=True)
    parser.add_argument("--db-path", default="~/.sibyl-memory/memory.db")
    args = parser.parse_args()
    sys.exit(reconcile(Path(args.db_path).expanduser(), args.decision_version_id, args.tx_hash))


if __name__ == "__main__":
    main()
