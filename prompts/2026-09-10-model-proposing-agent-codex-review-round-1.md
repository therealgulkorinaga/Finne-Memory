# Model-proposing agent — Codex review, round 1

Recorded 2026-09-10, submission day. Kickoff prompt: `prompts/2026-09-10-model-proposing-agent-kickoff.md`.

---

**Review request: a model was reinstated at runtime in a project that deliberately removed one five days ago. Review the reversal as hard as the code.**

`SPEC-002` / `DECISION-027` add `finne/agent.py`, a model-backed proposer. Arko identified that the project had no AI agent — `scripts/session1.py` line 87 was `proposal = build_proposal(owner_policy.max_amount)`, so the "agent" proposed the ceiling because the script handed it the ceiling. Suite 229 → 262 passed, 4 skipped.

**The governance question first.** On 2026-09-05, seam (e) round 4 recommended deleting the model from `finne/explain.py` after four rounds each found a new way for model-influenced text to state something false. Arko ratified that on 2026-09-06. This change partially reverses it. The argument for why that is coherent rather than a relapse:

> What was removed was model-written **prose asserting things about a decision** — an assertion can be false, and three attempts at validating "is this sentence true of this decision" all failed. What is added is a model-produced **structured proposal** — a proposal cannot be false, only unreasonable, and an unreasonable proposal is the input this product exists to constrain.

**Attack that argument.** If it does not hold, the change should not ship. Specifically: is there any path by which model output reaches something that asserts, displays, or decides rather than merely proposes? The `reasoning` field is requested from the model and deliberately dropped — confirm it is dropped everywhere and cannot reach the screen, the memory records, or the Base facts hash.

Please verify independently:

1. **Can the agent see what it is permitted to do?** This is invariant 11 and the thing that makes the demonstration honest. `finne/agent.py` must not reach `finne/authority/`, `finne/memory/`, `finne/policy.py`, or `finne/base/` — the tests check the transitive closure, but check the closure yourself, and check the request body too. `DEMO_AVAILABLE_CAPITAL` (25,000.00) and `owner_policy.max_amount` (25,000.00) are equal in this corpus and read from independent places. Is that genuinely independent, or is it a leak wearing a disguise? Would a judge reasonably read it as one?
2. **Try to make a model response cause an unsafe authorization.** The claim is that model output can change what is asked for and never what is granted. `tests/test_agent.py` covers ten malformed shapes, a prompt-injection attempt in `reasoning`, and a parametrised ceiling sweep — assume that is not exhaustive. Try oversized payloads, unicode and control characters in string fields, a valid-but-absurd `amount` (`"1e400"`, `"0.000000001"`, `"NaN"`, `"Infinity"`), duplicate JSON keys, a nested object where a string is expected, and a response that echoes a different `target_class` than the schema pinned.
3. **Is `require_parameters: true` actually sufficient?** It is sent because OpenRouter's own docs say enforcement varies by provider and some "treat it as a strong hint". Confirm the flag is in the request body on every path, and judge whether the failure mode it guards against is genuinely closed or merely narrowed. What happens if OpenRouter routes to a provider that honours the schema but truncates?
4. **The dependency.** `requests>=2.31` is now declared, amending `DECISION-023`. The reasoning is that it was already installed transitively via `web3`, that stdlib `urllib` fails certificate verification on this machine, and that declaring an already-present package changes nothing about the install footprint. Is that sound, or should this have used `urllib` with a `certifi` bundle and avoided touching the dependency list at all?
5. **No-fallback.** On every model failure the session raises and stops; there is deliberately no fallback to a fixed proposal. Confirm no path silently substitutes one, and judge the choice — on a recorded demo, is failing visibly right, or should the demo degrade?
6. **Is the default path genuinely untouched?** `--agent=fixed` must be byte-identical to before, and the test suite and the memory-deletion gate must still run with no key and no network. The 40% rubric gate depends on that. Verify it rather than take the diff's word for it.
7. **Are the document amendments honest and complete?** `SPEC-001` sections 9 and 15, `PREREQ-003` sections 6 and 17, and `ARCHITECTURE.md` were amended. `PREREQ-003` section 6 was NARROWED — from "only module holding key material or reaching the network" to "only module holding **signing** key material or reaching **Base**". Is that a legitimate narrowing or a weakening dressed as one? Grep the repository for any remaining current-facing statement that no model participates at runtime; a previous round of this project's reviews found exactly that class of under-search.
8. **What is missing?** The live model path has **not been exercised** — no `OPENROUTER_API_KEY` is present on this machine, so the agent has only ever run against a faked transport. Name what that leaves untested and what could still fail on camera.

## Status

- Branch: `master` (working tree; not committed). Also carries the uncommitted `web/` viewer (`DECISION-026`) and its own review prompt.
- Added: `finne/agent.py`, `tests/test_agent.py`, `SPEC-002`, two prompt files.
- Modified: both session scripts, `finne/demo_config.py`, `tests/test_import_boundaries.py`, `pyproject.toml`, `.env.example`, `README.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `PREREQ-003`, `SPEC-001`, and the audit documents.
- Tests: 262 passed, 4 skipped. The 229 pre-existing tests are unchanged.
- `SPEC-002` is DRAFT; its approval gate has not formally closed. Not committed, not reviewed.
