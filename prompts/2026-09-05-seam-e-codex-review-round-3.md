# Seam (e) — Codex review, round 3

Recorded 2026-09-05. Prior rounds: `prompts/2026-09-05-seam-e-codex-review-round-1.md`, `prompts/2026-09-05-seam-e-codex-review-round-2.md`.

---

**Review request: Finné Memory, seam (e), round 3 — one mechanism was replaced outright; verify the replacement and what it disturbed.**

Round 2 returned NOT READY FOR COMMIT with two blockers, three important, and three nice-to-haves. All eight were reproduced and fixed. One fix is a replacement rather than a repair, and is the thing most worth attacking.

What changed since round 2 (verify against the code, not this list):

- `finne/explain.py`: prose narration is gone entirely. The model is sent a numbered list of sentences the module itself holds in `_EMPHASIS_BY_RESULT`, keyed on `(result, whether a precedent is cited)`, and must reply with a bare ASCII integer. `_selected_index` parses it; `explain()` renders the module's own sentence or nothing. There is no `_narration_is_safe` and no model-authored text anywhere in the output path.
- `finne/memory/client.py`: new `AuthorityChainCorruptionError`. A journal entry that claims to be an authority event for the decision under inspection and fails validation now fails the whole chain closed with a logged warning, instead of being skipped. New `MEMORY_ACCESS_ERRORS` tuple defines the memory-outage exception boundary for callers.
- `scripts/session1.py`, `scripts/session2.py`: catch `MEMORY_ACCESS_ERRORS` only, and print the traceback to stderr.
- `finne/cli.py`: `decision_panel` and `memory_failure` raise `PresentationError` when both output paths fail; everything else stays best-effort. `_clean` NFC-normalises and strips `Mn`/`Me`.
- `tests/test_import_boundaries.py`: dynamic-import prohibition now covers name references, reflective lookup, `builtins`, and `eval`/`exec`/`compile`; module resolution follows both `x.py` and `x/__init__.py`.

Please verify independently:

1. `_EMPHASIS_BY_RESULT` — is EVERY sentence actually true of EVERY decision it can be offered for? Enumerate the reachable `(result, cited)` combinations from the real engine (not from the test fixtures) and check each sentence against each. In particular: can a CONSTRAIN cite a precedent while being bound by something other than that precedent, so that "it held itself to a limit an earlier decision established" is false? Can an ALLOW cite a precedent it did not actually rely on? Is the ESCALATE-with-citation case reachable at all, and if it is not, is offering a sentence for it a latent bug?
2. The selection channel — can a model response still influence anything beyond an index into a fixed tuple? Check `_selected_index` for parsing surprises (leading `+`, underscores, whitespace forms, non-ASCII digits, values that `int()` accepts but `isdigit()` should not have). Check that the prompt cannot cause the SDK call itself to have a side effect, and that a raised exception anywhere in `_model_selected_emphasis` cannot escape.
3. Is the replacement actually an improvement, or a downgrade dressed as one? The model now contributes a single integer. Argue the other side: is this still a meaningful model integration, or has the project quietly removed its AI component while claiming to have hardened it? Say so plainly if the latter.
4. `AuthorityChainCorruptionError` — trace what now fails closed that previously succeeded. Is there any legitimate, non-adversarial sequence (a schema version bump, a partially-written journal, a future field addition, a repeated `session1.py` run) that now zeroes out a case's authority where it previously worked? What happens on a corpus where ONE case is corrupt — does retrieval still return the others?
5. `MEMORY_ACCESS_ERRORS` — is the tuple right? Is there a real Sibyl Memory or sqlite failure that raises something outside it (and so now crashes instead of escalating), or something inside it that is really a programming defect (and so is still being misclassified)?
6. `PresentationError` — `decision_panel` now raises. Trace both session scripts: is there any call site where that raise happens AFTER a write to Sibyl Memory or a Base submission, so failing closed leaves a half-written record? Confirm the two frames that fail closed are the right two.
7. `_clean`'s NFC normalisation — can normalisation itself change the meaning of a rendered value (a decision-version id, an amount, a fact value) rather than only its representation? Is stripping `Mn`/`Me` after composition ever destructive to a legitimate value this system can hold?
8. Anything else across the whole seam, any severity — including anything rounds 1 or 2 confirmed as fine that these changes have since invalidated. This is the third pass on the same seam; if the remaining findings are cosmetic, say so plainly rather than filling a quota.
