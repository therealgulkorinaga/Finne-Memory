# AGENTS.md

This file is the standing operating manual for every Codex agent working in this repository.

## Persistent Project Memory

Repository documentation is persistent project memory. Treat the documentation in this repository as the source of truth for current project intent, unresolved questions, decisions, constraints, and task state.

Do not rely on prior chat context when repository documentation says otherwise.

## Required Reading Before Implementation

Before implementing any task, read:

- `AGENTS.md`
- `TASKS.md`
- Relevant sections of `PRD.md`
- Relevant sections of `ARCHITECTURE.md`
- Relevant decisions in `DECISIONS.md`
- `HACKATHON_RULES.md` where applicable

If the relevant product, architecture, decision, or task information is marked `UNRESOLVED`, treat it as unresolved. Do not fill the gap with an unrecorded assumption when that ambiguity materially affects implementation.

## Scope Control

Never implement an undefined feature merely because it seems useful.

Never silently change:

- Product scope
- Architecture
- Protocols
- Dependencies
- Security model
- Data model
- External integrations

When ambiguity materially affects implementation, identify the ambiguity rather than making a hidden product decision.

Do not remove existing functionality unless the task explicitly requires it.

## Incremental Development

Work incrementally. One bounded task should normally produce one understandable unit of development history.

The expected workflow is:

Specification -> bounded task -> branch -> implementation -> tests -> review -> commit -> PR -> merge -> next task.

Every implementation task must include acceptance criteria before implementation starts.

Relevant tests must be run before declaring a task complete.

## Attribution And Auditability

Preserve attribution and auditability of AI-assisted development through:

- Understandable commits
- Meaningful commit messages
- Task references
- Pull request descriptions
- Documentation of material decisions

Explain significant code changes in the task or pull request summary.

Significant AI-assisted contributions should remain attributable through Git history. Prefer small meaningful commits over giant one-shot commits.

## Documentation Updates

Update documentation when implementation materially changes documented behavior.

If an architectural decision changes, update `DECISIONS.md`.

If task status changes, update `TASKS.md`.

Product decisions must be recorded. Architectural changes must be recorded.

## Dependencies

Do not introduce large dependencies without documenting why.

Dependency changes that materially affect architecture, security, deployment, build behavior, or external integrations must be reflected in the appropriate repository documentation.

## Security

Security-sensitive operations, credentials, private keys, and secrets must never be hard-coded into the repository.

Document material security assumptions and security-relevant implementation decisions.

## Code Comments

Add useful comments where they help explain intent, assumptions, constraints, or non-obvious behavior.

Do not add meaningless comments that simply restate obvious syntax.

## Hackathon Constraints

Respect `HACKATHON_RULES.md` as a hard project constraint.

If a requested implementation conflicts with `HACKATHON_RULES.md`, stop and identify the conflict before proceeding.

