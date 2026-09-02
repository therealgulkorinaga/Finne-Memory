# Finné Memory Product Requirements Document

## Document Status

- CONFIRMED: Finné Memory's product identity, non-commerce boundary, V1 decision-support loop, deterministic/model responsibility split, target user and buyer, representative matter, human write-back boundary, and `PREREQ-002` data contract.
- CONFIRMED: Supplier onboarding and procurement compliance is the V1 demo domain.
- CONFIRMED: `PREREQ-002` defines matter and decision versioning, facts, evidence, sources, authority events and transitions, citations, precedent relationships, policy dates, product permissions, invariants, and the complete synthetic corpus.
- UNRESOLVED: Retrieval ranking, packet schema beyond the exact matter-version reference, technical authorization, interfaces, implementation architecture, integrations, and quantitative success thresholds.
- DEFERRED: Product capabilities beyond the single V1 precedent loop.
- UNRESOLVED: Implementation readiness. `TASK-001` remains reserved until the prerequisites and creation gate in `TASKS.md` are satisfied.

## Product Summary

Finné Memory gives autonomous systems institutional memory and precedent for consequential decisions. It records consequential decisions with their evidence, sources, reasoning, and authority status. For a new matter, it retrieves relevant past decisions, checks whether they remain authoritative, compares the facts, and produces a cited precedent brief.

Finné Memory does not make the final decision. Its primary output is a structured, cited `PrecedentPacket` for a human, agent, or downstream system to use when making that decision.

## Problem Statement

AI agents and automated systems increasingly make recurring consequential decisions, but commonly treat each matter as a fresh reasoning event. Ordinary memory can show that something happened before; it does not establish which past decisions are relevant, whether they remain authoritative, or why current facts should lead a system to follow, distinguish, question, or ignore them.

Human institutions address this through precedent, policy histories, citations, authority rules, and audit trails. Finné Memory provides an equivalent decision-memory layer for autonomous systems.

## Product Principle

Memory says that something happened before. Precedent establishes that a past decision is relevant, identifies whether it remains authoritative, and explains how it should inform the current matter.

## Non-Overlap With Finné And x402

- CONFIRMED: Finné Memory is not a payment, escrow, refund, settlement, transaction-dispute, or service-delivery verification product.
- CONFIRMED: Finné Memory does not process x402 payments, hold funds, arbitrate transactions, or determine whether a purchased service was delivered.
- CONFIRMED: Those capabilities belong to the separate Finné/x402 product direction and are outside Finné Memory's scope.
- CONFIRMED: No agent may redefine Finné Memory to include those capabilities.

## Target Users

- CONFIRMED: The primary user is a supplier-risk or procurement-compliance professional using an automated decision system.
- CONFIRMED: The primary buyer is the procurement, supplier-risk, or compliance function of an organization operating repeatable supplier-onboarding decisions.
- CONFIRMED: A downstream consumer may be a human, an AI agent, or another automated system.
- UNRESOLVED: Buyer organization size, deployment environment, decision volume, regulated-industry requirements, and production role structure.

## V1 Use Case

- CONFIRMED: V1 demonstrates supplier onboarding and procurement compliance.
- CONFIRMED: The representative matter is whether a supplier with incomplete beneficial-ownership evidence should be approved, rejected, or escalated.
- CONFIRMED: Finné Memory supplies precedent analysis but does not select the final outcome.

This domain is the current candidate because it has structured evidence, policies, exceptions, repeat decisions, meaningful authority changes, and an understandable distinction between similarity and authority.

## V1 Product Journey

1. A user or agent submits a new decision matter.
2. Finné Memory extracts structured facts from supplied material or receives already-structured facts.
3. Finné Memory retrieves similar past decisions.
4. Finné Memory checks each candidate's authority status.
5. Finné Memory compares the current matter with the past decisions.
6. Finné Memory produces a structured `PrecedentPacket` and a readable precedent brief with validated citations.
7. A downstream human, agent, or system makes the final decision outside Finné Memory.
8. CONFIRMED: After the downstream decision is made, an authorized human explicitly confirms whether it may enter Finné Memory's precedent corpus.

UNRESOLVED: Whether model-assisted fact extraction requires human confirmation before packet generation remains a later product-behavior decision.

CONFIRMED: Write-back permissions, deterministic validation, immutable draft creation, and the separate authority-activation event are defined by the approved `PREREQ-002` contract.

## Required V1 Capabilities

- Accept a new decision matter with facts and supporting material.
- Represent a small synthetic corpus of prior decisions and their authority relationships.
- Retrieve precedents by factual relevance.
- Distinguish factual similarity from authoritative eligibility.
- Validate source and citation references against deterministic records.
- Explain similarities and differences between the current matter and candidate precedents.
- Produce a structured, cited `PrecedentPacket` and human-readable `PrecedentBrief`.
- Permit an authorized, human-confirmed result to be saved as an immutable draft decision version under the approved deterministic rules.

## Synthetic Demo Corpus

The V1 demo corpus must be intentionally small and must contain:

- One original baseline decision.
- One decision that follows the baseline.
- One decision that distinguishes the baseline because of different facts.
- One decision that supersedes an older rule or decision.
- One highly similar decision that is no longer authoritative.
- One less-similar decision that remains active.
- One current matter that requires Finné Memory to explain the difference between similarity and authority.

CONFIRMED: Exact synthetic records, evidence, policy language, dates, authority histories, and the expected no-outcome packet behavior for the current matter are defined in the approved `PREREQ-002` outputs.

## Conceptual Data Requirements

The product specification must define these concepts before implementation:

- `DecisionRecord`
- `DecisionMatter`
- `Fact`
- `Evidence`
- `Source`
- `PolicyVersion`
- `CitationEdge`
- `AuthorityStatus`
- `PrecedentCandidate`
- `PrecedentPacket`
- `PrecedentBrief`

CONFIRMED: Approved fields, exact-version identity, cardinality, mutability, provenance, authority history, and corpus relationships are defined in `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`. Physical serialization remains deferred to `PREREQ-003`.

## Deterministic Responsibilities

The deterministic system owns:

- Precedent authority status.
- Source and decision identifiers.
- Citation relationships.
- Supersession relationships.
- Policy version dates.
- Authority state and transition validity.
- Whether a citation references valid records.
- Whether a precedent is eligible to be treated as active authority.
- CONFIRMED: One explicit `DecisionMatter.relevant_at` date selects the applicable policy version and authority snapshot; record `created_at` and downstream `decided_at` remain separate.
- CONFIRMED: Human write-back confirmation and subsequent authority activation are separate timestamped audit events; activation cannot occur implicitly during confirmation.

CONFIRMED: The V1 authority vocabulary is `draft`, `active`, `questioned`, `superseded`, and `withdrawn`; only `active` is eligible as active authority. Exact transitions and invariants are defined in the approved `PREREQ-002` contract.

## Probabilistic AI Responsibilities

The AI/model may assist with:

- Extracting facts from unstructured text.
- Comparing facts across matters.
- Explaining similarities and differences.
- Drafting the precedent brief from validated structured data.
- Suggesting that a precedent may be followed or distinguished.
- Rendering structured results in readable language.

The AI/model must not:

- Invent sources or decision identifiers.
- Declare a precedent active, superseded, or otherwise authoritative.
- Change authority state.
- Create an accepted citation relationship without deterministic validation.
- Make the final decision.
- Override deterministic rules.

UNRESOLVED: Model provider, prompting strategy, confidence representation, evaluation approach, fallback behavior, and whether any model suggestions are persisted.

## Product Surfaces

The V1 needs enough interface to demonstrate the complete loop. Candidate surfaces are:

- Matter submission.
- Extracted or supplied facts.
- Retrieved precedent candidates with similarity and authority shown separately.
- Precedent packet and readable brief with citations.
- Decision write-back.
- Demo seed/reset control.

ASSUMPTION: These are logical product surfaces, not confirmed screens or routes. Their grouping and interaction design remain unresolved.

## System Boundaries

Finné Memory is responsible for recording and retrieving decision precedent, validating deterministic authority and citation facts, and producing evidence-backed precedent analysis.

Finné Memory is not responsible for:

- Making or enforcing the final business decision.
- Executing procurement approval or rejection in an external system.
- Verifying real-world truth beyond the evidence supplied to it.
- Payments, escrow, refunds, settlement, transaction disputes, or x402 flows.
- Replacing an organization's source policies or systems of record.

UNRESOLVED: Which external systems, if any, are integrated in V1 and which system is authoritative for identity, policy, evidence, and final outcomes.

## Failure States

The V1 specification must define observable behavior for:

- No relevant precedent found.
- Similar precedent found but no active authority found.
- Conflicting active precedents.
- Missing or invalid source references.
- Citation to a nonexistent or ineligible record.
- Incomplete facts or evidence.
- Malformed or unavailable model output.
- Retrieval or storage failure.
- Unauthorized write-back or authority-state change.

UNRESOLVED: Exact user-facing states, retry behavior, degraded-mode behavior, and which failures block packet generation.

## Security And Trust Boundaries

- CONFIRMED: Model output is untrusted until checked against deterministic records and schemas.
- CONFIRMED: Authority state and citation validity cannot be changed by model-generated text.
- CONFIRMED: The final decision remains outside Finné Memory.
- CONFIRMED: Unverified or disputed facts remain visible with status and provenance but cannot support an authoritative conclusion.
- CONFIRMED: A Matter Submitter may submit and view analysis; a Decision Reviewer may record an external outcome and confirm write-back; an Authority Steward may maintain authority metadata; an Automated Client may submit and consume packets but may not confirm write-back or change authority.
- UNRESOLVED: Authentication, exact authorization rules, role combinations, tenant boundaries, audit retention, sensitive-data handling, and whether authority stewardship is exposed in the V1 interface.

## Product-Level Acceptance Criteria

V1 is product-complete for the demo when:

1. A prepared current matter can complete the full product journey from submission through cited packet generation.
2. The demo corpus includes every scenario listed in the synthetic corpus section.
3. The result presents factual similarity separately from authority status.
4. A highly similar but non-authoritative precedent is not represented as active authority.
5. Every cited decision and source can be resolved to a deterministic record, and invalid citations are rejected or clearly surfaced.
6. The brief explains material similarities and differences using only supplied facts and validated references.
7. Model output cannot change authority status, create an accepted citation edge without validation, or make the final decision.
8. CONFIRMED: The demonstrated result can enter the precedent corpus only after the downstream decision is made and an authorized human explicitly confirms it.
9. Model unavailability or malformed output produces a defined failure or degraded state without corrupting deterministic data.
10. The exact demo can be reset and rehearsed from a known starting state.
11. No V1 behavior implements payments, escrow, x402, refunds, settlement, transaction disputes, or service-delivery verification.

UNRESOLVED: Quantitative retrieval quality, latency, reliability, accessibility, privacy, and performance thresholds.

## Demo Requirements

The demo must make the following legible to judges:

- The recurring decision problem and why ordinary memory is insufficient.
- The difference between similarity and authority.
- A superseded or otherwise inactive precedent being handled correctly.
- Validated citations linking the brief to source records.
- The boundary between deterministic rules and model assistance.
- The downstream actor retaining final decision authority.
- A new decision becoming available as future precedent.

CONFIRMED: The demo uses the supplier-onboarding scenario described above.

## Risks And Mitigations

- Risk: The product looks like generic retrieval-augmented generation. Mitigation: demonstrate explicit authority states, supersession, citation validation, and similarity-versus-authority reasoning.
- Risk: Generated prose invents support. Mitigation: constrain generation to validated records and reject unresolved citations.
- Risk: Judges believe Finné Memory autonomously decides outcomes. Mitigation: show the `PrecedentPacket` as decision support and make the downstream decision boundary explicit.
- Risk: Scope drifts toward Finné/x402. Mitigation: enforce the non-overlap rule in the PRD, agent instructions, tasks, and reviews.
- UNRESOLVED: Domain-specific risks concerning procurement data, fairness, policy interpretation, and regulatory obligations.

## Out Of Scope For V1

- Payment, escrow, x402, refund, settlement, or transaction-dispute behavior.
- Final autonomous outcome selection or enforcement.
- Broad multi-domain precedent support.
- Production-scale corpus ingestion or migration.
- Production compliance certification.
- Unapproved sponsor integrations.
- Any capability not required for the single end-to-end V1 loop.

## Open Decisions Before Coding

- CONFIRMED: The four product decision packages in `docs/product/PREREQ-001_PRODUCT_DEFINITION_PROPOSAL.md` were approved, closing `PREREQ-001`.
- CONFIRMED: The `PREREQ-002` decision-record contract and complete synthetic seed-data appendix were approved, closing `PREREQ-002`.
- UNRESOLVED: Establish observable product behavior for failure states not governed by the approved `PREREQ-002` contract.
- UNRESOLVED: Define retrieval relevance, ranking requirements, and the complete `PrecedentPacket` contract without selecting technology prematurely.
- UNRESOLVED: Decide whether any external integration is necessary for the V1 demo.
- UNRESOLVED: Set measurable demo and non-functional acceptance thresholds.
- UNRESOLVED: Complete `PREREQ-003` and approve architecture, interfaces, repository layout, runtime, dependencies, testing, and known hackathon restrictions before creating `TASK-001`.
