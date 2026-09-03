# Finné Memory Product Requirements Document

## Document Status

- CONFIRMED: The active V1 use case, product thesis, owner-authority model, Sibyl Memory substrate role, Base execution role, deterministic/model split, and fresh-session demonstration are defined by `DECISION-022`.
- CONFIRMED: The `PREREQ-002` object model, authority semantics, invariants, and validation approach carry forward unchanged. Only its supplier-domain instantiation is superseded.
- CONFIRMED: Architecture is decided in `docs/architecture/PREREQ-003_ARCHITECTURE.md` under `DECISION-023`, approved and committed 2026-09-03.
- HISTORICAL: Supplier onboarding and procurement compliance was the V1 demo domain under `DECISION-010`. It is retained as historical design work and is no longer the active V1.
- CONFIRMED: The repository is licensed MIT under `DECISION-024`, satisfying the event's OSI-licence requirement.
- UNRESOLVED: `ORG-Q1` (Base mainnet versus Base Sepolia for the partner multiplier) in `HACKATHON_RULES.md`.
- UNRESOLVED: Implementation readiness. `SPEC-001` is proposed but not approved or committed, so no implementation task is authorized.

## Product Summary

Finné Memory converts an autonomous agent's remembered operating history into bounded authority for its next action.

> Sibyl lets agents remember. Finné determines what that memory authorizes them to do next.

Finné Memory is not generic agent memory. Sibyl Memory provides the persistent memory. Finné Memory operates above it, turning persisted experiences into structured precedents and using those precedents to derive a narrower, explainable action authority.

## Problem Statement

Autonomous agents can be given mechanical permissions: maximum spending limits, approved assets, approved contracts, approved protocols, approved functions, and permitted time windows. Those rules define what an agent is technically allowed to do. They do not capture the institutional meaning of the agent's previous performance.

Mechanical permissions do not answer:

- What happened when the agent exercised a similar permission before?
- Under what circumstances was the earlier action approved?
- What amount or scope was considered safe?
- Did the action succeed or fail?
- Was the earlier decision later questioned or withdrawn?
- What conditions made the earlier case safe?
- What is materially different now?
- What narrower authority has the agent earned from experience?

An agent with a 25,000 USDC ceiling and no memory of its own history will propose 25,000 USDC on its first day and on its hundredth. Finné Memory closes that gap.

## Product Principle

Memory says that something happened before. Precedent establishes that a past case is relevant, identifies whether it remains authoritative, and determines what narrower authority the agent has actually earned.

## Core Authority Model

The owner defines the hard permission ceiling. A representative ceiling is:

| Dimension | Owner ceiling |
| --- | --- |
| Maximum amount | 25,000 USDC |
| Approved network | Base |
| Approved asset | USDC |
| Approved action class | Capital deployment |
| Approved protocol or contract classes | Explicitly enumerated |
| Unknown situations | Constrained action or owner review |

Finné Memory may narrow the amount, narrow the permitted contract or function, add conditions, block an action, require escalation, or restore authority within the original owner ceiling when an owner-defined derivation policy permits it.

Finné Memory may never exceed the owner's permission ceiling; invent a new asset, contract, protocol, function, network, or action class; grant the agent powers the owner did not delegate; treat past success as unlimited authority; let the agent rewrite its own authority policy; or let a language model determine final authorization.

- CONFIRMED: The owner ceiling is always superior to learned authority.
- CONFIRMED: Effective authority is the strictest combination of the owner permission ceiling, current hard policy, active remembered precedents, learned constraint, and current action facts.

The deterministic formulation is conceptually:

```
effective_authority = intersection(
    owner_permission_ceiling,
    current_hard_policy,
    active_precedent_constraints,
    learned_constraint,
    current_action_scope
)
```

The implementation may differ in form, but the invariant is absolute: effective authority can never exceed owner authority.

## System Roles

### Sibyl Memory — mandatory persistent substrate

Sibyl Memory stores and recalls, across genuinely fresh sessions: past action proposals, relevant context, owner permissions, permission decisions, constraints applied, actions taken, Base transaction references, observed outcomes, incidents, precedent status, and later treatment.

- CONFIRMED: Sibyl Memory is the sole source of truth for remembered agent experiences.
- CONFIRMED: The application writes important state directly into Sibyl Memory and retrieves it in a fresh process.
- CONFIRMED: No competing generic memory database is built. Supabase, PostgreSQL, pgvector, Pinecone, and other databases are prohibited as the store of remembered agent experiences.
- CONFIRMED: If Sibyl Memory is removed, the agent loses the operating history required to derive learned authority, and the product must materially degrade or fail safely.

### Finné Memory — authority layer

Finné Memory operates above Sibyl Memory and provides the owner permission model, decision schema, precedent construction, precedent comparison, material-difference detection, authority-state treatment, learned-constraint derivation, deterministic action authorization, readable explanation, and outcome feedback.

### Base — execution and evidence layer

Finné derives the permitted action, the agent executes that permitted action on Base, the transaction result becomes outcome evidence, the outcome is written into Sibyl Memory, and a future fresh session recalls and uses it.

- CONFIRMED: Base performs genuine work and is not a decorative integration.
- CONFIRMED: Base is used for authorized execution and outcome evidence only. It does not make this an agent-commerce product.

## Target Users

- CONFIRMED: The primary user is the owner or operator of an autonomous onchain treasury agent who must delegate spending authority without granting unbounded discretion.
- CONFIRMED: The primary buyer is the treasury, risk, or operations function accountable for what a delegated agent is permitted to do.
- CONFIRMED: The consumer of the authorization output is the agent runtime itself, which is bounded by the result.
- UNRESOLVED: Buyer organization size, deployment environment, decision volume, regulated-industry requirements, and production role structure.

## Active V1 Use Case

- CONFIRMED: An autonomous treasury agent uses remembered operating history to determine its bounded authority for a materially similar Base action in a fresh session.
- CONFIRMED: The representative matter is whether a proposed Base capital-deployment action, made against a 25,000 USDC owner ceiling, is authorized in full, narrowed, blocked, or escalated on the evidence of the agent's own recorded history.
- CONFIRMED: Finné Memory determines the authority bound. It does not select the business action within that bound.

## V1 Product Journey

1. The agent proposes an action with structured facts: network, asset, amount, contract, function, and action class.
2. Finné Memory loads the owner permission ceiling and current hard policy from owner-controlled configuration.
3. Finné Memory retrieves candidate prior cases from Sibyl Memory.
4. Finné Memory checks each candidate's authority state; only `active` cases are eligible to support learned authority.
5. Finné Memory compares material facts and detects material differences.
6. Finné Memory derives the learned constraint and intersects all five authority inputs.
7. Finné Memory emits an `AuthorizationDecision` — allow, constrain, block, or escalate — with a readable, citation-backed explanation.
8. The agent executes only within the authorized bound on Base.
9. The transaction reference and observed outcome are written back into Sibyl Memory as new evidence.
10. An owner confirmation event promotes the recorded case to `active` precedent, available to a future fresh session.

## Required V1 Capabilities

- Represent an owner permission ceiling and hard policy in owner-controlled configuration that Finné Memory reads but never writes.
- Persist a complete case — proposal, context, material facts, owner ceiling, constrained authority, decision, action, Base transaction reference, observed outcome, supporting evidence, and precedent status — into Sibyl Memory.
- Retrieve prior cases from Sibyl Memory in a genuinely fresh process with no carried-over in-process state.
- Distinguish factual similarity from authoritative eligibility.
- Detect material differences between the current proposal and a candidate precedent.
- Derive a learned constraint from active precedents only.
- Compute effective authority as a strict intersection that can never exceed the owner ceiling.
- Emit an `AuthorizationDecision` with an auditable explanation naming the precedents relied upon and the binding constraint.
- Execute a safe Base action within the authorized bound and record the transaction reference.
- Write the observed outcome back into Sibyl Memory.
- Fail safely when memory is missing, malformed, contradictory, withdrawn, or unavailable.

## Precedent Model

The `PREREQ-002` model is retained: immutable matter versions, immutable decision versions, facts, evidence, sources, canonical fact-evidence links, policy versions, validated citations, precedent relationships, append-only authority events, owner confirmation, provenance, and rejected citation-attempt audit events.

- CONFIRMED: Authority states are `draft`, `active`, `questioned`, `superseded`, and `withdrawn`.
- CONFIRMED: Only `active` precedents may support learned authority.
- CONFIRMED: Withdrawn and superseded cases may be retrieved and displayed but cannot authorize an action.
- CONFIRMED: Precedent relationships are `follows`, `distinguishes`, `questions`, and `supersedes`.
- CONFIRMED: Similarity, authority, and outcome remain separate. A highly similar precedent may be withdrawn; a less similar precedent may remain active.
- CONFIRMED: A model may suggest a relationship or a material difference. Only deterministic validation and an authorized confirmation path may persist or apply it.

## Active Demo Corpus

The exact synthetic corpus, fixtures, authority histories, and expected authorization outcomes for the active V1 are defined in `docs/product/ACTIVE_DEMO_DESIGN.md`.

- HISTORICAL: `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md` remains the validated supplier-domain corpus. It is preserved as historical design work and is not the active demo corpus.

## Deterministic Responsibilities

The deterministic system owns the owner permission ceiling; effective action authority; permission intersection; amount limits; approved network, asset, contract, protocol, and function scope; authority states; authority transitions; terminal-state enforcement; valid citations; precedent eligibility; policy versions; exact identifier resolution; outcome recording; safe fallback behaviour; the final allow, constrain, block, or escalate result; and the prohibition on exceeding owner authority.

- CONFIRMED: The deterministic system must work with no model API key present.

## Model Responsibilities

The model may assist with extracting proposed facts from natural language, suggesting comparable precedents, explaining factual similarities, explaining material differences, drafting a readable precedent explanation, and proposing follow or distinguish treatment.

The model may not expand authority, authorize an action, change an authority state, create a valid citation, confirm a precedent, sign a transaction, hold a private key, submit a Base transaction, or bypass deterministic rules.

## Product Surfaces

- Action proposal input with structured facts.
- Owner policy display showing the ceiling and hard policy in force.
- Retrieved precedent candidates with similarity and authority shown separately.
- The `AuthorizationDecision` with its binding constraint and readable explanation.
- Base execution result with transaction reference.
- Outcome write-back and owner confirmation.
- Demo seed and reset control.

ASSUMPTION: These are logical surfaces. The concrete interface is decided in `docs/architecture/PREREQ-003_ARCHITECTURE.md`.

## System Boundaries

Finné Memory is responsible for representing owner authority, converting remembered operating history into structured precedent, deriving learned constraints, and emitting a deterministic, explainable authorization bound.

Finné Memory is not responsible for:

- Selecting the business action within the authorized bound.
- Custody of funds or private keys.
- Providing persistent memory itself; that is Sibyl Memory's role.
- Payments, escrow, refunds, settlement, transaction disputes, x402 flows, or service-delivery verification.
- Verifying real-world truth beyond the evidence supplied to it.

## Non-Overlap With Finné And x402

- CONFIRMED: Finné Memory is not a payment, escrow, refund, settlement, transaction-dispute, or service-delivery verification product.
- CONFIRMED: Finné Memory does not process x402 payments, hold funds, arbitrate transactions, or determine whether a purchased service was delivered.
- CONFIRMED: Those capabilities belong to the separate Finné/x402 product direction and are outside Finné Memory's scope.
- CONFIRMED: Base is used for authorized execution and outcome evidence, not to convert this into an agent-commerce product.
- CONFIRMED: No agent may redefine Finné Memory to include those capabilities.

## Failure States

The V1 must define observable behavior for:

- Sibyl Memory unavailable, uninitialised, or unauthenticated.
- No relevant precedent found (cold start).
- Similar precedent found but not `active`.
- Withdrawn or superseded precedent retrieved.
- Conflicting active precedents.
- Materially different facts against an otherwise comparable precedent.
- Requested amount above the owner ceiling.
- Malformed or contradictory memory records.
- Model unavailable or returning malformed output.
- Base transaction failure, revert, or timeout.
- Duplicate execution of the same authorized action.

- CONFIRMED: Every one of these resolves to constrain, block, or escalate. None may resolve to a wider authority than the safe default.

## Security And Trust Boundaries

- CONFIRMED: Model output is untrusted until validated against deterministic records and schemas.
- CONFIRMED: Authority state, effective authority, and citation validity cannot be changed by model-generated text.
- CONFIRMED: The owner ceiling lives in owner-controlled configuration that the agent cannot write.
- CONFIRMED: The agent may not rewrite its own authority policy.
- CONFIRMED: Only the Base adapter holds signing capability. No key material is written to Sibyl Memory, the repository, or any log.
- CONFIRMED: Records retrieved from memory are validated on read; a malformed record is treated as absent, not as permission.
- UNRESOLVED: Authentication, multi-tenant boundaries, audit retention, and production key management beyond the demo.

## Product-Level Acceptance Criteria

V1 is product-complete for the demo when:

1. Session 1 establishes a constrained 10,000 USDC authority under a 25,000 USDC owner ceiling and persists the complete case to Sibyl Memory.
2. Session 1's process terminates completely, with no carried-over in-process state.
3. Session 2 starts fresh, proposes the broader 25,000 USDC action, and is bounded to 10,000 USDC by precedent retrieved from Sibyl Memory.
4. The changed action is visible and attributable to the recalled memory, naming the precedent relied upon.
5. With Sibyl Memory removed or emptied, Session 2 cannot derive the learned authority and falls back to constrain, block, or require owner approval.
6. A withdrawn precedent is retrievable and displayable but cannot authorize an action.
7. A materially different proposal is not silently allowed to follow the precedent.
8. A request above the owner ceiling is blocked regardless of precedent.
9. The deterministic path produces identical authorization results with no model API key present.
10. A safe Base action executes within the authorized bound and its transaction reference is recorded and written back to memory.
11. Base failure produces no false success and no fabricated outcome record.
12. The demo can be reset and rehearsed from a known starting state.
13. No V1 behavior implements payments, escrow, x402, refunds, settlement, transaction disputes, or service-delivery verification.

UNRESOLVED: Quantitative retrieval quality, latency, reliability, accessibility, and performance thresholds.

## Demo Requirements

The demo must make the following legible to judges within 2 to 5 minutes:

- The delegation problem: mechanical permissions do not encode earned trust.
- Session 1 establishing constrained authority and persisting it.
- A genuine process termination between sessions.
- The fresh-session recall moment, shown as one continuous unedited segment.
- The action changing from 25,000 USDC proposed to 10,000 USDC authorized, attributed to the recalled precedent.
- A genuine Base transaction executed within the bound.
- The memory-deleted control showing safe degradation.
- The boundary between deterministic authority and model assistance.

## Risks And Mitigations

- Risk: The product reads as generic agent memory. Mitigation: state plainly that Sibyl Memory provides memory and Finné Memory provides bounded authority; show the authority computation, not the storage.
- Risk: The memory integration reads as decorative. Mitigation: the memory-deleted control is part of the demo and part of the test suite.
- Risk: Judges believe a model is deciding authorization. Mitigation: run the demo with no model API key present.
- Risk: Base appears bolted on. Mitigation: the authorized amount is carried in the onchain authorization receipt and the transaction result is the outcome evidence written back to memory.
- Risk: Scope drifts toward Finné/x402. Mitigation: enforce the non-overlap rule in the PRD, agent instructions, tasks, and reviews.
- Risk: `ORG-Q1` resolves against Base Sepolia. Mitigation: keep the network a single configuration value.

## Out Of Scope For V1

- Payment, escrow, x402, refund, settlement, or transaction-dispute behavior.
- Selecting the business action within the authorized bound.
- Custody, treasury management, or portfolio strategy.
- Virtuals Protocol integration.
- Broad multi-domain precedent support.
- Production-scale corpus ingestion, migration, or compliance certification.
- Any capability not required for the two-session vertical slice.

## Open Decisions Before Coding

- CONFIRMED: `DECISION-022` records the controlled domain pivot and the active V1 use case.
- CONFIRMED: `DECISION-023` and `docs/architecture/PREREQ-003_ARCHITECTURE.md` are approved and committed.
- PROPOSED: `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md` requires Arko's approval and a commit before implementation may begin.
- RESOLVED: `ORG-Q2` — the repository is licensed MIT under `DECISION-024`.
- UNRESOLVED: `ORG-Q1` — Base mainnet versus Base Sepolia for the partner multiplier.
