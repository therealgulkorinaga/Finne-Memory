# Seam (e) — Codex review, round 4

Recorded 2026-09-05. Prior rounds: rounds 1–3 in `prompts/2026-09-05-seam-e-codex-review-round-{1,2,3}.md`.

---

**Review request: Finné Memory, seam (e), round 4.**

Round 3 returned NOT READY FOR COMMIT with one blocker, three important, and two nice-to-haves. All six were reproduced and fixed. Three rounds have now each broken the same feature — the plain-language sentence beside a decision — in a different way: prose filtering by allowlist (round 1), prose filtering by vocabulary (round 2), and selection keyed on too few facts (round 3).

That history is the most important input to this round. **A defensible outcome here is "delete the feature."** It contributes one sentence to a demo; it has consumed three review cycles; and each fix has been sound in isolation while missing something the next round found. If your judgement is that the remaining risk is not worth the sentence, say so plainly and recommend removal — that is a more useful finding than a fourth repair.

What changed since round 3 (verify against the code, not this list):

- `finne/explain.py`: `_EMPHASIS` is keyed on `(result, binding_constraint, cited)` — twelve entries. No counterfactual claims, no comparative claims about non-binding constraints. The SDK import, call, response extraction, join, and parse all sit inside one `except Exception` boundary.
- `tests/test_explain.py`: reachable decisions are enumerated by running `derive_effective_authority` across a matrix; tests assert every reachable key has a sentence, no key is unreachable, and the truth properties hold. A fake `anthropic` module exercises the SDK path for the first time.
- `finne/memory/client.py`: `MEMORY_ACCESS_ERRORS` narrowed to specific operational failures; `sqlite3.Error`, `sqlite3.DatabaseError`, and the sibyl validation/conflict errors are excluded with reasons recorded inline.
- `finne/cli.py`: no normalisation; combining marks escaped as `<U+XXXX>` rather than deleted.

Please verify independently:

1. **The recommendation question first.** Given three rounds of the same feature failing, is the current mechanism sound enough to ship, or should the sentence be deleted and `explain()` reduced to the deterministic template alone? Answer this before enumerating defects, and answer it as a judgement, not a hedge.
2. If it ships: is the enumeration matrix in `tests/test_explain.py` actually exhaustive over the engine's reachable outputs? It varies amount, cold-start, hard-policy override, candidate sets, and scope. What does it not vary that could produce a thirteenth key — a different `unknown_situation_behaviour`, a zero owner ceiling, multiple candidates with different eligibilities, a candidate whose amount exceeds the owner ceiling?
3. Are the twelve sentences true for every decision that can carry their key, using ONLY what the key guarantees? Attack the four `current_hard_policy` and `current_action_scope` entries specifically — those are the ones round 3 found wrong.
4. `MEMORY_ACCESS_ERRORS` — is `StorageError`/`TenantError`/`TierGateError`/`TierVerificationError` the right sibyl set? Does any of them actually indicate caller misuse? Is there a real unavailable-storage failure that now escapes as a crash, and is the recorded `sqlite3.DatabaseError` exclusion the right call?
5. `cli._clean`'s escaping — does `<U+XXXX>` introduce any new problem (a value that legitimately contains that literal text, width/wrapping effects, an escape that itself needs escaping)? Confirm distinct values stay distinct and that nothing legitimate this system holds is now mangled.
6. Anything else across the whole seam, any severity. If what remains is cosmetic, say so plainly — this is the fourth pass on one seam and a clean verdict is a real outcome, not a failure to find something.
