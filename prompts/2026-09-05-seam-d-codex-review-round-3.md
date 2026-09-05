# 2026-09-05 Seam (d) Codex Review — Round 3 Of 4 (Cap Extended By Arko)

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, third pass on seam (d).
- Capture status: Drafted by Claude automatically and saved to `prompts/` in the same turn as directed.
- Cap status: `DECISION-025`'s standing two-pass cap was explicitly extended by Arko for seam (d) specifically — see `HUMAN_DECISIONS.md`, "2026-09-05: Seam (d) Review Extended Beyond The Two-Pass Cap." Up to four rounds authorized this time; this is not a change to the standing cap for other bounded changes.
- Governing outputs under review: the complete current state of seam (d) — `finne/base/contracts/AuthorizationReceipt.sol`, `finne/base/env.py`, `finne/base/adapter.py`, `scripts/deploy_contract.py`, `scripts/session1.py`, `scripts/session2.py`, `tests/test_base_adapter.py`, `tests/test_import_boundaries.py` — after two prior review rounds (round 1: three BLOCKERs, two IMPORTANT, all fixed; round 2: drafted, not yet run).

## Review Prompt (verbatim, to give to Arko to run against Codex)

Review request: Finné Memory, seam (d) round 3 — a comprehensive, fresh review of the whole seam, not limited to prior rounds' specific findings.

Context: This is the third of up to four independent review passes on seam (d) (the Base contract, deploy script, and adapter), extended beyond the project's standing two-pass cap by explicit human direction, specifically to get a broader, fresh look rather than only verifying fixes to previously-reported items. Round 1 found and fixed: an authority-inflation rounding bug in the USDC-to-onchain-units conversion; a write-once immutability hazard where a receipt timeout was recorded as confirmed failure instead of unknown/pending; and a module-boundary violation where the deploy script held key material directly instead of `finne/base/adapter.py`. All three were fixed, plus two IMPORTANT findings (test fakes not exercising real chunk-scan logic; an inaccurate "never persisted" documentation claim).

Please review the ENTIRE current implementation with fresh eyes — do not limit yourself to re-checking the round 1 fixes (a round 2 prompt already covers that specifically). Look in particular at:

1. `finne/base/contracts/AuthorizationReceipt.sol` — reentrancy, storage-layout, gas-griefing, or access-control concerns in the full contract, not just the signature match already confirmed. Is there any way `recorded[decisionId]` and `_receipts[decisionId]` could diverge, or any way `getReceipt` could return misleading data for a decisionId that was never actually recorded?
2. `finne/base/adapter.py` in full — read it as a complete file, not function-by-function against a checklist. Does the overall control flow in `record_authorization` and `get_receipt` hold together coherently? Is there any code path — including ones triggered by unusual but possible inputs (empty proposal fields, extremely large amounts, non-ASCII decision_version_id strings) — that isn't covered by an existing test?
3. Concurrency and idempotency beyond what's already been checked: this project's architecture is single-writer-by-design (Session 1 fully exits before Session 2 starts), but does anything in this seam assume that more strongly than it should, or would break under a hypothetical concurrent invocation in a way worth flagging even if out of current scope?
4. `.env` handling — confirm the file permissions set when it was created (mode 0600) are still meaningful given how `finne/base/env.py` reads it, and whether there's any other place a secret could leak (subprocess environment inheritance in `scripts/session1.py`/`session2.py`, error messages that might include an exception repr containing sensitive data, etc.).
5. Test coverage for this seam overall, stepping back from individual test files: given everything now in `tests/test_base_adapter.py` and the live end-to-end verification already performed, is there a scenario a judge or auditor might reasonably probe that still isn't covered by any test?
6. Any documentation-vs-code mismatch across `PREREQ-003`, `SPEC-001`, and the actual current implementation that rounds 1-2 didn't touch.

Report anything found, at any severity — this round is explicitly about breadth, not just depth on prior items.

## Status

Awaiting Arko running this against Codex and pasting back the findings. Every finding will be independently re-verified against the live code (and, where relevant, re-run against live Base Sepolia infrastructure) before any fix is applied.
