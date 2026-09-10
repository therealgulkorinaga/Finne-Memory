# README submission-readiness — Codex review, round 1

Recorded 2026-09-10, submission day. Deadline 23:59 UTC.

---

**Review request: Finné Memory README, rewritten for submission. Review it as the judged artifact it now is, not as prose.**

`README.md` was three merges out of date. Its Status section still read "Implementation has not started. No application code, scaffolding, or dependencies exist yet." while all five `SPEC-001` seams were merged and 229 tests passed. Four of the six sections `HACKATHON_RULES.md:52` requires were absent entirely.

What changed (verify against the repository, not this list):

- Status section replaced with a factual table: seams merged, test counts, contract address, deletion-gate test name, open questions.
- **Memory read/write table moved into the README** (W1–W5, R1–R5), which `HACKATHON_RULES.md:44` requires be findable within two minutes. Previously only a prose summary with a promise that "at implementation, this table moves into this README".
- **New: Memory Implementation Note** — what the agent persists, recalls, and uses to decide (`HACKATHON_RULES.md:55`).
- **New: Setup And Run** — clone, venv, install, test, and the demo sequence (`HACKATHON_RULES.md:52`).
- **New: Partner Stacks Used** — Sibyl Memory and Base with evidence paths; states Virtuals is not used (`HACKATHON_RULES.md:52`, `:54`).
- **New: Prior Work** — declares no external code reused, dependencies with licences, and the carried-forward `PREREQ-002` object model as this builder's own prior work (`HACKATHON_RULES.md:52`).
- **New: Builders And AI Tools** — names Arko, and Claude Code and Codex, pointing at `AI_USAGE.md` (`HACKATHON_RULES.md:98`, self-imposed practice).
- A top-of-file jump bar to the four judged sections.

**Two findings came out of smoke-testing the instructions, and both would have broken a judge's run.** Verify them first, because they are the highest-value part of this change:

1. Running the documented sequence under `FINNE_BASE_DRY_RUN=1` produces **escalate**, not the headline `25000 -> 10000`. With no Base attempt there is no recorded outcome, and `finne/authority/derivation.py` requires `outcome == "success"` for eligibility. This is specified behaviour — `test_session2_honestly_escalates_when_precedent_has_no_recorded_outcome` asserts it — but the first draft described dry-run as a plain convenience flag, which would have led a judge to conclude the demo does not work. Now documented explicitly in an environment-flag table.
2. **`DV-001-V1` and `DV-002-V1` are already recorded on the committed contract deployment.** Verified read-only against Base Sepolia: `recorded(keccak("DV-001-V1"))` and `recorded(keccak("DV-002-V1"))` both return `True`. A judge running live against `config/base_deployment.json` as committed gets a correct NEG-08 duplicate refusal, no outcome, and an escalating Session 2. `deploy_contract.py --force` is therefore **mandatory** before a live run, and the first draft called it optional. Now stated as a prerequisite in both the Status table and the run section.

Please verify independently:

1. **Do the documented instructions actually work, run verbatim, from a clean clone?** This is the whole point of the section and the thing I can least verify from inside the repository. Check the install command resolves, the test command produces the stated counts, and the demo sequence does what the README says it does at each step. Report any command that fails or produces different output.
2. **Are the two findings above correct, and are they now stated accurately?** Re-run the read-only `recorded()` check. If either is wrong, the run section is actively misleading on submission day.
3. **Is every factual claim true?** Test counts, contract address and chain id, PR numbers for the seams, the cited test names, the Python version floor, the dependency licences, and the memory-table call signatures against `finne/memory/client.py`. The table claims specific calls; confirm each matches the code rather than the architecture document, which is where they were copied from.
4. **Does the memory table satisfy the two-minute findability rule?** Judge it as someone who has never seen this repository and is looking for where memory is read and written. If it takes longer than two minutes to find and understand, say so and say what would fix it.
5. **Is the Prior Work declaration complete and honest?** It claims no external code was reused. Check that against `REUSED_COMPONENTS.md` and the actual tree. The `PREREQ-002` carry-forward is declared as this builder's own prior work — is that the right characterisation, and is it declared prominently enough?
6. **Is anything overclaimed?** This project's reviews have repeatedly found overclaiming in documents to be the recurring defect, and a README written on deadline is the most likely place for it. Look particularly at the Status table, "implemented and merged", and the deletion-gate claim.
7. **Is anything a judge needs still missing?** The remaining known gaps are the demo video and the two build-in-public posts, neither of which is a README item. Is there a submission requirement in `HACKATHON_RULES.md` that the README still does not satisfy?

## Status

- Branch: `master` (working tree; not committed).
- Files changed: `README.md` only. No application code, test code, or dependency touched.
- Tests: unchanged, 229 passed / 4 skipped.
- Not committed, not reviewed.
