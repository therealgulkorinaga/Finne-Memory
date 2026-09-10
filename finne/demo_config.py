"""Shared configuration for the demo scripts (scripts/reset_demo.py,
session1.py, session2.py) and their tests.

DEMO_TENANT_ID is a fixed, dedicated tenant for the Finné Memory demo —
isolated, via Sibyl Memory's own tenant scoping (verified in seam (b)),
from any other tenant that might share the same underlying database
file. It is not a secret; it is a namespace, chosen once and kept
stable so the demo is reproducible.
"""

from __future__ import annotations

from decimal import Decimal

DEMO_TENANT_ID = "f1442e00-0000-4000-8000-000000000001"

# The two facts the corpus's live-created cases share with every seeded
# fixture (ACTIVE_DEMO_DESIGN.md section 5), used by the session scripts
# to construct CASE-001 / CASE-002's proposals.
DEMO_NETWORK = "base"
DEMO_ASSET = "USDC"
DEMO_ACTION_CLASS = "capital_deployment"
DEMO_TARGET_CLASS = "yield_vault_conservative"
DEMO_FUNCTION = "deposit"

# --- the proposing agent's view of the world (SPEC-002) ----------------
#
# DEMO_AVAILABLE_CAPITAL is the treasury the agent has idle. It is NOT
# the owner ceiling: the ceiling lives in config/owner_policy.toml and
# the agent never sees it. The two happen to be equal in this corpus,
# which makes the demonstration clean — the agent proposes to deploy
# everything it has, and Finné Memory holds that it has earned less —
# but they are independent values read from independent places, and
# SPEC-002 invariant 11 plus tests/test_import_boundaries.py enforce
# that the agent cannot reach the policy at all.
DEMO_AVAILABLE_CAPITAL = Decimal("25000.00")

DEMO_OPPORTUNITY = (
    "A conservative single-asset USDC yield vault on Base, audited, with "
    "a multi-year track record and deep liquidity. Deposits are withdrawable "
    "on demand with no lockup. You hold idle treasury that is currently "
    "earning nothing."
)
