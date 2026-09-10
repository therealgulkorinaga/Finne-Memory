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

# The fact profile the corpus's live-created cases share with the seeded
# fixtures (ACTIVE_DEMO_DESIGN.md section 5). A residential buildings
# claim for sudden escape of water, assessed in-panel, where the handler
# is deciding whether to settle.
DEMO_NETWORK = "uk_retail_direct"
DEMO_ASSET = "GBP"
DEMO_ACTION_CLASS = "claim_assessment"
DEMO_TARGET_CLASS = "escape_of_water_sudden"
DEMO_FUNCTION = "approve_settlement"

# --- what the assessing agent is shown (SPEC-002) ---------------------
#
# DEMO_ASSESSED_VALUE is the loss adjuster's figure for this claim. It is
# NOT the handler's delegated settlement ceiling: the ceiling lives in
# config/owner_policy.toml and the agent never sees it. The two happen to
# be equal in this corpus, which makes the demonstration clean — the
# adjuster values the loss at the top of what the handler could in
# principle authorise — but they are independent values read from
# independent places, and SPEC-002 invariant 11 plus
# tests/test_import_boundaries.py enforce that the agent cannot reach the
# policy at all.
DEMO_ASSESSED_VALUE = Decimal("25000.00")

DEMO_CASE_SUMMARY = (
    "Residential buildings claim, in-panel. Escape of water. The "
    "policyholder reported a burst pipe under the kitchen floor overnight; "
    "the plumber's report records an abrupt rupture at a compression joint "
    "and no evidence of pre-existing corrosion. Loss adjuster has inspected "
    "and valued the reinstatement work. Policy wording covers sudden and "
    "accidental escape of water and excludes damage from gradual leakage. "
    "No prior claims on this policy."
)
