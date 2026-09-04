"""Owner-policy loading.

Read-only. No function in this module, or anywhere in this repository,
writes back to config/owner_policy.toml — the agent cannot rewrite its
own authority policy.
"""

from __future__ import annotations

import tomllib
from decimal import Decimal
from pathlib import Path

from finne.models import HardPolicy, OwnerPolicy, ValidationError

DEFAULT_POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "owner_policy.toml"


def _decimal_from_toml_string(field_name: str, raw_value: object) -> Decimal:
    """Convert a TOML value to Decimal, requiring it to already be a
    string in the source file.

    An unquoted TOML number (e.g. `max_amount = 0.1`) parses as a native
    Python `float`. `Decimal(float)` does not reject that — it silently
    expands the float's exact binary value into a long, imprecise Decimal
    (`Decimal(0.1)` == `Decimal('0.1000000000000000055511151231257827...')`),
    which passes every finiteness check downstream while corrupting the
    configured value. Requiring a quoted string in the TOML source is what
    actually enforces the Decimal-only boundary at its origin, not just at
    the dataclass layer.
    """
    if not isinstance(raw_value, str):
        raise ValidationError(
            f"owner_policy.toml field {field_name!r} must be a quoted string "
            f"(e.g. \"25000.00\"), got unquoted {type(raw_value).__name__} "
            f"{raw_value!r}. Unquoted TOML numbers parse as float and silently "
            f"corrupt precision when converted to Decimal."
        )
    return Decimal(raw_value)


def load_owner_policy(path: str | Path = DEFAULT_POLICY_PATH) -> OwnerPolicy:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    section = data["owner_policy"]
    return OwnerPolicy(
        max_amount=_decimal_from_toml_string("max_amount", section["max_amount"]),
        network=section["network"],
        asset=section["asset"],
        action_class=section["action_class"],
        approved_target_classes=tuple(section["approved_target_classes"]),
        approved_functions=tuple(section["approved_functions"]),
        unknown_situation_behaviour=section["unknown_situation_behaviour"],
        cold_start_autonomous_amount=_decimal_from_toml_string(
            "cold_start_autonomous_amount", section["cold_start_autonomous_amount"]
        ),
    )


def default_hard_policy() -> HardPolicy:
    """No V1 scenario requires an active temporary override beyond the
    owner policy file; see the design note in
    prompts/2026-09-03-task-001-and-seam-a-kickoff.md. Returns a no-op
    HardPolicy so the five-way intersection stays real without inventing
    undescribed product behavior."""
    return HardPolicy(max_amount_override=None)
