# AGENTS.md

This file is the standing operating manual for every Codex agent working in this repository.

## Persistent Project Memory

Repository documentation is persistent project memory. Treat the documentation in this repository as the source of truth for current project intent, unresolved questions, decisions, constraints, and task state.

Do not rely on prior chat context when repository documentation says otherwise.

## Required Reading Before Implementation

Before implementing any task, read:

- `AGENTS.md`
- `AGENT_BUILD_INSTRUCTIONS.md`
- `TASKS.md`
- Relevant sections of `PRD.md`
- Relevant sections of `ARCHITECTURE.md`
- Relevant decisions in `DECISIONS.md`
- `AI_BUILD_GOVERNANCE.md`
- `HACKATHON_RULES.md` for verified official event rules and unresolved event restrictions
- The governing committed `SPEC-*`
- Relevant entries in `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md`
- The material prompt saved under `prompts/`

If the relevant product, architecture, decision, or task information is marked `UNRESOLVED`, treat it as unresolved. Do not fill the gap with an unrecorded assumption when that ambiguity materially affects implementation.

Every implementation-agent prompt must include the exact control line required by `AGENT_BUILD_INSTRUCTIONS.md`.

No implementation may begin from an uncommitted specification. No one-shot or near-one-shot application generation is permitted.

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
- Shared schemas, interfaces, authority rules, or file ownership

When ambiguity materially affects implementation, identify the ambiguity rather than making a hidden product decision.

Do not remove existing functionality unless the task explicitly requires it.

No agent may redefine Finné Memory as a payment, escrow, x402, refund, settlement, transaction-dispute, or service-delivery verification product.

## Incremental Development

Work incrementally. One bounded task should normally produce one understandable unit of development history.

The mandatory lifecycle is defined verbatim in `AGENT_BUILD_INSTRUCTIONS.md` and `AI_BUILD_GOVERNANCE.md`. It requires an approved and committed bounded `SPEC-*`, a feature branch, contemporaneous prompt capture, bounded implementation, explanation, automated testing, Arko's manual verification, audit-document updates, diff review, human commit approval, a pull request, independent review, fixes and retesting, human-only merge to the repository’s remote default branch, and a known-good checkpoint.

Every implementation task must include acceptance criteria before implementation starts.

Relevant tests must be run before declaring a task complete.

## Attribution And Auditability

Preserve attribution and auditability of AI-assisted development through:

- Understandable commits
- Meaningful commit messages
- Task references
- Pull request descriptions
- Documentation of material decisions
- Contemporaneous prompts under `prompts/`
- `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md`

Explain significant code changes in the task or pull request summary.

Significant AI-assisted contributions must remain attributable at repository and pull-request level. Use small coherent commits; fabricated audit history and one-shot application commits are forbidden.

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

Add useful comments for non-obvious business rules, invariants, security and permission boundaries, and model limitations.

Do not add meaningless comments that simply restate obvious syntax.

## Hackathon Constraints

Respect `AI_BUILD_GOVERNANCE.md` as a hard project constraint. Verified official event rules in `HACKATHON_RULES.md` are also hard constraints, and unresolved material event restrictions block implementation authorization.

If requested work conflicts with either governance or a verified official event rule, stop and identify the conflict before proceeding.

The absolute stop conditions and mandatory commit gate in `AGENT_BUILD_INSTRUCTIONS.md` apply to every Work and Codex task. Agents never approve commits or merge to the repository’s remote default branch; those are human actions controlled by Arko.
