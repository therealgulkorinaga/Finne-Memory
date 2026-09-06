# 2026-09-05 Seam (e) Codex Review — Round 1 Of 2

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, first of the two permitted passes on seam (e).
- Capture status: Drafted automatically and saved to `prompts/` in the same turn as the work it reviews.
- Cap status: `DECISION-025`'s standing two-pass cap applies. Seam (d)'s extensions were scoped to seam (d) only.
- Governing outputs under review: `finne/explain.py`, `finne/cli.py`, `tests/test_explain.py`, `tests/test_negative_cases.py` (all new), plus `scripts/session1.py`, `scripts/session2.py`, `tests/test_fresh_session.py`, `tests/test_base_adapter.py`, `tests/test_import_boundaries.py`, `pyproject.toml`, `PREREQ-003`, `SPEC-001`.

## Review Prompt (verbatim, to give to Arko to run against Codex)

Review request: Finné Memory, seam (e) — the terminal interface and explanation. This is the fifth and final SPEC-001 build seam.

Context: `finne/explain.py` is the only module permitted to call a model (PREREQ-003 section 13) and must have no import path to `finne/base/`. `finne/cli.py` is presentation only. Both session scripts now route output through the CLI. Two previously-missing test files were written: `tests/test_negative_cases.py` (the last of PREREQ-003 section 14's eight specified files) and `tests/test_explain.py`. The suite runs, and the demo is recorded, with NO model API key present and with `anthropic` deliberately not installed.

Note: this branch is based on `feature/seam-d-base-adapter` (PR #10, still open at the time of writing), so its diff against `master` will include seam (d) until #10 merges. Review only the seam (e) files listed above.

Please verify independently (against the live code, not this description):

1. `finne/explain.py` — is it genuinely impossible for a model to affect the authorization? Trace whether `explain()`'s return value is read back anywhere, whether any caller branches on it, and whether the deterministic portion can be altered or suppressed by model output. Is `deterministic_explanation()` truly pure (no environment reads, no I/O, no ordering nondeterminism)?
2. `_narration_is_safe()` — the number-allowlist guard. Can a model response state a misleading amount that still passes (e.g. a number embedded in a word, a unicode digit, a percentage, an amount expressed in words rather than digits, scientific notation)? And does it over-reject in a way that would make narration useless in practice? Note the fallback is always safe, so over-rejection is a cost not a defect — but flag it if it is effectively always-reject.
3. `finne/cli.py` — confirm it contains no authority logic, reads no memory, and cannot alter what it renders. Is there any path where a rendering failure (a very long field, an unusual character, a narrow terminal) could crash a session script AFTER an authorization has been persisted but before the run completes?
4. The plain/rich duality: `FINNE_PLAIN_OUTPUT=1` is what the tests assert against, and rich panels are what the demo shows. Is the canonical change line (`25000.00 proposed -> 10000.00 authorized (citing DV-001-V1)`) genuinely identical in both modes, or could the two formats drift so that tests pass while the demo shows something different?
5. `tests/test_negative_cases.py` — do the tests actually prove what they claim for NEG-01 through NEG-07 and NEG-09? In particular, is the invariant-7 parametrised test meaningful, or does it pass trivially? Is anything in ACTIVE_DEMO_DESIGN.md section 8 still genuinely uncovered by ANY test file?
6. `tests/test_import_boundaries.py`'s two new tests — is the transitive-closure check correct (does it follow `from finne.x import y` where `y` is a module, and does it terminate)? Could a boundary violation evade it, e.g. via a runtime import inside a function body, an `importlib` call, or a conditional import?
7. Anything else across the whole seam, any severity.

## Status

Awaiting Arko running this against Codex and pasting back the findings. Every finding will be independently re-verified against the live code before any fix is applied.
