# 2026-09-04 Seam (c) Kickoff: Retrieval And The Two Session Scripts

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Capture status: Contemporaneous, saved before this turn's file changes.
- Governing outputs: `finne/retrieval.py`, `finne/base/adapter.py` (minimal stub), `scripts/reset_demo.py`, `scripts/session1.py`, `scripts/session2.py`, `tests/test_retrieval.py`, `tests/test_fresh_session.py`.

## Material Instruction From Arko (verbatim)

> yes go ahead on seam (c)

Confirming the seam (b) PR (`#8`) was merged, following a short exploratory exchange about hackathon expectations (whether Sibyl's CLI/MCP tooling was relevant to the submission — concluded it is not; the plain SDK, already in use, is exactly what the rubric rewards) and directing the start of seam (c) — "retrieval and the two session scripts" — per the build order in `SPEC-001` section 14, authorized under `TASK-001`.

## Interpretation Notes Recorded By Claude

- Seam (c) is where `finne/authority/` (seam a) and `finne/memory/` (seam b) are first connected. This is the first point at which the two-session demo becomes runnable end to end for the authority-and-memory claim, though not yet for the Base-execution claim.
- `finne/base/adapter.py` does not exist yet — that is seam (d)'s scope, per `SPEC-001` section 14. Rather than block seam (c) on it, or silently expand seam (c)'s scope to include real Base integration, Claude is creating a minimal, explicitly-labeled stub (`record_authorization`/`get_receipt` matching the interface `PREREQ-003` section 17 already specified) that returns a clearly-marked simulated result. Session scripts call this real interface; seam (d) replaces the stub body with the real `web3.py` implementation without changing the interface session scripts depend on. This keeps seam (c) testable and demoable for the authority/memory claim now, without inventing Base behavior ahead of its own seam. Acceptance criterion A11 (a real Base transaction hash is persisted) is explicitly out of scope for `test_fresh_session.py` per `SPEC-001` section 12's own test mapping (`test_base_adapter.py` owns A11) — this is not a gap seam (c) is expected to close.
- The owner's approval of a constrained 10,000 USDC authority at Session 1's cold-start escalation is encoded as the session script's own deterministic default, not an interactive human prompt read at run time. `ACTIVE_DEMO_DESIGN.md` section 7 already fixes this value as part of the documented demo design ("the owner approves a constrained authority of 10,000 USDC"), so hardcoding it as the default is not inventing a product decision — it is what makes `test_fresh_session.py` runnable as an automated subprocess test without hanging on interactive input. A CLI override is provided so a live demo recording can still show the amount being entered on camera if Arko wants that; the richer interactive terminal experience itself is seam (e)'s explicit scope, not seam (c)'s.
