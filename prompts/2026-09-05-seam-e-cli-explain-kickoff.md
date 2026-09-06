# 2026-09-05 Seam (e) Kickoff: Terminal Interface And Explanation

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Capture status: Contemporaneous.
- Governing outputs: `finne/explain.py`, `finne/cli.py`, `tests/test_explain.py`, `tests/test_negative_cases.py`, plus wiring into `scripts/session1.py` and `scripts/session2.py`.

## Material Instruction From Arko (verbatim)

> lets do seam (e)

Directing the fifth and final `SPEC-001` build seam immediately after seam (d) was committed, pushed, and opened as PR #10.

## Interpretation Notes Recorded By Claude

- PR #10 (seam (d)) was still OPEN when this began, so `feature/seam-e-cli-explain` was branched from `feature/seam-d-base-adapter`, not from `master` — branching from `master` would have silently dropped all of seam (d), which is exactly the mistake made once during seam (d) itself and caught before any commit. Consequence: PR #10 must merge before this seam's PR shows a clean diff.
- `tests/test_negative_cases.py` was the last of the eight test files `PREREQ-003` section 14 specifies and had never been written. It is included here rather than deferred, because its central case (NEG-05 / A10 — the deterministic path is identical with no model API key) is precisely the claim `finne/explain.py` introduces the risk to.
- `anthropic` is added to `pyproject.toml` as an OPTIONAL extra and deliberately left uninstalled. `PREREQ-003` section 13 requires both the full test suite and the recorded demo to run with no model available, so the deterministic explanation is what this project actually ships; model narration is a labelled extra that must never be load-bearing.
