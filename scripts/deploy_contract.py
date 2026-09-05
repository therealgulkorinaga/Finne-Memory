#!/usr/bin/env python3
"""Thin CLI wrapper around finne.base.adapter.deploy_contract().

The actual compile/deploy/sign/send logic — the only place besides
finne/base/adapter.py's own record_authorization/get_receipt that
reads FINNE_BASE_PRIVATE_KEY or reaches the network — lives there, not
here, per PREREQ-003 section 6 ("only finne/base/adapter.py holds key
material or reaches the network"). This script previously imported
eth_account/web3 and signed transactions directly; independent review
found that a module-boundary violation, moved to finne/base/adapter.py
accordingly. tests/test_import_boundaries.py enforces this statically
going forward.

Deploys to whatever network BASE_RPC_URL points at (Base Sepolia by
default — ORG-Q1 makes the network a configuration value, not a code
change). Refuses to redeploy if config/base_deployment.json already
exists, unless --force.

Run: python scripts/deploy_contract.py [--force]
"""

from __future__ import annotations

import argparse
import sys

from finne.base.adapter import deploy_contract


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="Redeploy even if config/base_deployment.json already exists."
    )
    args = parser.parse_args()
    try:
        deployment = deploy_contract(force=args.force)
    except Exception as exc:
        print(f"Deployment failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Deployed at: {deployment['contract_address']}")
    print(f"Chain ID: {deployment['chain_id']}")
    print(f"Deployment transaction: {deployment['deployment_tx_hash']}")


if __name__ == "__main__":
    main()
