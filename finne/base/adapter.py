"""Base execution adapter — STUB, pending seam (d).

This module's interface (record_authorization, get_receipt) matches
what PREREQ-003 section 17 and SPEC-001 section 7 already specify, so
session scripts can be written against it now without depending on an
implementation detail that will change. The implementation here
performs no real network call, holds no key material, and submits no
transaction — seam (d) replaces this module's body with the real
web3.py implementation against the deployed AuthorizationReceipt
contract on Base. Session scripts do not need to change when that
happens; only this file does.

Per NEG-07 (Base failure must produce no false success and no
fabricated transaction reference), this stub never claims success.
Every call returns success=False and tx_hash=None, explicitly labeled
as a stub result in `detail`, so nothing downstream — including a
persisted OutcomeRecord — can mistake a stub call for a genuine Base
outcome.
"""

from __future__ import annotations

from dataclasses import dataclass

from finne.models import AuthorizationDecision


@dataclass(frozen=True)
class BaseExecutionResult:
    """`attempted` distinguishes "no real Base call was made because
    seam (d) does not exist yet" from "a real Base call was made and
    failed" (NEG-07). Callers must not conflate the two: an unattempted
    result is an expected, transparent seam boundary, not a failure.
    Per PREREQ-003 section 3's W4 row ("after the Base transaction
    settles"), callers must never record an outcome — success or
    failure — until `attempted` is `True`; the authorization decision
    itself (W1-W3) is independently complete and correct before that,
    but the *outcome* genuinely does not exist yet. A genuinely
    attempted-and-failed result (`attempted=True, success=False`), once
    seam (d) exists, must never be reported as a success — that is what
    NEG-07 actually guards against.

    __post_init__ enforces the only two coherent shapes at the type
    level, so a caller cannot accidentally persist an incoherent
    combination (e.g. success without a real transaction reference):
    unattempted (`attempted=False, success=False, tx_hash=None`) or
    attempted (`attempted=True`, with `success` reflecting the real
    result and `tx_hash` a non-empty reference on success, `None` only
    permitted on a pre-broadcast failure that never got a hash).

    Checks use isinstance/strict-value comparisons, not truthiness —
    Codex's second review found `attempted="yes", success="yes",
    tx_hash=123` passed the original truthy checks despite none of
    these being the literal bool/str the type annotations promise. A
    caller relying on `if not result.attempted:` (as the session
    scripts do) would then treat that as `True`, letting a future,
    buggy seam (d) implementation slip an incoherent result past this
    guard and get treated as genuine success."""

    attempted: bool
    success: bool
    tx_hash: str | None
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.attempted, bool):
            raise ValueError(f"attempted must be a bool, got {type(self.attempted).__name__}")
        if not isinstance(self.success, bool):
            raise ValueError(f"success must be a bool, got {type(self.success).__name__}")
        if self.tx_hash is not None and not isinstance(self.tx_hash, str):
            raise ValueError(f"tx_hash must be a string or None, got {type(self.tx_hash).__name__}")
        if self.attempted is False:
            if self.success is not False or self.tx_hash is not None:
                raise ValueError(
                    "an unattempted BaseExecutionResult cannot claim success "
                    "or carry a transaction hash"
                )
        elif self.success is True and not self.tx_hash:
            raise ValueError(
                "a successful BaseExecutionResult must carry a real, "
                "non-empty transaction hash — success is never recorded "
                "without one (NEG-07)"
            )


def record_authorization(
    decision: AuthorizationDecision, decision_version_id: str
) -> BaseExecutionResult:
    """STUB. Seam (d) replaces this with a real, zero-value
    recordAuthorization(decisionId, authorizedAmount, factsHash) call
    against the deployed AuthorizationReceipt contract on Base Sepolia,
    returning attempted=True and the real success/tx_hash. `decision` is
    accepted now, unused, so the interface is already correct for that
    implementation rather than needing to change later."""
    del decision  # unused until seam (d); kept for interface stability
    return BaseExecutionResult(
        attempted=False,
        success=False,
        tx_hash=None,
        detail=(
            "finne.base.adapter is a stub pending seam (d); no real Base "
            f"transaction was attempted for {decision_version_id!r}"
        ),
    )


def get_receipt(decision_version_id: str) -> BaseExecutionResult | None:
    """STUB. Always returns None — no receipt can exist because no real
    transaction has ever been submitted through this stub."""
    del decision_version_id  # unused until seam (d)
    return None
