# 2026-09-05 Seam (d) Codex Review — Round 4 Of 4 (Final, Per Arko's Extension)

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, fourth and — per Arko's explicit "up to four rounds" extension (see `HUMAN_DECISIONS.md`, "2026-09-05: Seam (d) Review Extended Beyond The Two-Pass Cap") — final permitted pass on seam (d) unless Arko directs a fifth.
- Capture status: Drafted by Claude automatically and saved to `prompts/` in the same turn as directed.
- Governing outputs under review: fixes applied in response to round 3 (`prompts/2026-09-05-seam-d-codex-review-round-3.md`) — `finne/base/contracts/AuthorizationReceipt.sol` (`authorizedSigner` access control), `finne/base/adapter.py` (provenance check, chain-ID verification, URL redaction, `outcome_confirmed`/`tx_hash` coherence, `reconcile_pending`), `scripts/reconcile_outcome.py` (new), `scripts/session1.py`/`scripts/session2.py` (reconciliation messaging), `tests/test_base_adapter.py` (new tests, new full-live-flow test), plus corrections to `ACTIVE_DEMO_DESIGN.md`, `PREREQ-003`, and `SPEC-001`.

## Review Prompt (verbatim, to give to Arko to run against Codex)

Review request: Finné Memory, seam (d) round 4 — final verification pass.

Context: Round 3 found and fixed a genuine, verified-exploitable security gap (the deployed contract had no access control at all — confirmed by simulating an unauthorized call before fixing, then confirming it reverts after), a missing reconciliation workflow for timed-out transactions, a coherence gap in the result type, a missing chain-ID check, an RPC-URL redaction gap, and governing-document drift traced to its root cause in `ACTIVE_DEMO_DESIGN.md`'s original `NEG-07` wording. A real test-coverage gap (no automated test actually ran `session1.py`/`session2.py` live) was also closed with a new opt-in live test, which passes. This is intended as the final pass before seam (d) is considered ready to commit — please focus specifically on whether THIS round's fixes are themselves sound, not on rediscovering what rounds 1-3 already covered.

Please verify independently (against the live code, not this description):

1. `AuthorizationReceipt.sol`'s `authorizedSigner` — is there any way to bypass this restriction (e.g., a proxy/delegatecall pattern this simple contract doesn't use but worth ruling out explicitly; behavior if the contract were ever deployed via a factory or `CREATE2` where `msg.sender` at construction time isn't the intended wallet)? Is `authorizedSigner` being `immutable` and set unconditionally in the constructor sufficient, or should there be an explicit check that it's non-zero?
2. `reconcile_pending()` and `scripts/reconcile_outcome.py` — walk through what happens if run for a `decision_version_id` that was never actually submitted (no `tx_hash` ever existed), for a `tx_hash` that belongs to a completely unrelated transaction (operator typo), and for a case that's already been reconciled once (does `write_outcome`'s write-once protection correctly prevent a second, possibly-different write, and does the script report this clearly rather than crashing confusingly)?
3. `get_receipt()`'s provenance check (`submitted_by.lower() != account.address.lower()`) — is comparing to `account.address` (derived fresh from `FINNE_BASE_PRIVATE_KEY` on every call) the right comparison, or should it compare against the contract's own `authorizedSigner()` instead, in case the configured private key is ever different from whichever wallet actually deployed the currently-configured contract?
4. The chain-ID check in `_connect()` — does it run early enough to prevent ANY use of a mismatched connection (i.e., is there any code path between establishing the `Web3` connection and the chain-ID check that could act on the wrong-chain connection first)?
5. Take one more full look at `finne/base/adapter.py` end to end, now that it has grown across four review rounds — is the file still coherent as a whole, or has it accumulated any inconsistency between the various fixes (e.g., do the dry-run check, the amount check, the connect step, and the duplicate check all happen in a sensible, non-contradictory order in `record_authorization`)?
6. Anything else at all, any severity — this is the last currently-authorized pass, so surface anything you'd otherwise flag as "worth a follow-up" too, even if minor.

## Status

Awaiting Arko running this against Codex and pasting back the findings. This is the fourth of the four rounds Arko explicitly authorized for seam (d); any finding requiring a fifth pass will be surfaced to Arko rather than triggering one automatically.
