"""Shared configuration for the demo scripts (scripts/reset_demo.py,
session1.py, session2.py) and their tests.

DEMO_TENANT_ID is a fixed, dedicated tenant for the Finné Memory demo —
isolated, via Sibyl Memory's own tenant scoping (verified in seam (b)),
from any other tenant that might share the same underlying database
file. It is not a secret; it is a namespace, chosen once and kept
stable so the demo is reproducible.
"""

from __future__ import annotations

DEMO_TENANT_ID = "f1442e00-0000-4000-8000-000000000001"

# The two facts the corpus's live-created cases share with every seeded
# fixture (ACTIVE_DEMO_DESIGN.md section 5), used by the session scripts
# to construct CASE-001 / CASE-002's proposals.
DEMO_NETWORK = "base"
DEMO_ASSET = "USDC"
DEMO_ACTION_CLASS = "capital_deployment"
DEMO_TARGET_CLASS = "yield_vault_conservative"
DEMO_FUNCTION = "deposit"
