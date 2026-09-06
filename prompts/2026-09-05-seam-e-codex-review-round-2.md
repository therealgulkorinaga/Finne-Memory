# Seam (e) — Codex review, round 2

Recorded 2026-09-05. Round 1 prompt: `prompts/2026-09-05-seam-e-codex-review-round-1.md`.

---

**Review request: Finné Memory, seam (e), round 2 — verifying round 1's fixes and looking for what they broke.**

Round 1 returned NOT READY FOR COMMIT with three blockers, one important, and one nice-to-have. All five were reproduced against the live code and fixed. This round should verify the fixes independently and, more importantly, look for what the fixes themselves introduced — a previous seam in this project had a round-4 fix that was worse than the bug it closed, and that is the failure mode to hunt for here.

What changed since round 1 (verify against the code, not this list):

- `finne/explain.py`: the number allowlist is gone. `_narration_is_safe(narration)` now takes no decision, and rejects any Unicode numeric character, any scale word (`_NUMBER_WORDS`), any control or format character, and anything empty or over the length cap. Bare cardinals ("one", "five") are deliberately allowed.
- `finne/memory/client.py`: `fold_authority_state()` returns `None` on ANY cross-event contradiction or illegal transition, instead of the valid prefix, and logs an integrity warning via a module logger.
- `scripts/session1.py`, `scripts/session2.py`: memory construction and retrieval are wrapped, and a failure calls the new `cli.memory_failure()` and exits 1.
- `finne/cli.py`: every caller string renders as literal `Text` with control/format characters stripped (`_clean`/`_text`), and every write goes through `_emit`, which falls back to `print` and then to silence.
- `tests/test_import_boundaries.py`: resolves packages and relative imports, and a new test forbids `importlib`/`__import__` in `finne/` and `scripts/`.

Please verify independently:

1. `_narration_is_safe` — with the allowlist gone, can a model still put a misleading QUANTITY on screen? Consider roman numerals, spelled-out digits ("one zero zero zero zero"), hyphenated or possessive forms that split words, homoglyphs, "k"/"m"/"bn" suffixes, ordinal words, fractions written with a slash, and anything expressible without a `_NUMBER_WORDS` member. Separately: is it now over-rejecting to the point of uselessness — construct three narrations a model would plausibly return for this exact decision and see how many survive.
2. The `Cf`-category rejection and `cli._clean` — is there any character that can still reorder, hide, or overwrite rendered text and is NOT in a `C*` category? Zero-width joiners, combining marks, `\x7f`, and anything in `Mn` are worth trying against a real terminal.
3. `fold_authority_state` returning `None` on contradiction — what does this break? Trace every caller. A case that legitimately has a duplicate or out-of-order event now authorizes nothing at all, where it previously kept a prefix. Is there a real sequence in `reset_demo.py`'s corpus, or in a repeated `session1.py`/`session2.py` run, that can now produce `None` where it previously produced `active`? Is the logged warning actually reachable from a demo run, and does it say anything an operator can act on?
4. The `NEG-01` handling in both session scripts — the `except Exception` is deliberately broad. Confirm it cannot swallow a genuine programming error and report it as a memory failure in a way that hides a real bug (it prints the exception type; is that enough?). Confirm nothing is persisted, submitted, or displayed as authorized on that path, and that the exit code and message are the same in rich and plain mode.
5. `cli._emit`'s best-effort swallow — can it now hide a failure that matters? Specifically: is there any path where the decision panel silently fails to render and the run continues and exits 0, so a viewer or a test sees success with no visible decision? Should `decision_panel` be the one call that is NOT best-effort?
6. `tests/test_import_boundaries.py` — is `_resolve_relative` correct for level ≥ 2 and for `from . import x` (module `None`)? Does `_module_file` prefer the right file when both `x.py` and `x/__init__.py` exist? Can the dynamic-import test be evaded by `getattr(__builtins__, "__import__")` or an aliased `from importlib import import_module as f`?
7. The three tests moved/rewritten in this round (`test_fold_discards_the_whole_chain_at_a_break_not_just_the_tail`, and the new CLI tests placed in `tests/test_negative_cases.py`) — do they prove what they claim, and is placing CLI tests in the negative-cases file defensible, or is it hiding a missing `test_cli.py` that `PREREQ-003` section 14's eight-file list should have been amended to include?
8. Anything else across the whole seam, any severity — including anything round 1 confirmed as fine that these changes have since invalidated.
