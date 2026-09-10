# Demonstration viewer (`web/`) — Codex review, round 1

Recorded 2026-09-10, submission day. Deadline 23:59 UTC.

---

**Review request: a new web surface was added to a project whose architecture deliberately chose not to have one. Review the decision as hard as the code.**

`web/` is new: `index.html` (32KB, self-contained), `quay-tokens.css` (vendored design tokens), and `README.md`. Implemented from a Claude Design artboard (`Finne Memory Demo.dc.html`, project `51086be5-d2b8-412c-ac5a-9eaf4a11b298`) that Arko designed and directed be built.

No application code, test code, or dependency changed. Suite unchanged at 229 passed, 4 skipped. `finne/` is untouched.

**The governance question comes first, because it is the one that can sink the submission.** `PREREQ-003` section 16 chose a `rich` terminal interface over a web one, reasoning that two side-by-side terminals make process separation self-evident on video and a browser tab does not. `SPEC-001` section 15 excludes a web application from `TASK-001` while permitting one "tracked separately, if pursued." The conflict was raised with Arko before implementation and he proceeded; it is recorded as `DECISION-026`.

Three properties were treated as the things that keep this page from weakening the project's central claim. Attack all three:

1. **It computes no authority.** Every decision value is fixed recorded output. The deterministic engine is not reimplemented in JavaScript. A simulator was explicitly considered and rejected, on the grounds that an interactive recalculating page would show a judge a reimplementation rather than the real engine — under a gate that tests whether memory is load-bearing, that seemed actively harmful. Is that reasoning right, or is it over-cautious in a way that costs the demo something?
2. **It makes process separation more explicit, not less.** Labelled process boundary, an explicit "Process exited. In-memory state discarded." panel, a "Fresh process. No carried-over state." marker. Does it actually achieve that, or does putting both sessions in one scroll undo `PREREQ-003` section 16's whole reason for choosing terminals?
3. **Its only live element is a real onchain read**, and it fails visibly rather than falling back to cached values.

Please verify independently:

1. **Does the page state anything untrue?** This is the highest-value question. Every number on it is a claim about a real system. Check the corpus rows against `ACTIVE_DEMO_DESIGN.md` section 5, the owner ceiling against `config/owner_policy.toml`, the derivation rule against `finne/authority/derivation.py`, and the exclusion reason given for each of the six excluded candidates against what the code would actually decide. The table asserts three distinct exclusion reasons — state, outcome, comparability — and attributes one to each row. Confirm each attribution.
2. **Re-run the onchain read.** The page embeds `keccak256("DV-001-V1")` and the `recorded(bytes32)` / `getReceipt(bytes32)` selectors as constants rather than deriving them at runtime, and decodes `getReceipt` positionally by ABI order. Verify the constants, verify the decode against `config/base_deployment.json`'s ABI, and confirm the displayed 10,000.00 is genuinely what the contract returns rather than a hardcoded figure dressed as a live read.
3. **The source artboard decoded `getReceipt` by guessing field roles from value ranges.** That was replaced with positional decoding, on the reasoning that a small `authorizedAmount` falling in the plausible-timestamp range would be misread as `recordedAt`. Confirm the replacement is correct and that four words are always returned.
4. **Try to make the onchain panel lie.** Block the RPC, return malformed data, return fewer than four words, return an error object, make it time out. The panel must never show a stale or invented value, and must never show the "ok" state without live data behind it. It claims "This panel never falls back to cached figures" — prove or disprove that.
5. **Is the no-wallet claim correct?** The page connects nothing and the README asserts a browser wallet *cannot* write to this contract because `AuthorizationReceipt.sol`'s immutable `authorizedSigner` rejects any other sender. Verify that against the contract source and `test_live_contract_rejects_an_unauthorized_signer`.
6. **Vendored tokens.** `quay-tokens.css` is a reduced copy of the design system's `colors_and_type.css` — only the consumed tokens, with a provenance header, recorded in `REUSED_COMPONENTS.md`. Is the provenance declaration accurate and sufficient for the event's Prior Work requirement?
7. **Does it hold up under inspection a judge might actually do?** View source, disable JavaScript, open it on a phone, run it with the RPC unreachable. It was tested at 1440px and 400px with no horizontal overflow and the session panels stacking, but only in one browser.

## Status

- Branch: `master` (working tree; not committed).
- Files added: `web/index.html`, `web/quay-tokens.css`, `web/README.md`, this prompt.
- Files changed: `DECISIONS.md` (adds `DECISION-026`), `REUSED_COMPONENTS.md`.
- Tests: unchanged, 229 passed / 4 skipped.
- Not committed, not reviewed.
