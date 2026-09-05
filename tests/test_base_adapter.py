"""Tests for finne/base/adapter.py — the real web3.py implementation.

Per PREREQ-003 section 14: mocked revert, timeout, and duplicate
submission produce no false success, plus opt-in live tests gated by
FINNE_LIVE_BASE_TEST=1 (four of them, as of seam (d) round 5 — the
module docstring previously said "one", written before the later ones
were added). The mocked tests patch finne.base.adapter._connect
with lightweight fakes standing in for exactly the Web3/Contract/Account
surface the adapter actually calls — not a general-purpose web3.py test
double — so every scenario (revert, timeout, duplicate, read failure,
connection failure, success) is deterministic, instant, and has no real
network dependency. This is deliberate: test_fresh_session.py already
proved (the hard way — see its own module docstring) that letting an
automated test reach the real adapter fires genuine transactions at
live infrastructure.

Covers: A4, A5, A11 (live test only), A12, A13, invariant 10.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from decimal import Decimal

import pytest

import finne.base.adapter as adapter
from finne.base.adapter import (
    BaseExecutionResult,
    _authorized_amount_units,
    _decision_id,
    _facts_hash,
    get_receipt,
    reconcile_pending,
    record_authorization,
)
from finne.models import AuthorizationDecision, AuthorizationResult, Proposal, RiskTier


def _decision(authorized_amount: str, *, cited: tuple[str, ...] = ()) -> AuthorizationDecision:
    amount = Decimal(authorized_amount)
    return AuthorizationDecision(
        result=AuthorizationResult.CONSTRAIN if amount > 0 else AuthorizationResult.ESCALATE,
        authorized_amount=amount,
        binding_constraint="learned_constraint",
        cited_precedents=cited,
        material_differences=(),
        explanation="test decision",
    )


def _proposal(**overrides) -> Proposal:
    fields = dict(
        network="base",
        asset="USDC",
        action_class="capital_deployment",
        target_class="yield_vault_conservative",
        function="deposit",
        counterparty_risk_tier=RiskTier.LOW,
        amount=Decimal("25000.00"),
        proposed_at="2026-09-01T00:00:00Z",
    )
    fields.update(overrides)
    return Proposal(**fields)


# --- lightweight fakes for exactly the web3.py surface the adapter calls ---


class _FakeCall:
    def __init__(self, result=None, raises=None):
        self._result = result
        self._raises = raises

    def call(self):
        if self._raises:
            raise self._raises
        return self._result


class _FakeBuildableFn:
    def __init__(self, captured_tx=None):
        self._captured_tx = captured_tx

    def build_transaction(self, overrides):
        tx = dict(overrides)
        if self._captured_tx is not None:
            self._captured_tx.update(tx)
        return tx


class _FakeFunctions:
    def __init__(
        self,
        *,
        recorded_result=False,
        recorded_raises=None,
        captured_amount=None,
        captured_tx=None,
        receipt_submitted_by="0x000000000000000000000000000000000000dEaD",
    ):
        self._recorded_result = recorded_result
        self._recorded_raises = recorded_raises
        self._captured_amount = captured_amount
        self._captured_tx = captured_tx
        self._receipt_submitted_by = receipt_submitted_by

    def recorded(self, _decision_id_bytes):
        return _FakeCall(self._recorded_result, raises=self._recorded_raises)

    def recordAuthorization(self, _decision_id_bytes, amount, _facts_hash_bytes):
        if self._captured_amount is not None:
            self._captured_amount["value"] = amount
        return _FakeBuildableFn(self._captured_tx)

    def getReceipt(self, _decision_id_bytes):
        # (authorizedAmount, factsHash, submittedBy, recordedAt) — matches
        # _FakeAccount.address by default, so provenance verification in
        # get_receipt() passes for every test that isn't specifically
        # checking the mismatch-rejection path.
        return _FakeCall((0, b"\x00" * 32, self._receipt_submitted_by, 0))


class _FakeEventQuery:
    """Genuinely range-aware, unlike a fake that ignores its own
    from_block/to_block and always returns the same fixed list —
    IMPORTANT finding: that oversimplification meant _find_transaction_hash's
    chunked backward scan was never actually exercised by the mocked
    tests, only ever succeeding trivially on the first chunk or failing
    on every chunk. log_block=None preserves that simple, always-in-range
    behavior for tests that don't care about chunk placement; a real
    log_block value makes get_logs only return the log when the queried
    range actually contains it, so chunk traversal itself is tested."""

    def __init__(self, logs, *, log_block=None, raises_for_to_block=frozenset()):
        self._logs = logs
        self._log_block = log_block
        self._raises_for_to_block = raises_for_to_block

    def get_logs(self, *, argument_filters, from_block, to_block):
        if to_block in self._raises_for_to_block:
            raise RuntimeError(f"RPC error for chunk ending at {to_block}")
        if not self._logs:
            return []
        if self._log_block is None:
            return self._logs
        if from_block <= self._log_block <= to_block:
            return self._logs
        return []

    def __call__(self):
        # contract.events.AuthorizationRecorded() — used by
        # reconcile_pending's process_log path, distinct from get_logs.
        return self

    def process_log(self, log):
        # In these tests a "log" is already a plain dict shaped like
        # {"decisionId": <bytes32>} — decoded the way a real event's
        # .args would expose it.
        if log.get("_undecodable"):
            raise ValueError("cannot decode this log as AuthorizationRecorded")
        return {"args": {"decisionId": log["decisionId"]}}


class _FakeEvents:
    def __init__(self, logs, *, log_block=None, raises_for_to_block=frozenset()):
        self.AuthorizationRecorded = _FakeEventQuery(
            logs, log_block=log_block, raises_for_to_block=raises_for_to_block
        )


class _FakeContract:
    def __init__(
        self,
        *,
        recorded_result=False,
        recorded_raises=None,
        logs=(),
        log_block=None,
        raises_for_to_block=frozenset(),
        captured_amount=None,
        captured_tx=None,
        receipt_submitted_by="0x000000000000000000000000000000000000dEaD",
        decoded_fn_name="recordAuthorization",
        decoded_decision_id=None,
        decode_raises=None,
    ):
        self.functions = _FakeFunctions(
            recorded_result=recorded_result,
            recorded_raises=recorded_raises,
            captured_amount=captured_amount,
            captured_tx=captured_tx,
            receipt_submitted_by=receipt_submitted_by,
        )
        self.events = _FakeEvents(list(logs), log_block=log_block, raises_for_to_block=raises_for_to_block)
        self._decoded_fn_name = decoded_fn_name
        self._decoded_decision_id = decoded_decision_id
        self._decode_raises = decode_raises

    def decode_function_input(self, _calldata):
        # reconcile_pending binds a transaction to a decision from its
        # own calldata — which works for REVERTED transactions too,
        # where no event was ever emitted.
        if self._decode_raises:
            raise self._decode_raises
        return _FakeDecodedFn(self._decoded_fn_name), {"decisionId": self._decoded_decision_id}


class _FakeTxHash:
    def __init__(self, value):
        self._value = value

    def to_0x_hex(self):
        return self._value


class _FakeReceipt:
    def __init__(self, status, block_number=100):
        self.status = status
        self.blockNumber = block_number


class _FakeEth:
    def __init__(
        self,
        *,
        send_result="0xsenttxhash",
        send_raises=None,
        receipt=None,
        receipt_raises=None,
        block_number=1000,
        get_receipt_result=None,
        get_receipt_raises=None,
        get_transaction_result=None,
        get_transaction_raises=None,
    ):
        self.max_priority_fee = 1
        self.chain_id = 84532
        self.block_number = block_number
        self._send_result = send_result
        self._send_raises = send_raises
        self._receipt = receipt
        self._receipt_raises = receipt_raises
        self._get_receipt_result = get_receipt_result
        self._get_receipt_raises = get_receipt_raises
        self._get_transaction_result = get_transaction_result
        self._get_transaction_raises = get_transaction_raises

    def get_transaction_count(self, _address):
        return 0

    def get_block(self, _tag):
        return {"baseFeePerGas": 5}

    def estimate_gas(self, _tx):
        return 100_000

    def send_raw_transaction(self, _raw):
        if self._send_raises:
            raise self._send_raises
        return _FakeTxHash(self._send_result)

    def wait_for_transaction_receipt(self, _tx_hash, timeout):
        if self._receipt_raises:
            raise self._receipt_raises
        return self._receipt

    def get_transaction_receipt(self, _tx_hash):
        if self._get_receipt_raises:
            raise self._get_receipt_raises
        return self._get_receipt_result

    def get_transaction(self, _tx_hash):
        if self._get_transaction_raises:
            raise self._get_transaction_raises
        return self._get_transaction_result


class _FakeFullReceipt:
    def __init__(self, *, status, to=None, logs=()):
        self.status = status
        self.to = to
        self.logs = list(logs)


class _FakeDecodedFn:
    def __init__(self, fn_name):
        self.fn_name = fn_name


class _FakeW3:
    def __init__(self, eth):
        self.eth = eth


class _FakeSignedTx:
    raw_transaction = b"\x00"
    # record_authorization now computes the transaction hash locally
    # from the signed transaction BEFORE broadcasting, so an ambiguous
    # send failure still yields a reconcilable hash.
    hash = b"\xab\xc1" + b"\x00" * 30


class _FakeAccount:
    address = "0x000000000000000000000000000000000000dEaD"

    def __init__(self, sign_raises=None):
        self._sign_raises = sign_raises

    def sign_transaction(self, _tx):
        if self._sign_raises:
            raise self._sign_raises
        return _FakeSignedTx()


_FAKE_CONTRACT_ADDRESS = "0x00000000000000000000000000000000C0FFEE"
# Web3.to_hex(_FakeSignedTx.hash) — record_authorization now derives the
# transaction hash locally from the signed transaction rather than from
# send_raw_transaction's return value.
_LOCAL_TX_HASH = "0xabc1" + "00" * 30


def _patch_connect(monkeypatch, *, contract, eth=None, connect_raises=None, deployment_block=0):
    def fake_connect():
        if connect_raises:
            raise connect_raises
        return (
            _FakeW3(eth or _FakeEth()),
            contract,
            _FakeAccount(),
            {"deployment_block": deployment_block, "contract_address": _FAKE_CONTRACT_ADDRESS},
        )

    monkeypatch.setattr(adapter, "_connect", fake_connect)


def _refuse_connect(monkeypatch):
    def fail_if_called():
        raise AssertionError("must not connect for this scenario")

    monkeypatch.setattr(adapter, "_connect", fail_if_called)


# --- BaseExecutionResult's own coherence contract ---


def test_result_rejects_non_bool_attempted():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted="yes", success=False, outcome_confirmed=True, tx_hash=None, detail="x")


def test_result_rejects_non_bool_success():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success="yes", outcome_confirmed=True, tx_hash="0xabc", detail="x")


def test_result_rejects_non_bool_outcome_confirmed():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success=False, outcome_confirmed="yes", tx_hash="0xabc", detail="x")


def test_result_rejects_non_str_tx_hash():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success=True, outcome_confirmed=True, tx_hash=123, detail="x")


def test_result_rejects_unattempted_success():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=False, success=True, outcome_confirmed=True, tx_hash=None, detail="x")


def test_result_rejects_unattempted_with_tx_hash():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=False, success=False, outcome_confirmed=True, tx_hash="0xabc", detail="x")


def test_result_rejects_unattempted_with_unconfirmed_outcome():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=False, success=False, outcome_confirmed=False, tx_hash=None, detail="x")


def test_result_rejects_success_without_tx_hash():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success=True, outcome_confirmed=True, tx_hash=None, detail="x")


def test_result_rejects_success_with_empty_tx_hash():
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success=True, outcome_confirmed=True, tx_hash="", detail="x")


def test_result_rejects_success_with_unconfirmed_outcome():
    # The BLOCKER this type change fixes: a timed-out receipt wait must
    # never be representable as success, since the outcome isn't known.
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success=True, outcome_confirmed=False, tx_hash="0xabc", detail="x")


def test_result_rejects_attempted_unconfirmed_without_tx_hash():
    # IMPORTANT (independent review): this exact shape previously
    # constructed without error — an "unconfirmed" outcome with no
    # transaction hash at all is incoherent: there is nothing
    # "unconfirmed" about a broadcast that never happened.
    with pytest.raises(ValueError):
        BaseExecutionResult(attempted=True, success=False, outcome_confirmed=False, tx_hash=None, detail="x")


def test_result_allows_every_coherent_shape():
    BaseExecutionResult(attempted=False, success=False, outcome_confirmed=True, tx_hash=None, detail="x")
    BaseExecutionResult(attempted=True, success=True, outcome_confirmed=True, tx_hash="0xabc", detail="x")
    BaseExecutionResult(attempted=True, success=False, outcome_confirmed=True, tx_hash=None, detail="x")
    BaseExecutionResult(attempted=True, success=False, outcome_confirmed=True, tx_hash="0xabc", detail="x")
    BaseExecutionResult(attempted=True, success=False, outcome_confirmed=False, tx_hash="0xabc", detail="x")


# --- pure helpers: decisionId, factsHash, amount conversion ---


def test_decision_id_is_deterministic_and_distinguishes_inputs():
    assert _decision_id("DV-001-V1") == _decision_id("DV-001-V1")
    assert _decision_id("DV-001-V1") != _decision_id("DV-002-V1")


def test_facts_hash_is_deterministic_and_sensitive_to_material_facts():
    decision = _decision("10000.00", cited=("DV-001-V1",))
    proposal = _proposal()
    assert _facts_hash(proposal, decision) == _facts_hash(proposal, decision)

    different_network = _proposal(network="ethereum")
    assert _facts_hash(different_network, decision) != _facts_hash(proposal, decision)

    different_citation = _decision("10000.00", cited=("DV-999-V1",))
    assert _facts_hash(proposal, different_citation) != _facts_hash(proposal, decision)


def test_authorized_amount_units_converts_to_six_decimals():
    assert _authorized_amount_units(Decimal("10000.00")) == 10_000_000_000
    assert _authorized_amount_units(Decimal("0.01")) == 10_000
    assert _authorized_amount_units(Decimal("25000.00")) == 25_000_000_000


def test_authorized_amount_units_rejects_amounts_finer_than_six_decimals():
    # BLOCKER: the previous implementation used ROUND_HALF_UP, which
    # rounds e.g. 10000.0000006 up to onchain units representing
    # 10000.000001 — a higher amount than was actually authorized.
    # Reproduced directly before fixing; now must raise, never round.
    with pytest.raises(ValueError):
        _authorized_amount_units(Decimal("10000.0000006"))


# --- record_authorization ---


def test_refuses_when_decision_authorizes_nothing(monkeypatch):
    # PREREQ-003 section 9: refuses to submit anything the decision did
    # not authorize. No connection is even attempted.
    _refuse_connect(monkeypatch)
    result = record_authorization(_decision("0.00"), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (False, False, None)


def test_refuses_amount_not_exactly_representable_before_connecting(monkeypatch):
    # BLOCKER: refuses cleanly (no connection attempted, no exception
    # escapes) rather than rounding or crashing.
    _refuse_connect(monkeypatch)
    result = record_authorization(_decision("10000.0000006"), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (False, False, None)
    assert "not exactly representable" in result.detail


def test_dry_run_skips_everything(monkeypatch):
    monkeypatch.setenv("FINNE_BASE_DRY_RUN", "1")
    _refuse_connect(monkeypatch)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (False, False, None)


def test_connection_failure_is_unattempted_not_a_false_failure(monkeypatch):
    _patch_connect(monkeypatch, contract=_FakeContract(), connect_raises=RuntimeError("no RPC"))
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (False, False, None)


def test_read_failure_before_submitting_is_unattempted(monkeypatch):
    contract = _FakeContract(recorded_raises=RuntimeError("RPC error reading state"))
    _patch_connect(monkeypatch, contract=contract)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (False, False, None)


def test_refuses_duplicate_without_submitting(monkeypatch):
    # NEG-08, application-level half: the contract's own recorded()
    # state is checked before ever attempting to submit.
    contract = _FakeContract(recorded_result=True)
    _patch_connect(monkeypatch, contract=contract)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (False, False, None)
    assert "already recorded" in result.detail
    assert "duplicate" in result.detail.lower()


def test_successful_submission(monkeypatch):
    contract = _FakeContract(recorded_result=False)
    eth = _FakeEth(receipt=_FakeReceipt(status=1))
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    result = record_authorization(_decision("10000.00", cited=("DV-001-V1",)), _proposal(), "DV-TEST")
    assert (result.attempted, result.success, result.tx_hash) == (True, True, _LOCAL_TX_HASH)


def test_revert_produces_no_false_success(monkeypatch):
    # NEG-07/A12: a mocked revert must never be reported as success.
    contract = _FakeContract(recorded_result=False)
    eth = _FakeEth(receipt=_FakeReceipt(status=0))
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert result.attempted is True
    assert result.success is False
    # Real, non-fabricated reference to the reverted tx — computed
    # locally from the signed transaction, not returned by the node.
    assert result.tx_hash == _LOCAL_TX_HASH
    assert "reverted" in result.detail.lower()


def test_timeout_is_unconfirmed_not_a_false_success_or_false_failure(monkeypatch):
    # BLOCKER: a receipt timeout must be neither a false success (the
    # original NEG-07 concern) nor a false CONFIRMED failure (the
    # independent-review finding: writing immutable Outcome.FAILURE for
    # a transaction that might still land and succeed permanently
    # misrepresents an unknown outcome as a known one).
    contract = _FakeContract(recorded_result=False)
    eth = _FakeEth(receipt_raises=TimeoutError("no receipt in time"))
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert result.attempted is True
    assert result.success is False
    assert result.outcome_confirmed is False
    assert result.tx_hash == _LOCAL_TX_HASH


def test_ambiguous_broadcast_failure_is_unconfirmed_and_reconcilable(monkeypatch):
    # DEAL-BREAKER (round 5): every send_raw_transaction exception was
    # previously classified as a confirmed pre-broadcast rejection. A
    # transport-level failure can occur AFTER the node accepted the
    # transaction, so the sessions would have written an immutable
    # Outcome.FAILURE for something that may still succeed — the same
    # write-once hazard `outcome_confirmed` exists to prevent, just at
    # the broadcast boundary. Must now be unconfirmed AND carry the
    # locally-computed hash so it can actually be reconciled.
    contract = _FakeContract(recorded_result=False)
    eth = _FakeEth(send_raises=RuntimeError("connection reset by peer"))
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert result.attempted is True
    assert result.success is False
    assert result.outcome_confirmed is False
    assert result.tx_hash == _LOCAL_TX_HASH


def test_pre_broadcast_signing_failure_is_a_confirmed_failure(monkeypatch):
    # Everything up to and including signing is genuinely pre-broadcast
    # — nothing can be pending, so this IS confirmed, and there is no
    # meaningful hash to reconcile against.
    contract = _FakeContract(recorded_result=False)

    def fake_connect():
        return (
            _FakeW3(_FakeEth()),
            contract,
            _FakeAccount(sign_raises=RuntimeError("nonce too low")),
            {"deployment_block": 0, "contract_address": _FAKE_CONTRACT_ADDRESS},
        )

    monkeypatch.setattr(adapter, "_connect", fake_connect)
    result = record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert result.attempted is True
    assert result.success is False
    assert result.outcome_confirmed is True
    assert result.tx_hash is None


def test_transaction_never_carries_value(monkeypatch):
    # Invariant 10: every demonstration transaction carries zero value.
    captured_tx = {}
    contract = _FakeContract(recorded_result=False, captured_tx=captured_tx)
    eth = _FakeEth(receipt=_FakeReceipt(status=1))
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert captured_tx.get("value", 0) == 0


def test_authorized_amount_submitted_in_six_decimal_units(monkeypatch):
    captured_amount = {}
    contract = _FakeContract(recorded_result=False, captured_amount=captured_amount)
    eth = _FakeEth(receipt=_FakeReceipt(status=1))
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    record_authorization(_decision("10000.00"), _proposal(), "DV-TEST")
    assert captured_amount["value"] == 10_000_000_000


# --- get_receipt ---


def test_get_receipt_dry_run_returns_none(monkeypatch):
    monkeypatch.setenv("FINNE_BASE_DRY_RUN", "1")
    _refuse_connect(monkeypatch)
    assert get_receipt("DV-TEST") is None


def test_get_receipt_returns_none_when_not_recorded(monkeypatch):
    _patch_connect(monkeypatch, contract=_FakeContract(recorded_result=False))
    assert get_receipt("DV-TEST") is None


def test_get_receipt_returns_none_on_connection_failure(monkeypatch):
    _patch_connect(monkeypatch, contract=_FakeContract(), connect_raises=RuntimeError("no RPC"))
    assert get_receipt("DV-TEST") is None


def test_get_receipt_reconstructs_tx_hash_from_event_log(monkeypatch):
    logs = [{"transactionHash": _FakeTxHash("0xreal")}]
    _patch_connect(monkeypatch, contract=_FakeContract(recorded_result=True, logs=logs))
    result = get_receipt("DV-TEST")
    assert result is not None
    assert (result.attempted, result.success, result.tx_hash) == (True, True, "0xreal")


def test_get_receipt_returns_none_if_recorded_but_no_log_found(monkeypatch):
    # Defensive: recorded=True but no matching log is treated as
    # absent, never fabricated as a success with an invented hash.
    _patch_connect(monkeypatch, contract=_FakeContract(recorded_result=True, logs=[]))
    assert get_receipt("DV-TEST") is None


def test_get_receipt_rejects_provenance_mismatch(monkeypatch):
    # BLOCKER: recorded=True with a real log is not sufficient on its
    # own — a receipt whose submittedBy doesn't match this wallet must
    # never be trusted as this project's own evidence, even though the
    # contract's own authorizedSigner restriction should make this
    # unreachable in practice (defense in depth for a differently-
    # configured or older deployment).
    logs = [{"transactionHash": _FakeTxHash("0xreal")}]
    contract = _FakeContract(
        recorded_result=True,
        logs=logs,
        receipt_submitted_by="0x000000000000000000000000000000000BAD1",
    )
    _patch_connect(monkeypatch, contract=contract)
    assert get_receipt("DV-TEST") is None


# --- _find_transaction_hash's chunked backward scan ---
#
# IMPORTANT (independent review): the tests above use a range-blind
# fake, so they only ever exercise "found on the very first chunk" or
# "never found" — they never actually exercise chunk traversal itself.
# These tests use _FakeEventQuery's log_block parameter to place a log
# at a specific block, so the scan genuinely has to walk backward
# through multiple chunks to find (or fail to find) it.

_log = [{"transactionHash": _FakeTxHash("0xchunked")}]


def test_find_transaction_hash_finds_log_in_first_chunk():
    contract = _FakeContract(logs=_log, log_block=9_999)
    result = adapter._find_transaction_hash(contract, b"\x00" * 32, deployment_block=0, latest_block=10_000)
    assert result == "0xchunked"


def test_find_transaction_hash_finds_log_in_middle_chunk():
    contract = _FakeContract(logs=_log, log_block=5_000)
    result = adapter._find_transaction_hash(contract, b"\x00" * 32, deployment_block=0, latest_block=10_000)
    assert result == "0xchunked"


def test_find_transaction_hash_finds_log_at_deployment_block_boundary():
    contract = _FakeContract(logs=_log, log_block=0)
    result = adapter._find_transaction_hash(contract, b"\x00" * 32, deployment_block=0, latest_block=10_000)
    assert result == "0xchunked"


def test_find_transaction_hash_exhausts_scan_and_returns_none():
    # No log anywhere in range — must terminate (not loop forever) and
    # return None rather than raise or hang.
    contract = _FakeContract(logs=[], log_block=None)
    result = adapter._find_transaction_hash(contract, b"\x00" * 32, deployment_block=0, latest_block=10_000_000)
    assert result is None


def test_find_transaction_hash_returns_none_on_mid_scan_rpc_failure():
    # A chunk partway through the scan raises — must return None
    # (query failure is not evidence of absence, but this function has
    # no way to distinguish the two), not propagate the exception or
    # skip past the failure and report a false negative as if it were
    # a clean "not found."
    contract = _FakeContract(logs=_log, log_block=0, raises_for_to_block={6_000})
    result = adapter._find_transaction_hash(contract, b"\x00" * 32, deployment_block=0, latest_block=10_000)
    assert result is None


# --- reconcile_pending ---
#
# DEAL-BREAKER (round 5): reconcile_pending returned
# `success=False, outcome_confirmed=True` for an unrelated/mismatched
# transaction, which scripts/reconcile_outcome.py correctly read as
# "confirmed execution failure" and persisted as an immutable
# Outcome.FAILURE — reproduced end to end, fabricating a `failure` for
# a decision that transaction never represented. Mismatches now raise
# ReconciliationMismatch instead, so no caller can conflate "wrong
# transaction" with "the decision failed".
#
# Binding is verified from the transaction's own CALLDATA (sender,
# recipient, function, decisionId) rather than event logs, because a
# REVERTED transaction emits no events at all — the earlier version
# checked only the recipient for the revert path, so any reverted
# transaction to the contract could be attached as failure evidence
# for any decision.

_MATCHING_TX = {"to": _FAKE_CONTRACT_ADDRESS, "from": _FakeAccount.address, "input": b"\x00"}


def _reconcile_contract(decision_version_id="DV-TEST", **overrides):
    return _FakeContract(decoded_decision_id=_decision_id(decision_version_id), **overrides)


def test_reconcile_pending_unknown_transaction_is_unconfirmed(monkeypatch):
    from web3.exceptions import TransactionNotFound

    eth = _FakeEth(get_transaction_raises=TransactionNotFound("nope"))
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    result = reconcile_pending("DV-TEST", "0xabc")
    assert (result.attempted, result.success, result.outcome_confirmed) == (True, False, False)


def test_reconcile_pending_malformed_hash_raises_mismatch(monkeypatch):
    eth = _FakeEth(get_transaction_raises=ValueError("must be a hex string"))
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    with pytest.raises(adapter.ReconciliationMismatch):
        reconcile_pending("DV-TEST", "not-a-hash")


def test_reconcile_pending_raises_for_transaction_to_a_different_contract(monkeypatch):
    tx = {**_MATCHING_TX, "to": "0x000000000000000000000000000000DeadBeef"}
    eth = _FakeEth(get_transaction_result=tx)
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    with pytest.raises(adapter.ReconciliationMismatch, match="did not target"):
        reconcile_pending("DV-TEST", "0xabc")


def test_reconcile_pending_raises_for_transaction_from_a_different_sender(monkeypatch):
    tx = {**_MATCHING_TX, "from": "0x000000000000000000000000000000000BAD1"}
    eth = _FakeEth(get_transaction_result=tx)
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    with pytest.raises(adapter.ReconciliationMismatch, match="not sent by this wallet"):
        reconcile_pending("DV-TEST", "0xabc")


def test_reconcile_pending_raises_for_a_different_function(monkeypatch):
    eth = _FakeEth(get_transaction_result=_MATCHING_TX)
    contract = _reconcile_contract(decoded_fn_name="someOtherFunction")
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    with pytest.raises(adapter.ReconciliationMismatch, match="not recordAuthorization"):
        reconcile_pending("DV-TEST", "0xabc")


def test_reconcile_pending_raises_for_a_different_decision(monkeypatch):
    # The exact operator-typo scenario: a real, valid transaction of
    # ours, but for a DIFFERENT decision than the one being reconciled.
    eth = _FakeEth(get_transaction_result=_MATCHING_TX)
    contract = _reconcile_contract("DV-SOME-OTHER-CASE")
    _patch_connect(monkeypatch, contract=contract, eth=eth)
    with pytest.raises(adapter.ReconciliationMismatch, match="different decision"):
        reconcile_pending("DV-TEST", "0xabc")


def test_reconcile_pending_broadcast_but_unmined_is_unconfirmed(monkeypatch):
    from web3.exceptions import TransactionNotFound

    eth = _FakeEth(get_transaction_result=_MATCHING_TX, get_receipt_raises=TransactionNotFound("no receipt"))
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    result = reconcile_pending("DV-TEST", "0xabc")
    assert (result.attempted, result.success, result.outcome_confirmed) == (True, False, False)


def test_reconcile_pending_confirms_revert_only_after_binding(monkeypatch):
    # A revert emits no events, so this can only be confirmed via
    # calldata binding — which the checks above establish.
    eth = _FakeEth(
        get_transaction_result=_MATCHING_TX,
        get_receipt_result=_FakeFullReceipt(status=0, to=_FAKE_CONTRACT_ADDRESS),
    )
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    result = reconcile_pending("DV-TEST", "0xabc")
    assert (result.attempted, result.success, result.outcome_confirmed) == (True, False, True)
    assert "reverted" in result.detail


def test_reconcile_pending_confirms_success(monkeypatch):
    eth = _FakeEth(
        get_transaction_result=_MATCHING_TX,
        get_receipt_result=_FakeFullReceipt(status=1, to=_FAKE_CONTRACT_ADDRESS),
    )
    _patch_connect(monkeypatch, contract=_reconcile_contract(), eth=eth)
    result = reconcile_pending("DV-TEST", "0xabc")
    assert (result.attempted, result.success, result.outcome_confirmed) == (True, True, True)
    assert result.tx_hash == "0xabc"


# --- opt-in live tests, gated per PREREQ-003 section 14 ---

_LIVE = pytest.mark.skipif(
    os.environ.get("FINNE_LIVE_BASE_TEST") != "1",
    reason="live test against real Base Sepolia infrastructure; set FINNE_LIVE_BASE_TEST=1 to run",
)


def _retry_until(fn, *, attempts=6, delay_seconds=3):
    """Polls fn() until it returns a truthy value or attempts run out.

    Needed only for these live tests: a freshly-confirmed transaction's
    own state can briefly read as stale on an immediately-following,
    separately-connected read — a real characteristic of public RPC
    read-replica propagation (confirmed by direct diagnostic during
    development: a fresh read showed False, then True three seconds
    later), not a defect in the adapter. record_authorization's own
    returned result is already authoritative from the connection that
    submitted it; this tolerance is for the TEST's own separate
    verification reads only."""
    import time

    result = None
    for _ in range(attempts):
        result = fn()
        if result:
            return result
        time.sleep(delay_seconds)
    return result


@_LIVE
def test_live_record_and_read_back_a_real_receipt():
    """Submits a real, zero-value transaction to whatever contract
    config/base_deployment.json currently points at, using a freshly
    generated decision_version_id so this can never collide with a
    previous run's already-recorded state (A4, A11)."""
    decision_version_id = f"DV-LIVE-TEST-{uuid.uuid4()}"
    decision = _decision("1.00", cited=("DV-001-V1",))
    proposal = _proposal()

    result = record_authorization(decision, proposal, decision_version_id)
    assert result.attempted is True
    assert result.success is True
    assert result.tx_hash is not None
    assert result.tx_hash.startswith("0x")

    receipt = _retry_until(lambda: get_receipt(decision_version_id))
    assert receipt is not None
    assert receipt.tx_hash == result.tx_hash


@_LIVE
def test_live_duplicate_rejected_at_contract_level_too():
    """A13: proves the CONTRACT's own require(!recorded[decisionId])
    rejects a duplicate, independent of the adapter's own application-
    level pre-check — by calling the contract directly a second time,
    bypassing record_authorization's own guard entirely."""
    from web3.exceptions import ContractLogicError

    decision_version_id = f"DV-LIVE-DUP-TEST-{uuid.uuid4()}"
    decision = _decision("1.00")
    proposal = _proposal()

    first = record_authorization(decision, proposal, decision_version_id)
    assert first.attempted is True and first.success is True

    w3, contract, account, _deployment = adapter._connect()
    decision_id = adapter._decision_id(decision_version_id)
    facts_hash = adapter._facts_hash(proposal, decision)
    amount_units = adapter._authorized_amount_units(decision.authorized_amount)

    # Wait for this specific connection's view of chain state to catch
    # up before asserting the duplicate is rejected — see _retry_until.
    _retry_until(lambda: contract.functions.recorded(decision_id).call())

    with pytest.raises(ContractLogicError):
        contract.functions.recordAuthorization(decision_id, amount_units, facts_hash).call(
            {"from": account.address}
        )


@_LIVE
def test_live_session1_then_session2_constrains_citing_precedent():
    """A4/A5, fully live — the gap independent review found: neither
    live test above actually runs session1.py/session2.py, only the
    adapter's own functions directly, so SPEC-001's assignment of A4/A5
    to this file was previously unearned. Redeploys a fresh contract
    (session1.py/session2.py use the fixed decision_version_id values
    DV-001-V1/DV-002-V1, which the contract's own duplicate protection
    means can only ever be used once per deployment — see BUILD_LOG.md
    for the same constraint discovered during seam (c)/(d) manual
    verification) and runs reset_demo.py -> session1.py -> session2.py
    as real subprocesses, no dry-run flag, against a fresh temporary
    Sibyl Memory database. Session 2 must constrain 25,000 to 10,000,
    citing DV-001-V1 by name, with its own real Base transaction."""
    import subprocess
    import tempfile

    from finne.base.adapter import deploy_contract

    deploy_contract(force=True)

    repo_root = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "live_e2e_test.db"

        def run(script, *args):
            return subprocess.run(
                [sys.executable, str(repo_root / "scripts" / script), "--db-path", str(db_path), *args],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

        reset = run("reset_demo.py")
        assert reset.returncode == 0, reset.stderr

        first = run("session1.py")
        assert first.returncode == 0, first.stderr
        assert "Base transaction:" in first.stdout

        second = run("session2.py")
        assert second.returncode == 0, second.stderr
        assert "25000.00 proposed -> 10000.00 authorized" in second.stdout
        assert "citing DV-001-V1" in second.stdout
        assert "Base transaction:" in second.stdout


@_LIVE
def test_live_contract_rejects_an_unauthorized_signer():
    """Regression guard for seam (d) round 3's most serious finding:
    the deployed contract originally had NO access control, so any
    address could permanently record any predictable decisionId
    (decisionId = keccak256 of a fixed, public string) — verified
    exploitable at the time by simulating exactly this call, which
    succeeded before the `authorizedSigner` restriction was added.
    Simulating from a freshly-generated, unrelated wallet must now
    revert. Nothing is broadcast: `.call()` simulates only, so this
    costs no gas and records nothing."""
    from eth_account import Account
    from web3.exceptions import ContractLogicError

    _w3, contract, _account, _deployment = adapter._connect()
    attacker = Account.create()
    decision_id = adapter._decision_id(f"DV-ATTACKER-{uuid.uuid4()}")

    with pytest.raises(ContractLogicError, match="not the authorized signer"):
        contract.functions.recordAuthorization(decision_id, 1, b"\x00" * 32).call(
            {"from": attacker.address}
        )
