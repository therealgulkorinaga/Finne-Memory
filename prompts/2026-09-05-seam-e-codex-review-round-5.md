# Seam (e) — Codex review, round 5

Recorded 2026-09-05. Prior rounds: rounds 1–4 in `prompts/2026-09-05-seam-e-codex-review-round-{1,2,3,4}.md`.

---

**Review request: Finné Memory, seam (e), round 5 — a feature was deleted; verify the deletion, not the feature.**

Round 4 recommended deleting the model-selected sentence rather than repairing it a fifth time. Claude accepted that recommendation and implemented it. **Arko has NOT ratified the removal** — `HUMAN_DECISIONS.md` records it as outstanding, deliberately, because it narrows a capability an approved document described. Read "accepted" below as Claude accepting a reviewer's recommendation, never as the human approval that is still pending. This round is about what a deletion of that size disturbs, and about whether the seam is now finished.

What changed since round 4 (verify against the code, not this list):

- `finne/explain.py` was rewritten. It contains `deterministic_explanation()` and an `explain()` that returns exactly that. No `_EMPHASIS`, no selection, no SDK import, no `os` import, no environment read.
- `pyproject.toml`: the `anthropic` optional extra is gone.
- `finne/memory/client.py`: `MEMORY_ACCESS_ERRORS` (a flat tuple) was replaced by `is_memory_unavailable(exc)`, which walks the `__cause__`/`__context__` chain. Both session scripts now catch broadly and re-raise anything that classifier rejects.
- `finne/cli.py`: `_clean` escapes rather than deletes, and escapes its own `<` delimiter, so the transformation is injective. No normalisation.
- `tests/test_explain.py` lost 34 tests that existed only to constrain the deleted mechanism and gained five structural ones. Suite went 258 → 228 passed, 4 skipped.
- `PREREQ-003` sections 13 and 19, `SPEC-001` section 12, and `ACTIVE_DEMO_DESIGN` `NEG-05` were corrected. The removal is recorded in `HUMAN_DECISIONS.md` as awaiting Arko's ratification, since it narrows a capability an approved document described.

Please verify independently:

1. **Did the deletion take coverage with it that was not about the deleted mechanism?** This is the highest-value question in this round. 34 tests were removed at once. Diff the old and new `tests/test_explain.py` and confirm every removed test was solely about model selection or narration — not about `deterministic_explanation()`'s content, purity, result-kind rendering, or the material-differences labelling that a real demo bug produced in seam (e).
2. Is `finne/explain.py` genuinely inert now? Confirm nothing anywhere still imports, patches, or documents the removed functions; that `explain()` and `deterministic_explanation()` cannot diverge; and that the module's stated purity (no I/O, no environment, no ordering nondeterminism) actually holds — including that dict/tuple iteration in the material-differences block is deterministic across runs.
3. `is_memory_unavailable()` — attack the chain walk. What happens when a defect is raised *while handling* an outage (`__context__` chains the outage under the defect) or an outage while handling a defect? Both are reachable in real code and classify oppositely depending on which link is found first. Are cycles and self-referential chains handled? Is `__context__` the right thing to follow at all, or does implicit chaining make the classifier too eager to see a defect?
4. The session scripts now `except Exception` and re-raise on a defect. Confirm the re-raise preserves the original traceback, that nothing was persisted or submitted before that point, and that the re-raised path is genuinely distinguishable on screen from the escalation path.
5. `cli._clean` — is it actually injective? Try to construct any two distinct inputs that render identically. Then judge the cost: `<` in ordinary text now renders as `<U+003C>`, and the demo shows this module's own prose. Is any legitimate string this system displays now mangled, and does escape expansion change wrapping in a way that matters on the demo's key frame?
6. **Is the seam finished?** Five passes on one seam is a lot. State plainly whether what remains is cosmetic. If it is, say so — a clean verdict is the useful outcome here, and a sixth pass has a real cost against the deadline.
7. Separately from defects: is the removal correctly and honestly recorded? `PREREQ-003` section 17 still grants `finne/explain.py` the exclusive permission to call a model while section 13 says nothing calls one. Is that pair coherent, or is it drift dressed up as a decision?
