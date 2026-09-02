# Sybill Hackathon

This repository is for an AI-assisted hackathon project.

Its purpose is to support persistent, incremental development through written specifications, bounded implementation tasks, branches, tests, reviews, commits, pull requests, and merges.

Product implementation has not started.

## Documentation Structure

- `PRD.md`: product requirements and unresolved product decisions.
- `AGENT_BUILD_INSTRUCTIONS.md`: agent roles, ownership, handoffs, reviews, and escalation rules.
- `ARCHITECTURE.md`: system architecture, constraints, and unresolved technical decisions.
- `DECISIONS.md`: product, architecture, and process decision log.
- `TASKS.md`: bounded implementation task registry.
- `AI_BUILD_GOVERNANCE.md`: voluntarily adopted, mandatory AI-build lifecycle and control gates.
- `HACKATHON_RULES.md`: official event-rule register; currently unresolved and unverified.
- `CONTRIBUTING.md`: collaboration and development workflow.
- `AI_USAGE.md`: repository-wide and change-level AI attribution.
- `HUMAN_DECISIONS.md`: material human decisions, corrections, rejected suggestions, and approvals.
- `BUILD_LOG.md`: chronological record of bounded work and verification checkpoints.
- `REUSED_COMPONENTS.md`: provenance and licensing record for reused code, assets, data, and dependencies.
- `prompts/`: contemporaneous material prompts and planning artifacts.
- `docs/product/`: product discovery and supporting product notes.
- `docs/architecture/`: architecture references and technical design notes.
- `docs/integrations/`: external service and integration notes.
- `docs/hackathon/`: hackathon-specific references and submissions.
- `docs/reference/`: source material and external references.

The PRD, issue registry, and agent build instructions are separate artifacts: the PRD defines the product, `TASKS.md` defines bounded work, and the agent instructions define how specialized agents may execute and coordinate that work.

The approved V1 decision-record contract is `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`; its complete synthetic corpus is defined in `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`.
