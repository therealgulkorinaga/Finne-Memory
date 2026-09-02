# Contributing

## Development Workflow

Use this mandatory lifecycle for future implementation:

`DECIDE → WRITE AND APPROVE SPEC → COMMIT SPEC → CREATE FEATURE BRANCH → SAVE PROMPT → IMPLEMENT BOUNDED SLICE → EXPLAIN CHANGES → TEST → MANUALLY VERIFY → UPDATE AUDIT DOCUMENTS → REVIEW DIFF → COMMIT → OPEN/UPDATE PR → INDEPENDENT REVIEW → FIX AND RETEST → HUMAN MERGE → KNOWN-GOOD CHECKPOINT`

No application implementation may begin before its bounded `SPEC-*` is approved by Arko and committed. One-shot and near-one-shot application generation are forbidden.

## Branches

One bounded feature or coherent repair must happen on one branch and pull request.

Branch naming convention:

DEFERRED: The exact naming convention will be selected in `PREREQ-003`. Until then, no implementation branch is authorized.

## Commits

Use small, coherent commits that preserve progressive development history. Agents may prepare changes and a proposed commit, but Arko approves commits and only a human may merge to `main`.

Commit message convention:

DEFERRED: Exact message syntax will be selected before implementation. Every commit must reference its committed specification or documented fix.

## Pull Requests

A pull request must cover one bounded feature or coherent repair, reference the committed specification, map tests to acceptance criteria, include the mandatory commit gate, and identify AI tools, prompt paths, assisted files, human decisions, reused components, limitations, and rollback point.

Pull request requirements:

An independent agent, session, or reviewer must perform a second-pass diff review. Unresolved `BLOCKER` findings prevent merge. Arko performs or directs fixes, confirms retesting, and controls the human-only merge.

## Tests

Automated testing requirements must be defined in the committed specification and mapped to acceptance criteria. Arko must personally verify affected product behavior and record the result.

Project-wide testing strategy:

UNRESOLVED: The project-wide test framework and commands belong to `PREREQ-003`.

## Documentation

Tests and documentation should accompany relevant implementation changes.

Product decisions and architectural changes must be recorded in `DECISIONS.md`.

Material prompts belong under `prompts/`. Every change must update `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md` where applicable.

For documentation-only commits, implementation tests and manual product verification may be `NOT APPLICABLE` with a reason. Documentation validation, internal-link checking, status consistency, AI attribution, human-decision traceability, independent-review status, and rollback identification remain mandatory.

## Stop Conditions And Commit Gate

The absolute stop conditions and mandatory commit gate in `AI_BUILD_GOVERNANCE.md` and `AGENT_BUILD_INSTRUCTIONS.md` are binding. A change cannot be committed or merged while any gate item is missing, any acceptance criterion is unproven, or Arko cannot explain its critical behavior and boundaries.
