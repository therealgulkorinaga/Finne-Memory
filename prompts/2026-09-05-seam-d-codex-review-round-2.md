# 2026-09-05 Seam (d) Codex Review — Round 2 Of 2

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, second and — per the two-pass cap — final permitted pass on seam (d).
- Capture status: Drafted by Claude automatically and unasked, per the standing default, and saved to `prompts/` in the same turn as the fixes it reviews.
- Governing outputs under review: fixes applied in response to round 1 (`prompts/2026-09-05-seam-d-codex-review-round-1.md`) — `finne/base/adapter.py` (amount-representability check, `outcome_confirmed` field, `deploy_contract()` added), `finne/base/env.py` (corrected persistence claim), `scripts/deploy_contract.py` (reduced to a thin wrapper), `scripts/session1.py`/`scripts/session2.py` (`outcome_confirmed` handling), `tests/test_base_adapter.py` (new coherence/chunk/retry tests), `tests/test_import_boundaries.py` (new).
- Review pass cap: this is pass 2 of the 2 permitted independent passes per `DECISION-025`. If this pass finds anything still open, Claude stops and asks Arko how to proceed rather than drafting a third prompt automatically.

## Review Prompt (verbatim, to give to Arko to run against Codex)

Review request: Finné Memory, seam (d) round 2 — fixes for the round 1 findings.

Context: Round 1 found three BLOCKERs and two IMPORTANT findings. All five were fixed and re-verified, including a full live end-to-end re-run of `reset_demo.py` → `session1.py` → `session2.py` → `session2.py --no-memory` with real Base Sepolia transactions. Two live tests in `test_base_adapter.py` also needed a fix during re-verification: a real, previously-undiagnosed transient RPC read-replica lag (a fresh connection's read of just-confirmed contract state can briefly be stale) made both flaky; a bounded retry was added to the live tests' own verification reads only.

Please verify independently (against the live code, not this description):

1. `_authorized_amount_units` — confirm it now raises (rather than rounds) for any amount not exactly representable in six decimal places, and that `record_authorization` catches this cleanly as `attempted=False` rather than letting the exception escape. Are there other unit-conversion or precision boundaries in this seam that could still silently widen an authorized amount?
2. `BaseExecutionResult`'s new `outcome_confirmed` field and `__post_init__` — walk through every construction site in `record_authorization`/`get_receipt` and confirm each one sets `outcome_confirmed` correctly for what actually happened (in particular: is a submission-failure — the node rejecting the broadcast outright, before any tx_hash exists — correctly `outcome_confirmed=True`, given nothing is left pending, versus a post-broadcast timeout being `outcome_confirmed=False`?). Confirm `scripts/session1.py`/`scripts/session2.py` never write `Outcome.FAILURE` when `outcome_confirmed` is `False`.
3. `finne/base/adapter.py`'s `deploy_contract()` — confirm no file outside `finne/base/` imports `eth_account` or `web3` now (this is what `tests/test_import_boundaries.py` checks; verify the test itself is correct — does its AST-based scan actually catch a re-introduced violation, e.g. would it catch `import eth_account` inside a function body, not just at module level?).
4. `tests/test_base_adapter.py`'s new ranged fake (`_FakeEventQuery` with `log_block`) and the chunk-boundary tests — do they actually exercise `_find_transaction_hash`'s real chunk arithmetic correctly, or could the fake's simplifications (e.g., treating `log_block` as a single point rather than a real block that could appear in multiple overlapping-adjacent chunk boundaries) mask an off-by-one in the real chunking logic?
5. The live-test retry (`_retry_until`) — is 6 attempts × 3 seconds (18 seconds max) a reasonable bound, or could this mask a genuine bug by retrying past it? Should `record_authorization`'s own NEG-08 pre-check (`contract.functions.recorded(decision_id).call()`) be vulnerable to this same read-lag in a way that could let a genuine duplicate slip through in production, not just in tests?
6. `finne/base/env.py`'s corrected persistence claim — is "never written to Sibyl Memory, logged, or committed to version control" now fully accurate, or does the key appear anywhere else not covered by that claim (e.g., process environment visible to other processes, shell history if ever exported manually, crash dumps)?
7. Is there any other place in seam (d) where an amount, outcome, or duplicate-check could still be wrong in a way round 1 and this round's fixes didn't surface?

## Status

Awaiting Arko running this against Codex and pasting back the findings. This is the second and final permitted pass for seam (d) per `DECISION-025`'s cap — any finding still open after this pass will be surfaced to Arko rather than triggering an automatic third round.
