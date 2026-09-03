# Human Decisions

This ledger records material human decisions, corrections, rejected AI suggestions, and approvals. It supplements the chronological product and architecture log in `DECISIONS.md`; it does not replace it.

## 2026-09-02: Transferable AI Build Governance

- Human decision-maker: Arko.
- Decision reference: `DECISION-019`.
- Decision: Adopt the explicitly listed spec-driven, human-directed, progressively auditable operating rules as mandatory Sybill governance.
- Required exclusions: Do not import the ETHOnline-specific Finne thesis, stablecoin workflow, sponsors, bounties, deadline, prize cap, submission format, or demo requirements.
- Correction to prior process: An approved task or planning prerequisite alone is insufficient for implementation; the bounded `SPEC-*` must also be approved and committed first.
- Human-only controls: Arko approves commits, personally verifies affected product behavior, confirms understanding, and controls merge to the repository’s remote default branch.
- Rejected or deferred suggestions: No unseen PDF content was treated as confirmed. Event-specific Sybill hackathon rules remain `UNRESOLVED`.
- Approval status: Governance direction and the resulting governance checkpoint were approved by Arko after the successful independent second-pass review.

## 2026-09-02: Governance Review Corrections

- Human decision-maker: Arko.
- Decision reference: `DECISION-020`.
- Decision: Separate voluntary build governance into `AI_BUILD_GOVERNANCE.md` and retain `HACKATHON_RULES.md` only as the unresolved official event-rule register.
- Specification clarification: `PREREQ-001` and `PREREQ-002` are planning contracts. No bounded implementation `SPEC-*` exists, and none may be created until `PREREQ-003` is approved.
- Audit correction: Attribute the saved prompts and all materially AI-assisted files; explicitly identify the Arko-supplied lifecycle, stop conditions, and commit checklist as reused text.
- Approval boundary at the correction checkpoint: Staging, commit, push, merge, `PREREQ-003`, and `TASK-001` authorization remained prohibited. The clean second-pass review and later commit approval were subsequently completed; the other prohibitions remain in force unless Arko explicitly changes them.

## 2026-09-02: Finné Memory Naming

- Human decision-maker: Arko.
- Decision reference: `DECISION-021`.
- Confirmed names: Product `Finné Memory`; repository `Finne-Memory`; technical slug `finne-memory`; former product name `Sybill`.
- Event-name correction: `Sybill` remains the hackathon/event name wherever it refers to the event, organizer, rules, eligibility, submission, deadline, or event-specific restrictions.
- Historical boundary: Historical decisions, logs, reviews, prompts, commit descriptions, pull-request records, and historical repository URLs retain their original wording. Saved prompts are not rewritten.
- Product boundary: The naming migration changes no product thesis, V1 behavior, authority rule, corpus fixture, permission, acceptance criterion, or implementation gate.
- Approval boundary: Arko required occurrence classification before correction and has not authorized staging or commit.

## 2026-09-03: Controlled Domain Pivot To Base Agent Authority

- Human decision-maker: Arko.
- Decision references: `DECISION-022`, `DECISION-023`.
- Prompt record: `prompts/2026-09-03-revised-direction-base-agent-authority.md`.
- Decision: Change the demonstration domain, not the product. Finné Memory converts an autonomous agent's remembered operating history into bounded, auditable authority for its next action. The active V1 is an autonomous treasury agent deriving its bounded authority for a materially similar Base action in a fresh session.
- Naming correction supplied by Arko: Sibyl Labs is the organiser, Sibyl Memory is its mandatory infrastructure, Finné is the umbrella venture, Finné Memory is the product, `Finne-Memory` is the repository, and `finne-memory` is the slug. The product must never be described as Sibyl, and must never be claimed to provide generic agent memory.
- Authority model supplied by Arko: the owner permission ceiling is always superior to learned authority; effective authority is the strictest intersection of owner ceiling, hard policy, active precedents, learned constraint, and current action scope; and effective authority can never exceed owner authority.
- Substrate decision supplied by Arko: Sibyl Memory is the mandatory and sole store of remembered agent experiences. Supabase, PostgreSQL, pgvector, Pinecone, and other databases are prohibited for that purpose.
- Scope change accepted by Arko and flagged by Claude: Finné Memory's output changes from an advisory-only `PrecedentPacket` to a binding deterministic `AuthorizationDecision`. This amends `DECISION-002` and `DECISION-013` and required reconciling `AGENT_BUILD_INSTRUCTIONS.md` sections 2 and 9 and `AI_BUILD_GOVERNANCE.md`. Claude recorded it explicitly rather than applying it silently. **Arko's confirmation of this specific amendment is requested at the approval checkpoint.**
- Historical boundary required by Arko: historical decisions, saved prompts, build logs, previous commits, and merged pull-request records are preserved unrewritten. `DECISION-010`, `DECISION-011`, and `DECISION-012` are marked superseded with annotations; `DECISION-002` and `DECISION-013` are annotated as amended; six `docs/product/` files carry historical labels with their content untouched.
- Velocity model directed by Arko: one decision, one PRD, one architecture document, one specification, one independent review, then build. No documentation that documents other documentation, and no recursive review bureaucracy.
- Rejected or deferred by Claude under Arko's instruction: no alternative architectures, review packets, or competing proposals were produced, because no genuine blocker prevented a decision.
- Blocking item raised to Arko: the repository has **no `LICENSE` file**, which fails a stated submission requirement. Claude did not create one, because the licence choice is Arko's. MIT is recommended, matching `sibyl-memory-client`.
- Approval boundary: This turn is preparation only. Arko has not approved `DECISION-023` or `SPEC-001`, and has not authorized staging, commit, push, merge, dependency installation, contract deployment, onchain transactions, or implementation.

## 2026-09-03: Planning Checkpoint Approval And MIT Licence

- Human decision-maker: Arko.
- Decision references: `DECISION-022`, `DECISION-023`, `DECISION-024`.
- Approval given: Arko approved the planning checkpoint, including the controlled domain pivot (`DECISION-022`), the architecture (`DECISION-023`), and the proposed commit boundary and message.
- Scope-change confirmation: Arko's approval covers the flagged amendment that Finné Memory's output becomes a binding deterministic authorization bound rather than advisory decision support. `DECISION-002` and `DECISION-013` remain annotated as amended, and the reconciled statements in `AGENT_BUILD_INSTRUCTIONS.md` sections 2 and 9 and `AI_BUILD_GOVERNANCE.md` stand as approved.
- Licence decision: Arko selected **MIT**, closing `ORG-Q2`. Recorded as `DECISION-024`. `LICENSE` was added as the standard unmodified OSI MIT template with copyright `2026 Arko Ganguli`.
- Copyright-holder note raised by Claude: the copyright line names Arko Ganguli, inferred as the repository owner rather than supplied verbatim. If the intended holder is a different entity, `LICENSE` must be corrected before submission.
- Approval boundary that remains: `SPEC-001` still requires explicit approval and a commit of its own before `TASK-001` may be created or any implementation may begin. Arko has not authorized a push, a pull request, a merge, dependency installation, contract deployment, onchain transactions, or implementation.
