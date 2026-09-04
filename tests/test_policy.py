"""Tests for owner-policy loading.

Found by Codex review (second pass): unquoted TOML numeric literals parse
as native `float`, which `Decimal()` silently accepts and expands into a
binary-approximation Decimal rather than rejecting — bypassing the
Decimal-only boundary at its source, before any dataclass validation
runs.
"""

from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from finne.models import ValidationError
from finne.policy import DEFAULT_POLICY_PATH, load_owner_policy

VALID_TOML = """
[owner_policy]
max_amount = "25000.00"
network = "base"
asset = "USDC"
action_class = "capital_deployment"
approved_target_classes = ["demo_receipt", "yield_vault_conservative"]
approved_functions = ["recordAuthorization", "deposit"]
unknown_situation_behaviour = "escalate_to_owner"
cold_start_autonomous_amount = "0.00"
"""

UNQUOTED_NUMBER_TOML = VALID_TOML.replace('max_amount = "25000.00"', "max_amount = 25000.00")


def _write_and_load(toml_text: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False
    ) as f:
        f.write(toml_text)
        path = Path(f.name)
    try:
        return load_owner_policy(path)
    finally:
        path.unlink()


def test_real_config_file_loads_with_exact_decimal_values():
    policy = load_owner_policy(DEFAULT_POLICY_PATH)
    assert policy.max_amount == Decimal("25000.00")
    assert policy.cold_start_autonomous_amount == Decimal("0.00")
    assert "yield_vault_aggressive" not in policy.approved_target_classes


def test_quoted_string_amounts_load_as_exact_decimal():
    policy = _write_and_load(VALID_TOML)
    assert policy.max_amount == Decimal("25000.00")
    assert isinstance(policy.max_amount, Decimal)


def test_unquoted_numeric_max_amount_is_rejected():
    """The exact regression this test guards against: max_amount = 0.1
    (unquoted) previously loaded as Decimal('0.100000000000000005551...')
    instead of being rejected."""
    with pytest.raises(ValidationError):
        _write_and_load(UNQUOTED_NUMBER_TOML)


def test_unquoted_cold_start_amount_is_rejected():
    bad_toml = VALID_TOML.replace(
        'cold_start_autonomous_amount = "0.00"', "cold_start_autonomous_amount = 0.00"
    )
    with pytest.raises(ValidationError):
        _write_and_load(bad_toml)
