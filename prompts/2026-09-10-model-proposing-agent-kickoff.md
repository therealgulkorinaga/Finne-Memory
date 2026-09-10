# Model-proposing agent — implementation kickoff

Recorded 2026-09-10, before implementation, per `AI_BUILD_GOVERNANCE.md`'s lifecycle (`SAVE PROMPT` precedes `IMPLEMENT`) and `DECISION-025`.

---

## What Arko asked

Verbatim, across three messages on 2026-09-10:

> "check the demo rules of the hackathon befoer making a decision, more importantly I didnt use any AI, where is the AI agent"

> "If i go for option 2, which is better an API call or local"

> "can i use open router" / "yes i have an openrouter key, go ahead"

> "remember to create the specs and documentation too"

## What prompted it

Arko identified, unprompted, that the project has no AI agent. Verified: `scripts/session1.py` line 87 is `proposal = build_proposal(owner_policy.max_amount)`, and no model exists anywhere in the runtime — `pyproject.toml` declares `sibyl-memory-client`, `web3`, `py-solc-x`, `rich` and nothing else.

The full rules register was re-read before answering. **No event rule requires a model.** The 40% gate is memory being load-bearing, which holds. But the event is "build with agents that don't forget", and the documents said "the agent proposes 25,000" against a line that hardcodes the ceiling — an overclaim.

Three options were put to Arko: reframe honestly as infrastructure (30 min, no risk), make the agent real (60-90 min, real risk), or ship as-is. He chose to make it real, and chose OpenRouter because he holds a key.

## What is being built

Per `SPEC-002` and `DECISION-027`, both written before this prompt was saved:

- `finne/agent.py` — a model-backed proposer. Given an opportunity and its available capital; **never** given the ceiling, precedent, or any authority value. Returns a `Proposal` and nothing else.
- OpenRouter over its OpenAI-compatible endpoint, strict JSON schema, **`provider: {"require_parameters": true}`** — their docs state enforcement varies by provider and some "treat it as a strong hint", which on a recorded demo is unrecoverable.
- No new package dependency; a single JSON POST.
- `--agent=model` opt-in; `--agent=fixed` stays the default so the suite, the deletion gate, and a key-less judge are all unaffected.

## The line that must not be crossed

The model proposes. It never authorizes, widens, signs, or submits. This is why the change is safe despite partially reversing the seam (e) model removal: what was removed was model-written **prose asserting things about a decision**, which four rounds each found a new way to make false. What is added is a model-produced **proposal** that the deterministic engine then bounds. A false proposal is not a hazard — it is the input the product exists to constrain.

## Standing constraints carried into this work

- Reproduce before claiming. Every defect and every capability claim gets executed, not reasoned about.
- No silent fallback. A model failure is a visible failure; falling back to a hardcoded proposal would make the demo appear to work while proving nothing.
- The default path stays byte-identical. If the suite count moves for any reason other than the new tests, stop.
- Do not touch `finne/authority/`, `finne/memory/`, `finne/base/`, `finne/models.py`, `finne/policy.py`, or `config/owner_policy.toml`.

## Known state at kickoff

- Branch `master`, with uncommitted work: `web/` (the demonstration viewer, `DECISION-026`), plus `DECISIONS.md` and `REUSED_COMPONENTS.md` edits.
- Suite: 229 passed, 4 skipped.
- Deadline: 2026-09-10 23:59 UTC. `SPEC-002` is DRAFT and its approval gate has not formally closed; Arko directed implementation on deadline timing, recorded in `HUMAN_DECISIONS.md`.
