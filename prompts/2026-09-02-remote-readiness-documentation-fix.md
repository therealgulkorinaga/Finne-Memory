# Remote Readiness Documentation Fix Prompt

## Record

- Date: `2026-09-02`
- Human director: Arko
- AI tool: OpenAI Codex desktop agent
- Fix reference: `FIX-DOC-001: Correct default-branch terminology and review attribution`
- Scope: Bounded documentation correction only
- Prohibitions: Do not stage, commit, push, open a pull request, merge, create a branch, change authentication, begin `PREREQ-003`, create an implementation specification, or write application code

## Material Instruction

Search all tracked documentation for branch-specific references to `main`. Where the text means the protected or default integration branch, replace the hard-coded branch name with `the repository’s remote default branch`. Preserve `main` where it is ordinary English rather than a Git branch. State where useful that the current remote default branch is `master`, and require human-only merge regardless of whether the branch is named `master` or `main`.

Update `AI_USAGE.md` to record that the clean independent second-pass governance review covered the exact 15-file boundary against 27 criteria, completed successfully with no findings, and was accepted by Arko. Remove current statements that the review remains pending. Record the remote-readiness inspection and these corrections in `BUILD_LOG.md`, and attribute this prompt and all assisted files.

Do not change the product, architecture, prerequisites, implementation authorization, dependencies, scaffolding, or application code. `PREREQ-001` and `PREREQ-002` remain complete; `PREREQ-003` remains unresolved; no bounded implementation `SPEC-*` exists; and `TASK-001` remains unauthorized.

Validate links, formatting, decision chronology, status consistency, branch terminology, review attribution, and the absence of implementation artifacts. Preserve the original governance prompt as contemporaneous provenance even though its historical `main` wording is superseded by this fix.
