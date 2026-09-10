# Insurance-claims domain pivot — Codex review, round 1

Recorded 2026-09-10, submission day. Kickoff: `prompts/2026-09-10-insurance-domain-pivot-kickoff.md`.

---

**Review request: a project pivoted its entire demonstration domain on deadline day and claims it cost almost nothing. Verify that claim, because if it is wrong the submission is worse than before.**

`DECISION-028` re-instantiates the demo domain as insurance claims and reframes the product as a pre-dispute decision-control layer. Delivered as five commits on `feat/insurance-claims-domain`. Suite 262 passed, 4 skipped at every commit.

**The central claim to attack:** that the engine is genuinely domain-agnostic, evidenced by `finne/authority/`, `finne/memory/`, `finne/base/` and `finne/models.py` being untouched, and by only two test files needing changes. If that is true the pivot is sound. If the domain fits only because the fixtures were bent to fit the code, it is a costume and should be reverted.

Please verify independently:

1. **Is the domain mapping honest, or is it a reskin?** The argument is that five of seven fact dimensions were already neutral and the other two carry genuine insurance meanings — `network` as the claims channel (in-network/out-of-network is standard vocabulary) and `asset` as settlement currency (which is how `finne/cli.py` already renders it). Judge that as an insurance person would. Does `network: uk_retail_direct` read naturally, or does it read as a crypto field with a new value in it? If the latter, say so — it is better to know now than from a judge.
2. **Does the comparability rule still mean something in this domain?** It matches exactly on five dimensions plus a directional risk tier. In claims, is "same channel, currency, assessment type, peril and decision, and no riskier" actually the right test for whether one claim is precedent for another? Name what it would wrongly include or exclude.
3. **`CASE-005` is the fixture the pivot turns on.** Gradual leakage against a sudden-rupture record: active, upheld, superficially identical, not followable. Confirm the engine excludes it for the stated reason — a `target_class` mismatch — and not incidentally. Then judge whether the corpus as a whole is a real test or a demonstration of one rule.
4. **Did the pivot quietly change any behaviour?** The claim is that the numbers and mechanics are identical and only the meaning moved. Diff the corpus fixtures against the previous ones and confirm the amounts, states, outcomes and comparability results map one-to-one. Any drift is a finding.
5. **Sweep for stale domain references.** A repository-wide grep was run and reported clean across current-facing documents, with historical `PREREQ-002` / `DECISION-022` references preserved deliberately. Assume the sweep was incomplete — this project has recorded that exact under-search as a defect twice. Check `web/`, the test docstrings, and `docs/testing/TEST-CATALOGUE.md`, which was **not** updated and still describes the agent-spending corpus.
6. **Is the Base reframing honest?** Base moved from "execution and outcome evidence" to "tamper-evident attestation". The contract did not change — it already stored an amount and a `factsHash`. Is describing it as attestation accurate, or is it a better story told about the same thing? Separately: `finne/authority/derivation.py` still requires `outcome == "success"`, and the outcome comes from a Base transaction. In claims, "was this settlement upheld" has nothing to do with a chain. Is that seam now more visible or less?
7. **Is the PMF boundary held?** `HACKATHON_RULES.md` line 62 requires publicly verifiable evidence and states fabricated evidence disqualifies. The corpus is synthetic and `PRD.md` carries an explicit NOT CLAIMED line. Check every document for anything that could read as a claimed insurer engagement, pilot, or real claims data — including the README's framing and the `web/` viewer.
8. **What did the pivot break that the tests do not cover?** Only two test files changed. That is either strong evidence of a clean seam or evidence that the tests do not constrain the domain at all. Which is it?

## Status

- Branch `feat/insurance-claims-domain`, five commits, not merged. `master` retains the working agent-domain demo at `faae7ce`.
- Suite: 262 passed, 4 skipped.
- Untouched throughout: `finne/authority/`, `finne/memory/`, `finne/base/`, `finne/models.py`, `finne/policy.py`, `finne/explain.py`, `finne/retrieval.py`, `finne/cli.py`.
- Known gap: `docs/testing/TEST-CATALOGUE.md` still describes the agent-spending corpus and its four open questions (`Q1`-`Q4`) remain unanswered.
- Not committed to `master`, not reviewed.
