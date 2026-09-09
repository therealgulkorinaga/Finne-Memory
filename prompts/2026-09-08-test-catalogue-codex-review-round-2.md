# Test catalogue — Codex review, round 2

Recorded 2026-09-08. Round 1: `prompts/2026-09-08-test-catalogue-codex-review-round-1.md`.

---

**Review request: Finné Memory test catalogue, round 2 — round 1 found two blockers and ten further findings. All twelve were reproduced and accepted. Verify the corrections, and verify what the corrections disturbed.**

Round 1's verdict was NOT READY FOR COMMIT. Nothing was disputed: every claim was re-run against the code and every one held. The document was rewritten rather than patched.

What changed (verify against the document, not this list):

- **Blocker 1 became `F-9` and open question Q1.** `INV-5` is false whenever `cold_start_autonomous_amount` exceeds an eligible precedent's amount — reproduced at cold start 500.00 with a 100.00 precedent, where losing the precedent RAISES authority to 500.00. The catalogue does not attempt to settle whether the invariant or the code is wrong; it is returned to Arko. TC-183, TC-189, TC-190 and TC-685 are marked `UNRES` and blocked.
- **Blocker 2 produced a Class column and a two-part split.** Every row is now `REQ`, `CHAR`, `DEFECT` or `UNRES`, with `DEFECT` and `UNRES` rows explicitly not implementable and each `DEFECT` row stating desired behaviour separately from observed. 17 of 479 rows fall in those two classes. Part I is normative; Part II is an explicitly non-authoritative behaviour inventory, per round 1's Document Form note. The document went from 564 rows to 479.
- **`F-10` is new**, from round 1's finding 3: exhaustive construction confirms SIX coherent `BaseExecutionResult` shapes, not five — `(True, False, True, "")` constructs because empty `tx_hash` is rejected only on the success path. Returned as Q3.
- **`F-2` and `F-6` were upgraded.** F-2 is not "odd attribution": the engine cites `DV-001-V1` while its own explanation states no active, comparable, successful precedent supports it. F-6 is not theoretical: with equal timestamps the fold returns `ACTIVE` or `None` depending on journal search order. Returned as Q2.
- **`F-4`'s reproduction was corrected.** The first draft's `ALLOW` came from proposing 0.00, not from the pairing. The claim is now narrow — the mismatched pairing passes the SCOPE GATE — and still classified by-design.
- **Coverage was re-audited.** All five false positives round 1 named are now `GAP` with the reason stated; the eighteen rows claiming coverage with no named test are `INDIRECT` or `GAP`; `PARTIAL` and `INDIRECT` no longer count as covered. New counts: 205 covered, 17 partial, 5 indirect, 252 gap.
- **Traceability is now GENERATED from the row data** rather than hand-written, so a case appears under a criterion only if its own row carries that trace. `A12` now has 14 rows. Comparable cases were removed from the `NEG-03` set.
- **Invalid inputs corrected.** Sibyl exceptions take a `message`; `TierGateError` also requires keyword-only `feature`. TC-682 no longer compares fields `AuthorizationDecision` does not have. The dangling TC-295 reference is gone.
- **The key-material cases were rewritten with a method** — a sentinel key and sentinel RPC token, an explicit artifact table, and `.env` named as the legitimate exception with a mode `0600` and gitignore assertion instead.

Please verify independently:

1. **Are the four open questions correctly scoped as questions?** Q1–Q4 are the load-bearing claim of this revision: that these are decisions rather than defects the catalogue should have settled. Challenge that. If any of them has an obviously correct answer that a specification already implies, the catalogue is dodging rather than escalating, and should say so.
2. **Re-run F-9 and F-2.** These changed the document most. Confirm the reproductions, and confirm the catalogue's characterisation — particularly that F-2 is a FALSE statement rather than an awkward one, and that F-9 is a defect in the invariant's wording rather than in the code.
3. **Is the Class assignment right per row?** Look specifically for rows classed `CHAR` that are really `DEFECT` — behaviour excused as "documented" that should be fixed — and for rows classed `REQ` whose expected result encodes an implementation accident rather than a requirement. TC-217, TC-227, TC-233, TC-234, TC-308, TC-315, TC-355, TC-431 and TC-432 are the ones I am least sure of.
4. **Re-audit the coverage column again, adversarially.** Round 1 found five false positives by reading test bodies. Assume more remain. The 205 rows now claiming a named test are the exposed surface; sample them and report any where the test does not assert what the row says.
5. **Is the Part I / Part II split defensible?** Part II is declared non-authoritative except for rows marked `REQ` — of which there are many. Judge whether that exception swallows the rule, and whether anything in Part II should have been in Part I or vice versa.
6. **What is still missing?** Same question as round 1, and still the one I am least able to answer about my own work. The document is now smaller, which means something was dropped. Was anything load-bearing among it?
7. **Is the document still too big?** Round 1 said a 1,035-line normative specification was the wrong shape. It is now 937 lines across two parts, of which the normative part is roughly half. State plainly whether that went far enough.

## Status

- Branch: `feature/seam-e-cli-explain` (working tree; not committed).
- Files added: `docs/testing/TEST-CATALOGUE.md`, round 1 and round 2 prompts.
- Files changed: none. No application or test code has been touched at any point.
- Tests: unchanged, 229 passed / 4 skipped.
- Not committed, not approved. Q1–Q4 remain open and block implementation.
