"""Base execution adapter — the only module in this repository that
holds key material or reaches the network, per PREREQ-003 section 6.

Calls the deployed AuthorizationReceipt contract (finne/base/contracts/
AuthorizationReceipt.sol, address/ABI/chain in config/base_deployment.json)
via web3.py, signing locally with the key from FINNE_BASE_PRIVATE_KEY
(finne/base/env.py — never passed to the authority engine, never
written to Sibyl Memory, never logged, never committed).

Interface change from the seam (c) stub: record_authorization now also
takes `proposal`, not just `decision` and `decision_version_id`. The
contract's factsHash field is specified (PREREQ-003 section 11) as "a
hash of the material facts and cited precedents" — the material facts
(network, asset, action_class, target_class, function,
counterparty_risk_tier, amount) live on Proposal, not on
AuthorizationDecision, so computing a real factsHash requires both.
scripts/session1.py and scripts/session2.py are updated to pass it.

Per NEG-07 (Base failure must produce no false success and no
fabricated transaction reference): every path that returns
`attempted=False` corresponds to nothing having been submitted at all
(refused pre-flight, or a connection/read failure before any
transaction existed) — never to a transaction that was sent but not
yet confirmed. `attempted=True, success=False` covers every case where
a transaction (or the deliberate absence of one, per the NEG-08 check
below) was genuinely reasoned about against live chain state.

Per NEG-08 (duplicate execution must be rejected at both application
and contract level): before submitting, this module reads the
contract's own `recorded(decisionId)` state and refuses a doomed
duplicate submission itself, in addition to the contract's own
`require(!recorded[decisionId])` guard, which is the backstop if two
callers ever race.

FINNE_BASE_DRY_RUN=1 skips every network call and behaves like the
seam (c) stub (attempted=False), for automated tests that exercise
session1.py/session2.py's own orchestration logic as real subprocesses
without touching live infrastructure — matching PREREQ-003 section
14's mocked-by-default, opt-in-live testing philosophy already
specified for test_base_adapter.py, extended here to
test_fresh_session.py's subprocess invocations, which reach this real
adapter the same way a live demo run does. Found necessary the hard
way: running the full test suite once submitted two genuine,
permanent, zero-value transactions to Base Sepolia for the fixed
decision_version_id values scripts/session1.py and scripts/session2.py
use ("DV-001-V1", "DV-002-V1") — a contract's `recorded` state is
permanent and global, unlike a test's own temporary Sibyl Memory
database, so a live demo rehearsal against the same contract deployment
now correctly refuses those two decisionIds as already recorded; a
fresh contract deployment (scripts/deploy_contract.py --force) is
required before a live rehearsal, exactly as a fresh database file
already was for the local-only part of a rehearsal (see
scripts/reset_demo.py's own docstring).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract

from finne.base.env import get_env_var
from finne.models import AuthorizationDecision, Proposal

_DEPLOYMENT_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "base_deployment.json"
_SIX_DECIMAL_SCALE = Decimal(10) ** 6
_RECEIPT_TIMEOUT_SECONDS = 180
_DRY_RUN_ENV_VAR = "FINNE_BASE_DRY_RUN"


class ReconciliationMismatch(Exception):
    """The supplied transaction cannot be bound to the supplied
    decision_version_id (wrong contract, wrong sender, wrong function,
    wrong decisionId, or an unusable hash).

    Deliberately an exception rather than a BaseExecutionResult: a
    mismatch is an operator error about WHICH transaction to look at,
    not a fact about the decision's outcome. Returning it as a result
    let scripts/reconcile_outcome.py read "not success" as "confirmed
    failure" and persist an immutable, fabricated Outcome.FAILURE —
    reproduced directly during seam (d) round 5's review."""


def _is_dry_run() -> bool:
    return os.environ.get(_DRY_RUN_ENV_VAR) == "1"


@dataclass(frozen=True)
class BaseExecutionResult:
    """`attempted` distinguishes "no real Base call was made" (refused
    pre-flight, or a connection/read failure before any transaction
    existed) from "a real Base call was made" (NEG-07). `outcome_confirmed`
    then distinguishes a KNOWN result (success, or a confirmed failure —
    an outright broadcast rejection or an onchain revert) from a
    genuinely UNKNOWN one — a broadcast that was accepted by the node
    but whose confirmation timed out or errored before a receipt was
    obtained. That third state matters because W4 (PREREQ-003 section 3,
    "after the Base transaction settles") is write-once: a caller that
    treated "timed out waiting" the same as "confirmed failed" would
    permanently record Outcome.FAILURE for a transaction that might
    still land and succeed, with no way to correct it later — an
    independent review's finding, reproduced by tracing the original
    two-state design's `success=False` used for both cases. Reconcile a
    pending case later via get_receipt(decision_version_id), which
    checks the contract's own state directly rather than trusting any
    locally-cached assumption about what happened.

    __post_init__ enforces the only coherent shapes at the type level:
    unattempted (`attempted=False`, `outcome_confirmed=True` — nothing
    happened, which is itself a certain fact — `success=False`,
    `tx_hash=None`); attempted-and-confirmed (`outcome_confirmed=True`,
    `success` reflecting the real result, `tx_hash` a non-empty
    reference required on success, `None` permitted only on a
    pre-broadcast rejection that never got a hash); attempted-and-unknown
    (`outcome_confirmed=False`, `success` must be `False` — confirmed
    success can never coexist with an unconfirmed outcome — `tx_hash`
    present, since the broadcast was accepted even though its result
    isn't known yet).

    Checks use isinstance/strict-value comparisons, not truthiness —
    a prior review found `attempted="yes", success="yes", tx_hash=123`
    passed truthy checks despite none of these being the literal
    bool/str the type annotations promise."""

    attempted: bool
    success: bool
    outcome_confirmed: bool
    tx_hash: str | None
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.attempted, bool):
            raise ValueError(f"attempted must be a bool, got {type(self.attempted).__name__}")
        if not isinstance(self.success, bool):
            raise ValueError(f"success must be a bool, got {type(self.success).__name__}")
        if not isinstance(self.outcome_confirmed, bool):
            raise ValueError(f"outcome_confirmed must be a bool, got {type(self.outcome_confirmed).__name__}")
        if self.tx_hash is not None and not isinstance(self.tx_hash, str):
            raise ValueError(f"tx_hash must be a string or None, got {type(self.tx_hash).__name__}")

        if self.attempted is False:
            if self.success is not False or self.tx_hash is not None or self.outcome_confirmed is not True:
                raise ValueError(
                    "an unattempted BaseExecutionResult cannot claim success, "
                    "carry a transaction hash, or leave its outcome unconfirmed"
                )
            return

        if self.outcome_confirmed is False and self.success is not False:
            raise ValueError(
                "success cannot be claimed while the outcome is unconfirmed "
                "— a broadcast whose confirmation timed out or errored is "
                "unknown, not successful"
            )
        if self.outcome_confirmed is False and not self.tx_hash:
            raise ValueError(
                "an attempted-but-unconfirmed result must carry a real "
                "transaction hash — the broadcast was accepted even though "
                "its result isn't known yet; there is nothing 'unconfirmed' "
                "about a broadcast that never happened"
            )
        if self.success is True and not self.tx_hash:
            raise ValueError(
                "a successful BaseExecutionResult must carry a real, "
                "non-empty transaction hash — success is never recorded "
                "without one (NEG-07)"
            )


def _load_deployment() -> dict[str, Any]:
    if not _DEPLOYMENT_PATH.exists():
        raise RuntimeError(
            f"{_DEPLOYMENT_PATH} does not exist; run scripts/deploy_contract.py first"
        )
    return json.loads(_DEPLOYMENT_PATH.read_text())


def _redact_rpc_url(url: str) -> str:
    """Many RPC providers (Alchemy, Infura, QuickNode — all named as
    fallback options in .env.example) embed an API key directly in the
    URL path. Showing the full URL in an error message would leak that
    key into terminal output, logs, or anywhere the error text is later
    pasted — independent review flagged this as a real exposure even
    though the currently-configured public endpoint has no embedded
    secret; the code must not depend on which URL happens to be
    configured today.

    Strips URL user-info (https://user:key@host/...) as well as the
    path — `urlparse().netloc` includes user-info, so returning netloc
    alone would have preserved an embedded credential (independent
    review, seam (d) round 5)."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.hostname or "[unparseable-host]"
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return f"{parsed.scheme}://{host}/[redacted]"


def _connect() -> tuple[Web3, Contract, LocalAccount, dict[str, Any]]:
    rpc_url = get_env_var("BASE_RPC_URL")
    private_key = get_env_var("FINNE_BASE_PRIVATE_KEY")
    deployment = _load_deployment()

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"could not connect to {_redact_rpc_url(rpc_url)}")

    live_chain_id = w3.eth.chain_id
    if live_chain_id != deployment["chain_id"]:
        # Fail closed rather than sign for whatever network the RPC
        # happens to be on. A misconfigured BASE_RPC_URL (wrong network,
        # typo, stale value after switching providers) must never result
        # in silently signing and submitting to an unintended chain —
        # found missing by independent review; this project's own
        # architecture already treats network selection as a
        # configuration value precisely because it's meant to be
        # changed deliberately, which requires detecting an accidental
        # mismatch just as much as it requires allowing a deliberate one.
        raise RuntimeError(
            f"RPC chain ID {live_chain_id} does not match the deployed "
            f"contract's chain ID {deployment['chain_id']!r} in "
            f"{_DEPLOYMENT_PATH.name} — refusing to sign for the wrong network"
        )

    contract = w3.eth.contract(address=deployment["contract_address"], abi=deployment["abi"])
    account = Account.from_key(private_key)
    return w3, contract, account, deployment


_CONTRACT_PATH = Path(__file__).resolve().parent / "contracts" / "AuthorizationReceipt.sol"
_SOLC_VERSION = "0.8.24"
_DEPLOYMENT_RECEIPT_TIMEOUT_SECONDS = 180


def _compile_contract() -> tuple[list, str]:
    import solcx  # lazy: only deploy_contract() needs this, not the demo's normal run path

    solcx.install_solc(_SOLC_VERSION, show_progress=False)
    compiled = solcx.compile_files(
        [str(_CONTRACT_PATH)],
        output_values=["abi", "bin"],
        solc_version=_SOLC_VERSION,
    )
    key = next(k for k in compiled if k.endswith(":AuthorizationReceipt"))
    contract = compiled[key]
    return contract["abi"], contract["bin"]


def deploy_contract(*, force: bool = False) -> dict[str, Any]:
    """Compiles and deploys AuthorizationReceipt.sol, writing
    config/base_deployment.json (contract address, ABI, chain ID read
    from the connected RPC itself). Raises RuntimeError on any refusal
    (already deployed, no connection, zero balance, reverted deployment)
    rather than silently proceeding past one.

    This function — not scripts/deploy_contract.py — is where deployment
    actually reads the private key, signs, and reaches the network.
    Independent review found the original design had that code living
    directly in the script, outside finne/base/, contradicting this
    module's own stated boundary ("the only module in this repository
    that holds key material or reaches the network"). scripts/
    deploy_contract.py is now a thin CLI wrapper around this function."""
    if _DEPLOYMENT_PATH.exists() and not force:
        raise RuntimeError(f"{_DEPLOYMENT_PATH} already exists; pass force=True to redeploy deliberately")

    private_key = get_env_var("FINNE_BASE_PRIVATE_KEY")
    rpc_url = get_env_var("BASE_RPC_URL")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"could not connect to {_redact_rpc_url(rpc_url)}")

    account = Account.from_key(private_key)
    chain_id = w3.eth.chain_id
    if w3.eth.get_balance(account.address) == 0:
        raise RuntimeError(f"deployer wallet {account.address} has zero balance")

    abi, bytecode = _compile_contract()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": chain_id,
        }
    )
    tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.2)
    # Derived from the network rather than a hardcoded gwei assumption
    # — see _build_and_send's matching comment; the same fee-calculation
    # bug was independently present here until fixed.
    priority_fee = w3.eth.max_priority_fee
    base_fee = w3.eth.get_block("latest")["baseFeePerGas"]
    tx["maxPriorityFeePerGas"] = priority_fee
    tx["maxFeePerGas"] = base_fee * 2 + priority_fee

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=_DEPLOYMENT_RECEIPT_TIMEOUT_SECONDS)
    if receipt.status != 1:
        raise RuntimeError("deployment transaction reverted")

    deployment = {
        "contract_address": receipt.contractAddress,
        "abi": abi,
        "chain_id": chain_id,
        "deployment_tx_hash": tx_hash.to_0x_hex(),
        "deployment_block": receipt.blockNumber,
    }
    _DEPLOYMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DEPLOYMENT_PATH.write_text(json.dumps(deployment, indent=2) + "\n")
    return deployment


def _decision_id(decision_version_id: str) -> bytes:
    """decisionId = keccak256(decision_version_id), per PREREQ-003
    section 11 — matches the contract's own duplicate-protection key."""
    return Web3.keccak(text=decision_version_id)


def _facts_hash(proposal: Proposal, decision: AuthorizationDecision) -> bytes:
    """A hash of the material facts and cited precedents (PREREQ-003
    section 11), over a canonical (sorted-key, compact) JSON
    serialization so it is independently reproducible by anyone
    holding the same facts and decision — the whole point of storing
    this as verifiable evidence rather than a bare log line."""
    payload = json.dumps(
        {
            "network": proposal.network,
            "asset": proposal.asset,
            "action_class": proposal.action_class,
            "target_class": proposal.target_class,
            "function": proposal.function,
            "counterparty_risk_tier": proposal.counterparty_risk_tier.value,
            "amount": str(proposal.amount),
            "cited_precedents": list(decision.cited_precedents),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return Web3.keccak(text=payload)


def _authorized_amount_units(amount: Decimal) -> int:
    """Converts a Decimal USDC amount (e.g. Decimal('10000.00')) to the
    6-decimal integer units the contract's authorizedAmount field
    expects (PREREQ-003 section 11). A policy value only — the
    contract never moves this amount; it is a uint256 log field.

    Raises rather than rounds when amount has more than six decimal
    places: rounding up (the previous behavior, ROUND_HALF_UP) could
    silently record an on-chain policy value exceeding what the
    deterministic engine actually authorized — an authority-inflation
    bug found by independent review, not observed in practice only
    because every current caller already produces 2-decimal-place
    amounts. Fails loudly instead, matching this codebase's standing
    rule that a boundary conversion must never be allowed to widen
    authority, even silently and even for inputs no current caller
    happens to produce."""
    scaled = amount * _SIX_DECIMAL_SCALE
    if scaled != scaled.to_integral_value():
        raise ValueError(
            f"authorized amount {amount} is not exactly representable in "
            "6-decimal USDC units; refusing to round it, since rounding up "
            "would record a higher onchain amount than was authorized"
        )
    return int(scaled)


def _build_and_sign(
    w3: Web3,
    contract: Contract,
    account: LocalAccount,
    decision_id: bytes,
    authorized_amount_units: int,
    facts_hash: bytes,
):
    """Builds, gas-estimates, and locally signs — but does NOT broadcast.

    Split from broadcasting so the caller can compute the transaction
    hash BEFORE sending: independent review found that treating every
    send_raw_transaction exception as a confirmed pre-broadcast
    rejection recreates the same write-once false-failure hazard at the
    broadcast boundary that `outcome_confirmed` was introduced to close
    at the receipt-wait boundary. A transport-level failure can occur
    after the node already accepted the transaction, so the caller
    needs a real hash to reconcile against later.

    Everything this function does is genuinely pre-broadcast: a failure
    here (bad nonce, failed gas estimate, insufficient funds surfacing
    during estimation) leaves nothing pending and IS a confirmed
    failure."""
    fn = contract.functions.recordAuthorization(decision_id, authorized_amount_units, facts_hash)
    # Derived from the network rather than a hardcoded gwei assumption
    # — Base Sepolia's actual gas prices are small fractions of a gwei,
    # so a hardcoded priority fee reasonable on mainnet can end up
    # larger than maxFeePerGas here and be rejected outright (found
    # empirically while writing scripts/deploy_contract.py).
    priority_fee = w3.eth.max_priority_fee
    base_fee = w3.eth.get_block("latest")["baseFeePerGas"]
    tx = fn.build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": w3.eth.chain_id,
            "maxPriorityFeePerGas": priority_fee,
            "maxFeePerGas": base_fee * 2 + priority_fee,
        }
    )
    tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.2)
    return account.sign_transaction(tx)


def record_authorization(
    decision: AuthorizationDecision, proposal: Proposal, decision_version_id: str
) -> BaseExecutionResult:
    """Submits decision_version_id's authorization to the deployed
    AuthorizationReceipt contract. Refuses to submit anything the
    decision did not authorize (PREREQ-003 section 9) and refuses a
    doomed duplicate submission (NEG-08) — both checked here, in
    addition to the contract's own enforcement of each."""
    if _is_dry_run():
        return BaseExecutionResult(
            attempted=False,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=(
                f"{_DRY_RUN_ENV_VAR}=1: skipping the real Base call for "
                f"{decision_version_id!r} (used by automated tests exercising "
                "orchestration logic, not Base connectivity)"
            ),
        )
    if decision.authorized_amount <= 0:
        return BaseExecutionResult(
            attempted=False,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=(
                f"refusing to submit {decision_version_id!r}: the decision "
                f"authorized {decision.authorized_amount}, nothing to record"
            ),
        )

    try:
        authorized_amount_units = _authorized_amount_units(decision.authorized_amount)
    except ValueError as exc:
        return BaseExecutionResult(
            attempted=False,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=f"refusing to submit {decision_version_id!r}: {exc}",
        )

    try:
        w3, contract, account, _deployment = _connect()
    except Exception as exc:
        return BaseExecutionResult(
            attempted=False,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=f"could not connect to Base: {exc}",
        )

    decision_id = _decision_id(decision_version_id)

    try:
        already_recorded = contract.functions.recorded(decision_id).call()
    except Exception as exc:
        return BaseExecutionResult(
            attempted=False,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=f"could not read contract state before submitting: {exc}",
        )
    if already_recorded:
        return BaseExecutionResult(
            attempted=False,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=(
                f"{decision_version_id!r} is already recorded onchain; "
                "refusing a duplicate submission (NEG-08)"
            ),
        )

    facts_hash = _facts_hash(proposal, decision)

    try:
        signed = _build_and_sign(w3, contract, account, decision_id, authorized_amount_units, facts_hash)
    except Exception as exc:
        # Failed before anything could be broadcast (bad nonce, failed
        # gas estimate, insufficient funds surfacing during estimation)
        # — nothing is pending; this IS a confirmed, known failure.
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=True,
            tx_hash=None,
            detail=f"Base transaction could not be built or signed: {exc}",
        )

    # Computed locally from the signed transaction, BEFORE broadcasting,
    # so an ambiguous send failure still yields a real, reconcilable
    # hash (independent review, seam (d) round 5).
    local_tx_hash = Web3.to_hex(signed.hash)

    try:
        w3.eth.send_raw_transaction(signed.raw_transaction)
    except Exception as exc:
        # AMBIGUOUS, not a confirmed rejection: a transport-level
        # failure can happen after the node already accepted the
        # transaction, so it may still be mined and may still succeed.
        # Treating this as confirmed failure would recreate exactly the
        # write-once false-failure hazard `outcome_confirmed` exists to
        # prevent, just at the broadcast boundary instead of the
        # receipt-wait one.
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=False,
            tx_hash=local_tx_hash,
            detail=(
                f"broadcast failed ambiguously: {exc}; the node may still have "
                "accepted it, so the outcome is unknown, not confirmed failed — "
                "reconcile via scripts/reconcile_outcome.py"
            ),
        )

    try:
        receipt = w3.eth.wait_for_transaction_receipt(local_tx_hash, timeout=_RECEIPT_TIMEOUT_SECONDS)
    except Exception as exc:
        # The broadcast WAS accepted but its confirmation timed out or
        # errored — genuinely UNKNOWN, not a confirmed failure: the
        # transaction may still be mined and may still succeed. Never
        # write an immutable Outcome.FAILURE for this.
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=False,
            tx_hash=local_tx_hash,
            detail=(
                f"broadcast accepted but confirmation timed out or errored: {exc}; "
                "outcome unknown, not confirmed failed — reconcile via "
                "scripts/reconcile_outcome.py rather than treating this as final"
            ),
        )

    if receipt.status != 1:
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=True,
            tx_hash=local_tx_hash,
            detail="Base transaction reverted",
        )

    return BaseExecutionResult(
        attempted=True,
        success=True,
        outcome_confirmed=True,
        tx_hash=local_tx_hash,
        detail=f"recorded {decision_version_id!r} onchain",
    )


_LOG_SCAN_CHUNK_SIZE = 2000
_LOG_SCAN_MAX_CHUNKS = 25


def _find_transaction_hash(contract: Contract, decision_id: bytes, deployment_block: int, latest_block: int) -> str | None:
    """Scans backward from latest_block toward deployment_block in
    bounded chunks. A single get_logs call spanning the whole range can
    exceed the RPC provider's block-range limit — found empirically:
    a public Base Sepolia endpoint rejected a ~15,630-block range with
    "413 Payload Too Large" only hours after this project's own
    contract was deployed, silently swallowed by this function's own
    broad exception handling until traced down. Stops as soon as a
    match is found, or after _LOG_SCAN_MAX_CHUNKS chunks (up to 50,000
    blocks back) — bounded, not a single lucky guess at a "safe"
    window size."""
    chunk_end = latest_block
    for _ in range(_LOG_SCAN_MAX_CHUNKS):
        chunk_start = max(deployment_block, chunk_end - _LOG_SCAN_CHUNK_SIZE + 1)
        try:
            logs = contract.events.AuthorizationRecorded.get_logs(
                argument_filters={"decisionId": decision_id},
                from_block=chunk_start,
                to_block=chunk_end,
            )
        except Exception:
            return None
        if logs:
            return logs[0]["transactionHash"].to_0x_hex()
        if chunk_start <= deployment_block:
            break
        chunk_end = chunk_start - 1
    return None


def get_receipt(decision_version_id: str) -> BaseExecutionResult | None:
    """Reads back whether decision_version_id has a real onchain
    receipt, reconstructing the transaction hash from the emitted
    AuthorizationRecorded event via a bounded, chunked backward scan
    (see _find_transaction_hash). Returns None if nothing is recorded,
    the query itself fails, a recorded receipt's transaction hash could
    not be located within the scan bound, or the receipt's own
    submittedBy does not match this wallet's address — a query failure
    is not evidence of absence, but this function has no way to
    distinguish the two and must not guess.

    The submittedBy check is provenance verification, not just a
    duplicate-detection shortcut: the contract's own authorizedSigner
    restriction should make this unreachable in practice (only this
    wallet can ever succeed in writing a receipt at all), but this
    function must not blindly trust "recorded=True" as sufficient proof
    on its own — a differently-configured or older contract deployment
    without that restriction would otherwise let a receipt genuinely
    submitted by a third party be reported as this project's own
    evidence."""
    if _is_dry_run():
        return None
    try:
        w3, contract, account, deployment = _connect()
    except Exception:
        return None

    decision_id = _decision_id(decision_version_id)

    try:
        recorded = contract.functions.recorded(decision_id).call()
    except Exception:
        return None
    if not recorded:
        return None

    try:
        _amount, _facts_hash, submitted_by, _recorded_at = contract.functions.getReceipt(decision_id).call()
    except Exception:
        return None
    if submitted_by.lower() != account.address.lower():
        return None

    try:
        latest_block = w3.eth.block_number
    except Exception:
        return None

    tx_hash = _find_transaction_hash(contract, decision_id, deployment["deployment_block"], latest_block)
    if tx_hash is None:
        return None

    return BaseExecutionResult(
        attempted=True,
        success=True,
        outcome_confirmed=True,
        tx_hash=tx_hash,
        detail=f"onchain receipt found for {decision_version_id!r}",
    )


def reconcile_pending(decision_version_id: str, tx_hash: str) -> BaseExecutionResult:
    """Resolves a previously-unknown outcome (a receipt-wait timeout,
    `outcome_confirmed=False`) by checking the ORIGINAL transaction's
    own receipt directly, rather than relying only on contract state.
    get_receipt(decision_version_id) alone cannot distinguish "still
    pending" from "confirmed reverted" — both look identical
    (recorded()=False) from contract state, since a reverted
    transaction never writes anything. Checking the transaction itself
    resolves that ambiguity: no receipt yet means genuinely still
    unresolved; a receipt with status=0 means confirmed reverted;
    status=1 means confirmed success.

    A transaction at tx_hash is NOT by itself evidence about
    decision_version_id. This function verifies the binding from the
    transaction's OWN CALLDATA — sender, recipient, function selector,
    and the exact `decisionId` argument — before reporting any outcome.
    Calldata rather than event logs, because a REVERTED transaction
    emits no events at all: an earlier version checked only the
    recipient address for the revert path, which meant any reverted
    transaction to this contract could be attached as immutable failure
    evidence for any decision (independent review, seam (d) round 5).

    Anything that cannot be bound to decision_version_id raises
    ReconciliationMismatch rather than returning a result. That
    distinction is the whole point: an earlier version returned
    `success=False, outcome_confirmed=True` for a mismatch, which
    scripts/reconcile_outcome.py correctly read as "confirmed
    execution failure" and wrote as an immutable Outcome.FAILURE —
    reproduced directly: an unrelated transaction hash persisted a
    fabricated `failure` for a decision that transaction never
    represented, while printing "refusing to treat it as evidence".
    A mismatch is an operator error about WHICH transaction to look
    at, not a fact about the decision's outcome, and raising makes it
    impossible for any caller to conflate the two.

    scripts/reconcile_outcome.py is the CLI wrapper that calls this and
    writes the resulting outcome to Sibyl Memory exactly once — this
    function itself does no persistence, only the chain query, per the
    same module boundary the rest of this file observes.

    Independent review found no reconciliation workflow existed at
    all: session1.py/session2.py correctly stopped writing an
    immutable Outcome.FAILURE for a timeout, but nothing ever
    completed W4 for a pending case afterward."""
    try:
        w3, contract, account, deployment = _connect()
    except Exception as exc:
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=False,
            tx_hash=tx_hash,
            detail=f"could not connect to check {tx_hash!r}: {exc}",
        )

    from web3.exceptions import TransactionNotFound

    try:
        transaction = w3.eth.get_transaction(tx_hash)
    except TransactionNotFound:
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=False,
            tx_hash=tx_hash,
            detail=f"{tx_hash!r} is not known to the node — still pending, dropped, or never broadcast",
        )
    except Exception as exc:
        # A malformed tx_hash (not valid hex, wrong length) raises a
        # validation error distinct from TransactionNotFound. That is an
        # operator error about the input, not a fact about the outcome.
        raise ReconciliationMismatch(f"{tx_hash!r} is not a usable transaction hash: {exc}") from exc

    # --- bind the transaction to this decision, from its own calldata ---

    if transaction["to"] is None or transaction["to"].lower() != deployment["contract_address"].lower():
        raise ReconciliationMismatch(
            f"{tx_hash!r} did not target the configured contract "
            f"({deployment['contract_address']}) — it is not evidence about {decision_version_id!r}"
        )
    if transaction["from"].lower() != account.address.lower():
        raise ReconciliationMismatch(
            f"{tx_hash!r} was not sent by this wallet ({account.address}) "
            f"— it is not evidence about {decision_version_id!r}"
        )

    try:
        fn, args = contract.decode_function_input(transaction["input"])
    except Exception as exc:
        raise ReconciliationMismatch(
            f"{tx_hash!r} calldata is not a call to this contract's ABI "
            f"— it is not evidence about {decision_version_id!r}: {exc}"
        ) from exc
    if fn.fn_name != "recordAuthorization":
        raise ReconciliationMismatch(
            f"{tx_hash!r} called {fn.fn_name!r}, not recordAuthorization "
            f"— it is not evidence about {decision_version_id!r}"
        )
    if args.get("decisionId") != _decision_id(decision_version_id):
        raise ReconciliationMismatch(
            f"{tx_hash!r} authorized a different decision — it is not evidence "
            f"about {decision_version_id!r}"
        )

    # --- the transaction IS this decision's submission; report its outcome ---

    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except TransactionNotFound:
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=False,
            tx_hash=tx_hash,
            detail=f"{tx_hash!r} is broadcast but not yet mined — still genuinely pending",
        )
    except Exception as exc:
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=False,
            tx_hash=tx_hash,
            detail=f"could not read {tx_hash!r}'s receipt: {exc}",
        )

    if receipt.status != 1:
        return BaseExecutionResult(
            attempted=True,
            success=False,
            outcome_confirmed=True,
            tx_hash=tx_hash,
            detail=f"reconciled {tx_hash!r}: confirmed reverted for {decision_version_id!r}",
        )

    return BaseExecutionResult(
        attempted=True,
        success=True,
        outcome_confirmed=True,
        tx_hash=tx_hash,
        detail=f"reconciled {tx_hash!r}: confirmed success for {decision_version_id!r}",
    )
