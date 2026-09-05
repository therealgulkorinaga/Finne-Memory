# 2026-09-05 Seam (d) Codex Review — Round 1 Of 2

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, first of the two permitted independent passes on seam (d).
- Capture status: Drafted by Claude automatically and unasked, per the standing default, and saved to `prompts/` in the same turn as the work it reviews.
- Governing outputs under review: `finne/base/contracts/AuthorizationReceipt.sol` (new), `finne/base/env.py` (new), `scripts/deploy_contract.py` (new), `tests/test_base_adapter.py` (new), `.env.example` (new), `config/base_deployment.json` (generated), `finne/base/adapter.py` (stub replaced with the real implementation), `scripts/session1.py` and `scripts/session2.py` (call-site updates), `tests/test_fresh_session.py` (dry-run gating added).
- Review pass cap: this is pass 1 of the 2 permitted independent passes per `DECISION-025`.

## Review Prompt (verbatim, to give to Arko to run against Codex)

Review request: Finné Memory, seam (d) — the Base contract and adapter.

Context: This seam replaces seam (c)'s Base stub with a real `web3.py` implementation against a deployed `AuthorizationReceipt` contract on Base Sepolia. It has been run live, for real, multiple times: contract deployed and redeployed, `record_authorization`/`get_receipt` exercised directly, and a full `session1.py -> session2.py` demo run completed end to end with real transactions (escalate → owner approves 10,000 → real Base tx succeeds → fresh Session 2 retrieves the precedent → autonomously constrains 25,000 to 10,000 → its own real Base tx succeeds). Three real bugs were found only by running against live infrastructure (not by inspection): a hardcoded gas fee assumption that Base Sepolia's actual (much cheaper) gas market rejected outright; an automated test suite that fired genuine transactions at live infrastructure once the adapter stopped being a stub (fixed with `FINNE_BASE_DRY_RUN=1`); and a `get_receipt()` event-log query that exceeded a public RPC provider's block-range limit within hours of deployment (fixed with a bounded, chunked backward scan).

Please verify independently (against the live code, not this description):

1. `finne/base/contracts/AuthorizationReceipt.sol` — does `recordAuthorization`'s signature exactly match `PREREQ-003` section 11 (`bytes32 decisionId, uint256 authorizedAmount, bytes32 factsHash`, non-payable, emits `AuthorizationRecorded`)? Does `require(!recorded[decisionId])` correctly and unconditionally prevent a duplicate write regardless of caller? Is there any path where `_receipts[decisionId]` could be written without `recorded[decisionId]` also being set, or vice versa?
2. `finne/base/adapter.py`'s `_facts_hash` — is hashing a canonical JSON serialization of the material facts and cited precedents (not the raw `Proposal`/`AuthorizationDecision` objects) a correct, sufficient reading of PREREQ-003's "hash of the material facts and cited precedents," or does it omit something that should be bound into the hash (e.g., the owner ceiling in force, the decision's `binding_constraint`)?
3. `record_authorization`'s NEG-08 pre-check (reads `recorded()` before submitting) plus the contract's own `require` — walk through whether there's any window where two concurrent callers (or a retry after a timeout) could still produce two on-chain writes for the same `decisionId`, given the pre-check is a separate read from the actual submission.
4. Every `BaseExecutionResult` returned by `record_authorization`/`get_receipt` — confirm each one is actually reachable, coherent per `__post_init__`, and that `attempted=False` genuinely never corresponds to a transaction that was actually broadcast (re-read the "unattempted" cases in `record_authorization`: refused-zero-amount, dry-run, connection failure, read-failure, and NEG-08-duplicate-detected — none of these submit a transaction, correct?).
5. `_find_transaction_hash`'s chunked backward scan — bounded at `_LOG_SCAN_MAX_CHUNKS * _LOG_SCAN_CHUNK_SIZE` = 50,000 blocks. Is this actually sufficient given the real, current gap between `deployment_block` and `latest` on the currently-deployed contract, and is the chunking logic itself correct (does it ever skip or double-count a block range, and does it correctly stop at `deployment_block`)?
6. `tests/test_base_adapter.py`'s lightweight fakes (`_FakeContract`, `_FakeEth`, etc.) — do they faithfully model the real `web3.py`/`eth_account` call shapes the adapter actually uses, or could a fake's oversimplification let a mocked test pass while the real integration is subtly broken? (The two opt-in live tests were both run for real and passed, which is independent evidence the mocks aren't masking anything — but check the mocks' fidelity on their own terms too.)
7. Module boundaries: confirm no file outside `finne/base/` reads `FINNE_BASE_PRIVATE_KEY` or constructs a signing account, and that the key never appears in any persisted file, log line, or Sibyl Memory record.
8. `tests/test_fresh_session.py`'s `FINNE_BASE_DRY_RUN=1` gating — confirm every subprocess invocation in that file actually receives it (no code path that spawns `session1.py`/`session2.py` without the environment override), since a single missed one would repeat the exact live-infrastructure incident that motivated this fix.

## Status

Awaiting Arko running this against Codex and pasting back the findings. Per `AGENT_BUILD_INSTRUCTIONS.md` section 11, each finding will be independently re-verified against the live code (and, where relevant, re-run against live Base Sepolia infrastructure) before any fix is applied — Codex's description of a finding is never taken on trust.
