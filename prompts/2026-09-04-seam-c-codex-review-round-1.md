# 2026-09-04 Seam (c) Codex Review — Round 1 Of 2

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, first pass on the seam (c) application code.
- Capture status: Drafted by Claude automatically and unasked, per the standing default (`AGENT_BUILD_INSTRUCTIONS.md` section 11 and the earlier correction that review prompts are never self-filtered as "too small"). Saved to `prompts/` after the fact — this file itself corrects a process slip where the prompt was given to Arko inline in chat but not persisted contemporaneously, as `AGENT_BUILD_INSTRUCTIONS.md` line 27 requires ("Save material prompts and planning artifacts contemporaneously under `prompts/`").
- Governing outputs under review: `finne/retrieval.py`, `finne/base/adapter.py`, `finne/demo_config.py`, `scripts/reset_demo.py`, `scripts/session1.py`, `scripts/session2.py`, `tests/test_retrieval.py`, `tests/test_fresh_session.py` (all new), and an 18-line addition to `finne/memory/client.py` (`clear_all_case_data_for_demo_reset`). All other files are unchanged from the merged seam (a)/(b) state.
- Review pass cap: this is pass 1 of the 2 permitted independent passes per `DECISION-025`.

## Review Prompt (verbatim, as given to Arko to run against Codex)

Review request: Finné Memory, seam (c) — retrieval and the two session scripts

Scope: `finne/retrieval.py`, `finne/base/adapter.py`, `finne/demo_config.py`, `scripts/reset_demo.py`, `scripts/session1.py`, `scripts/session2.py`, `tests/test_retrieval.py`, `tests/test_fresh_session.py` (all new), and the 18-line addition to `finne/memory/client.py` (`clear_all_case_data_for_demo_reset`). All other files are unchanged from the merged seam (a)/(b) state.

Context: This seam wires the pure authority engine (`finne/authority/`) to the Sibyl Memory adapter (`finne/memory/`) for the first time, and implements the two-session demo: Session 1 proposes 25,000 USDC, escalates at cold start, owner approves 10,000, case persists. Session 2 is a genuinely separate OS process that retrieves the precedent and autonomously constrains 25,000→10,000, citing `DV-001-V1` by name. A `--no-memory` control on Session 2 points at a fresh, never-seeded tenant to prove escalation with no precedent.

Please verify independently (against the live code, not the description above):

1. `find_candidates()` — does the coarse query (network/asset/action_class only) plus `comparability.compare()` correctly reproduce every case in `ACTIVE_DEMO_DESIGN.md` §5 (CASE-003 through 008) with the right eligibility, given the seeded states in `reset_demo.py`? Any candidate that should be excluded but isn't, or vice versa?
2. `BaseExecutionResult.attempted` — does every call site (`session1.py`, `session2.py`) correctly distinguish "stub, not attempted" from "attempted and failed" per NEG-07? Could a future real seam (d) failure be mis-reported as success anywhere in the current call sites?
3. `session1.py`/`session2.py` — do the persisted records (case version, owner-policy snapshot, authority events, outcome) exactly match what `ACTIVE_DEMO_DESIGN.md` §7 specifies, including that `DV-002-V1` deliberately stays at `draft`?
4. `test_fresh_session.py` — does it actually prove A3 (no in-process state carryover), or does anything in the two scripts implicitly depend on shared process state (env vars, temp files outside `--db-path`, module-level caching) that the subprocess boundary wouldn't catch?
5. The `clear_all_case_data_for_demo_reset` gap I found and the fix I chose (repeatable-rehearsal test starts from a fresh DB file, rather than trying to force-clear write-once references/journal entries) — is that the right resolution, or is there a real product-level problem with "the demo resets and rehearses repeatably" (A14) needing a live re-take against the *same* long-lived tenant?
6. Module boundaries: confirm no file outside `finne/memory/client.py` imports `sibyl_memory_client`, and that `finne/base/adapter.py` holds no key material (it currently holds none, by design, but worth confirming nothing snuck in).

## Status

Awaiting Arko running this against Codex and pasting back the findings. Per `AGENT_BUILD_INSTRUCTIONS.md` section 11, each finding will be independently re-verified against the live code before any fix is applied — Codex's description of a finding is never taken on trust.
