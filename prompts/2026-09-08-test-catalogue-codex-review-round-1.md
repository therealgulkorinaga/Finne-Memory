# Test catalogue — Codex review, round 1

Recorded 2026-09-08. First review of `docs/testing/TEST-CATALOGUE.md`. No prior rounds.

---

**Review request: Finné Memory — an exhaustive test-case specification. Review it as a specification, not as code.**

`docs/testing/TEST-CATALOGUE.md` is new and is a **document only**: 564 enumerated test cases across every module, with preconditions, inputs, expected results, traceability to `A1`–`A14` / `INV-1`–`INV-10` / `NEG-01`–`NEG-09`, a coverage column, eight findings, and six recommendations. No application code, test code, or dependency changed. The suite is unchanged at 229 passed, 4 skipped.

The document's own risk is specific and worth naming up front: **a test-case catalogue is exactly the kind of artifact that can be fluent, voluminous, and wrong.** A row that names a function that does not exist, asserts a value the code does not produce, or claims coverage that is not there is worse than no row, because it will be implemented as written and will then encode a false belief as a passing test. That is the failure mode to hunt.

Please verify independently:

1. **Are the expected results actually correct?** Sample aggressively across areas — at minimum the engine rows (TC-200–TC-253), the derivation rows (TC-170–TC-189), the `BaseExecutionResult` shape matrix (TC-410–TC-424), and the `is_memory_unavailable` matrix (TC-379–TC-395). For each sampled row, run the described input against the real code and confirm the stated expectation. Report any row whose expectation the code contradicts. Rows describing DELIBERATE current behaviour (TC-227's tie resolution, TC-233's citation on an ALLOW, TC-300's negative-amount acceptance, TC-603's exit codes) must be checked especially carefully — those are claims about what the code does today, and if any is wrong the document teaches the opposite of the truth.

2. **Is the coverage column honest?** It was assigned by reading `tests/*.py` and matching names and bodies, NOT by instrumentation — the document says so explicitly, and `coverage` was deliberately not installed because `DECISION-023` fixes the dependency list. Spot-check both directions: rows marked with a test name where that test does not actually exercise the case, and rows marked `GAP` where a test does cover it. The first direction is the dangerous one — a false "covered" hides a real hole.

3. **Attack the eight findings.** Each was reproduced against the running code before being written, and the reproduction is stated in the document. Re-run them. F-5 (a negative `authorized_amount` crashing `find_candidates` rather than reading as absent) is the one with real consequences — confirm or refute the full chain: write accepted, `from_body` accepted, `search_cases` passes it, `EvaluatedCandidate` raises, `is_memory_unavailable` returns False, both session scripts re-raise. Then judge the verdict: the document says the direction of failure is safe but that it violates `NEG-06`'s "treated as absent" and the sessions' own "the screen is not a traceback" contract. Is that the right reading? F-4 is classified as by-design rather than a defect — is that classification right, or is it a defect being excused?

4. **What is missing?** This is the question that matters most for an exhaustive catalogue, and the one I am least able to answer about my own work. 564 rows will read as complete whether or not they are. Name the module, branch, failure mode, or acceptance criterion that has no case and should. Pay particular attention to `INV-9` (key material), which the document itself flags as the weakest-covered invariant, and to whether the deletion cases in M.3 genuinely prove the organiser's gate rather than merely asserting it.

5. **Is the traceability sound in both directions?** Every `A*`, `INV-*`, and `NEG-*` should map to cases that would actually demonstrate it — not merely touch the same area. Check for the inverse too: cases claiming a trace they do not earn. A row tagged `INV-1` that does not constrain the ceiling is noise dressed as rigour.

6. **Is anything over-claimed?** The document asserts several properties about its own method: that findings were reproduced, that coverage marks came from inspection rather than measurement, that `GAP` means "not found by a search" rather than "proven absent". Are those hedges accurate and sufficient, or does the document still read as more authoritative than its method supports? This project has repeatedly found overclaiming in documents to be the recurring defect; assume it is present here and look for it.

7. **Are the recommendations correctly ordered and correctly scoped?** Recommendation 5 proposes adding `coverage` as a dev extra, which is a dependency change requiring a decision record. Recommendation 4 proposes fixing F-5 or recording it as accepted. Is anything recommended that should not be, or missing that should be first?

8. Separately from defects: **should this document exist in this form at all?** It is 1,035 lines and will need maintenance as the code changes. State plainly whether a smaller artifact — the findings plus the four parametrised matrices, say — would carry most of the value at a fraction of the upkeep. A verdict of "trim it" is a useful outcome.

## Status

- Branch: `feature/seam-e-cli-explain` (working tree; not committed).
- Files added: `docs/testing/TEST-CATALOGUE.md`, this prompt.
- Files changed: none.
- Tests: unchanged, 229 passed / 4 skipped.
- Not yet reviewed, not committed, not approved.
