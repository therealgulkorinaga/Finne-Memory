# Sybill Issue And Task Registry

This is the implementation-oriented issue list. It is intentionally short while product prerequisites remain unresolved. Do not expand every possible workstream into a backlog before the shared product contracts and architecture are approved.

## Implementation Readiness

- Status: UNRESOLVED / BLOCKED
- Decision: There is not yet enough confirmed information to create the first implementation task.
- Reason: Every plausible first code change would require at least one undocumented product, schema, authority, interface, architecture, repository-layout, or testing decision.
- Consequence: `TASK-001` is reserved and has not been created. The items below are specification prerequisites, not implementation tasks.

## Workflow

Specification -> bounded task -> branch -> implementation -> tests -> independent review -> human understanding gate -> commit -> PR -> merge -> next task.

## Required Task Format

Each implementation task must include:

- Task ID
- Title
- Status: `CONFIRMED | PROPOSED | ASSUMPTION | UNRESOLVED | DEFERRED`
- Owner role
- Spec reference
- Objective
- Why this task exists
- Dependencies
- Exact scope
- Explicit exclusions / out of scope
- Files or components expected to be affected
- Interfaces consumed and exposed
- Functional acceptance criteria
- Technical acceptance criteria
- Testing requirements
- Documentation requirements
- Handoff requirements
- Stop conditions
- Definition of Done

## Prerequisites Before TASK-001

### PREREQ-001: Confirm V1 Product Choices

- Status: CONFIRMED / COMPLETE
- Owner role: Product Spec Agent
- Spec reference: `PRD.md` and `docs/product/PREREQ-001_PRODUCT_DEFINITION_PROPOSAL.md`
- Objective: Obtain approval or changes for the four product decision packages in the Product Definition Proposal.
- Scope: Target user, supplier-onboarding demo domain, representative matter, downstream decision boundary, write-back expectation, and demo narrative.
- Allowed files or ownership area: `PRD.md`, `DECISIONS.md`, and product notes under `docs/product/`.
- Required interfaces: None; this is a product-definition task.
- Exclusions: Technical architecture, framework selection, data-store selection, implementation, and external integration selection.
- Dependencies: Satisfied by Arko's approval of the four product decision packages.
- Acceptance criteria: SATISFIED. Arko approved the V1 domain, primary user and buyer, representative matter, and clarified human-confirmed write-back rule; the proposal, PRD, and decision log are reconciled.
- Testing requirements: Not applicable; review the PRD for internal consistency and traceability.
- Handoff requirements: Present only the four decisions Arko must approve or change to close `PREREQ-001`.
- Stop conditions: Stop if a choice would redefine Sybill as a commerce or final-decision product.

### PREREQ-002: Define Decision Record And Precedent Corpus

- Status: CONFIRMED / COMPLETE
- Owner role: Product Spec Agent, with Data Model Agent input and Orchestrator review
- Spec reference: `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`, and `docs/product/PREREQ-002_TRACEABILITY_REVIEW.md`
- Objective: Obtain approval or changes for the proposed decision record, supporting objects, authority model, permissions, write-back workflow, invariants, and synthetic V1 corpus.
- Scope: Conceptual objects, required fields, identifiers, provenance, authority statuses and semantics, permitted state transitions, policy versions, citation-edge rules, invariants, permissions, failure cases, exact demo records, and acceptance criteria.
- Allowed files or ownership area: The PREREQ-002 proposal and approved `PREREQ-002` outputs under `docs/product/`; related product sections and append-only entries in `DECISIONS.md`.
- Required interfaces: Define the technology-neutral contracts later implementation tasks must consume.
- Exclusions: Database selection, API framework, UI implementation, retrieval implementation, model provider, and application code.
- Dependencies: PREREQ-001 is CONFIRMED / COMPLETE.
- Acceptance criteria: SATISFIED. All decision packages and ten detected issues are resolved; the approved specification and complete seed appendix define exact versioning, objects, fields, authority transitions, citations, relationships, permissions, fixtures, invariants, and negative cases; documentation traceability and referential-integrity review pass.
- Testing requirements: Specification review with example records and state-transition cases; no application tests yet.
- Handoff requirements: SATISFIED by the review packet, final specification, complete seed-data appendix, and traceability review.
- Stop conditions: Stop for Arko and Orchestrator approval if authority semantics, permissions, or shared contracts remain ambiguous.

### PREREQ-003: Define Initial Architecture And Ownership Map

- Status: UNRESOLVED / NEXT PLANNING GATE
- Owner role: Orchestrator / Integration Agent
- Spec reference: Approved PRD and `PREREQ-002` outputs.
- Objective: Propose the minimum architecture needed for one complete V1 loop and replace unresolved code ownership placeholders in `AGENT_BUILD_INSTRUCTIONS.md`.
- Scope: System boundaries, major components, data flow, shared schemas, interfaces, trust boundaries, deployment assumptions, test boundaries, and exact repository ownership paths.
- Allowed files or ownership area: `ARCHITECTURE.md`, `AGENT_BUILD_INSTRUCTIONS.md`, `DECISIONS.md`, and architecture notes under `docs/architecture/`.
- Required interfaces: Must preserve the approved product contracts from `PREREQ-002`.
- Exclusions: Application implementation, speculative scale architecture, unapproved integrations, and product-scope changes.
- Dependencies: PREREQ-001 and PREREQ-002 are CONFIRMED / COMPLETE; hackathon-specific technical constraints remain unresolved.
- Acceptance criteria: Every major component and interface is described; trust boundaries are explicit; each implementation role has non-overlapping default file ownership; all material technology choices are proposed for approval and logged after approval.
- Testing requirements: Architecture review against PRD flows, failures, and acceptance criteria.
- Handoff requirements: Provide alternatives considered, recommended option, consequences, unresolved choices, and proposed first bounded implementation task.
- Stop conditions: Stop before choosing architecture where product requirements or hackathon constraints are still materially unresolved.

## Unresolved Dependencies Blocking TASK-001

`TASK-001` must not be created until all material items below are resolved or explicitly deferred with a rationale:

- CONFIRMED: The V1 domain, primary user and buyer, representative matter, and human-confirmed write-back boundary were approved in `PREREQ-001`.
- CONFIRMED: The approved `PREREQ-002` outputs define exact record fields, version identifiers, provenance, authority semantics, transitions, citation rules, invariants, permissions, negative cases, and the synthetic corpus.
- UNRESOLVED: Define the minimum shared interface or schema that the first implementation task would consume or expose.
- UNRESOLVED: Define authorization and trust boundaries for record creation, authority changes, citation changes, and decision write-back to the extent relevant to the first task.
- UNRESOLVED: Approve the minimum architecture, repository structure, component boundaries, file ownership, runtime, dependency policy, and test approach required by the first task.
- UNRESOLVED: Record any event-specific hackathon technology restrictions that could invalidate the selected implementation approach, or explicitly confirm that none are known.
- UNRESOLVED: Identify the first vertical slice and give it observable functional and technical acceptance criteria without relying on unstated choices.

## TASK-001 Creation Gate

The Orchestrator may draft `TASK-001` only when:

1. Its governing product behavior is `CONFIRMED`.
2. Its referenced specification is approved and contains inputs, outputs, state changes, rules, permissions, failures, invariants, acceptance criteria, and out-of-scope behavior.
3. Its consumed and exposed interfaces are documented.
4. Its exact ownership area and expected files or components are known.
5. Its architecture and dependencies are approved in `ARCHITECTURE.md` and recorded in `DECISIONS.md` where material.
6. Its testing approach and required test cases are defined.
7. It can be completed and independently reviewed without another agent making a product or architecture decision.

## Current Expected Codex Delivery

- CONFIRMED: No application-code delivery is authorized yet.
- CONFIRMED: Codex must not scaffold a project, select a stack, add dependencies, define schemas in code, or implement product behavior before `TASK-001` exists.
- CONFIRMED: For an assigned prerequisite, Codex may deliver only the named repository documentation, decision proposals, examples, and traceability review within that prerequisite's scope.
- CONFIRMED: The first future implementation delivery must be exactly the files, behavior, tests, and documentation specified by an approved `TASK-001`; nothing outside that task is implied.

## Deferred Implementation Issue Groups

These groups are planning placeholders, not authorized implementation tasks:

- Project structure and development baseline.
- Shared schemas and synthetic corpus.
- Deterministic authority and citation validation.
- Precedent retrieval and ranking.
- Fact extraction and comparison.
- Precedent packet and brief generation.
- Decision write-back.
- API and service orchestration.
- Frontend workflow.
- QA, red-team, security, and model-boundary tests.
- Demo seed/reset flow.
- README, demo script, pitch material, and submission checklist.

No implementation group may be promoted to a bounded task until its governing specification, dependencies, file ownership, interfaces, acceptance criteria, tests, and stop conditions are recorded.
