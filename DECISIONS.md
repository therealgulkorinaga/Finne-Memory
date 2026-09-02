# Decision Log

This file records product, architecture, and process decisions.

## Decision Format

Each decision should use this structure:

- ID: `DECISION-000`
- Date: `YYYY-MM-DD`
- Type: `Product | Architecture | Process`
- Status: `Proposed | Accepted | Superseded`
- Context: UNRESOLVED
- Decision: UNRESOLVED
- Consequences: UNRESOLVED
- Related Tasks: UNRESOLVED

## Decisions

### DECISION-001: Sybill Product Identity And Commerce Boundary

- ID: `DECISION-001`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Sybill must remain distinct from the separate Finné/x402 product direction.
- Decision: Sybill is a machine precedent layer for autonomous decision-making. It records and retrieves decision precedent, checks deterministic authority and citations, compares facts, and produces cited decision support. It is not a payment, escrow, x402, refund, settlement, transaction-dispute, or service-delivery verification product.
- Consequences: Product specs, tasks, agent prompts, reviews, and submission material must preserve this boundary. Any proposed commerce behavior is a scope conflict and must stop for review.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`

### DECISION-002: Sybill Produces Decision Support, Not Final Decisions

- ID: `DECISION-002`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: The system needs a clear responsibility boundary between precedent analysis and consequential outcome selection.
- Decision: Sybill's primary output is a structured, cited `PrecedentPacket` and readable brief. A downstream human, agent, or system makes the final decision.
- Consequences: Product flows and interfaces must expose decision support without representing Sybill as the final authority. Write-back records the resulting decision only under rules still to be specified.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`

### DECISION-003: Deterministic Authority Boundary For Model Assistance

- ID: `DECISION-003`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Model-assisted analysis must not control authoritative records or fabricate support.
- Decision: Deterministic behavior owns authority status, identifiers, citation and supersession relationships, policy dates, authority hierarchy, citation validity, and active-authority eligibility. Models may assist with extraction, comparison, explanation, and drafting, but may not invent records, alter authority, create accepted citations without validation, override deterministic rules, or make the final decision.
- Consequences: Shared schemas and authority semantics must be specified before implementation. Model outputs require validation and explicit failure behavior.
- Related Prerequisites: `PREREQ-002`, `PREREQ-003`

### DECISION-004: Separate Product, Task, And Agent-Governance Artifacts

- ID: `DECISION-004`
- Date: `2026-09-02`
- Type: `Process`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: The PRD alone does not tell specialized coding agents how to divide work without conflict.
- Decision: Maintain `PRD.md`, `TASKS.md`, and `AGENT_BUILD_INSTRUCTIONS.md` as separate source-of-truth artifacts. The PRD defines the product, the task registry defines bounded work, and the agent instructions define ownership, roles, interfaces, handoffs, review, commits, forbidden changes, and escalation.
- Consequences: Implementation cannot begin until the assigned task, governing spec, ownership, interfaces, acceptance criteria, tests, and stop conditions are clear across these documents.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`, `PREREQ-003`

### DECISION-005: Supplier Onboarding As Candidate V1 Demo Domain

- ID: `DECISION-005`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Superseded`
- Classification: PROPOSED
- Context: The preliminary product write-up identifies supplier onboarding and procurement compliance as a judge-legible domain with evidence, policies, exceptions, and superseded precedent.
- Decision: Use supplier onboarding as the working V1 demo domain, centered on incomplete beneficial-ownership evidence, pending explicit confirmation by Arko.
- Consequences: Product specifications may use this scenario for planning, but implementation must not begin until Arko accepts or changes the proposal and later prerequisites are complete.
- Related Prerequisites: `PREREQ-001`
- Resolution: Confirmed by `DECISION-010`.

### DECISION-006: Reserve TASK-001 Until Implementation Prerequisites Are Approved

- ID: `DECISION-006`
- Date: `2026-09-02`
- Type: `Process`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: The repository was reviewed to determine whether one small implementation task could be assigned without undocumented product or architecture choices.
- Decision: Do not create `TASK-001` yet. Rename the current specification work as `PREREQ-001` through `PREREQ-003`, reserve `TASK-001` for the first actual implementation task, and create it only after the readiness gate in `TASKS.md` is satisfied.
- Consequences: Codex is not authorized to implement application code. Product decisions, `SPEC-001`, architecture, interfaces, ownership, and testing requirements must be approved first.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`, `PREREQ-003`

### DECISION-007: Candidate V1 User And Buyer

- ID: `DECISION-007`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Superseded`
- Classification: PROPOSED
- Context: `PREREQ-001` requires a specific primary user and buyer for the supplier-onboarding V1.
- Decision: Use a supplier-risk or procurement-compliance professional as the primary user and the organization's procurement, supplier-risk, or compliance function as the primary buyer.
- Consequences: The V1 workflow, language, permissions, and demo must serve an accountable professional using an automated decision system. This remains non-binding until Arko approves or changes it.
- Related Prerequisites: `PREREQ-001`
- Resolution: Confirmed by `DECISION-011`.

### DECISION-008: Candidate Representative Supplier Matter

- ID: `DECISION-008`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Superseded`
- Classification: PROPOSED
- Context: The V1 needs one concrete matter that demonstrates evidence gaps, precedent comparison, and the difference between similarity and authority.
- Decision: Use the question of whether a supplier with incomplete beneficial-ownership evidence should be approved, rejected, or escalated.
- Consequences: `SPEC-001` will define a synthetic corpus and current matter around this question if Arko approves it. Sybill will still provide precedent support rather than select the outcome.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`
- Resolution: Confirmed by `DECISION-012`.

### DECISION-009: Candidate Human Confirmation Boundary For Write-Back

- ID: `DECISION-009`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Superseded`
- Classification: PROPOSED
- Context: A completed external decision may become future precedent, but automated or model-generated output must not silently enter the authoritative corpus.
- Decision: Require explicit confirmation by an authorized human before a completed external decision is written into Sybill's precedent corpus.
- Consequences: Automated clients and models may not confirm write-back. Exact roles, validation, initial authority state, and record schema remain for `PREREQ-002` after Arko approves or changes this boundary.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`
- Resolution: Confirmed with clarification by `DECISION-013`.

### DECISION-010: Confirm Supplier Onboarding As V1 Domain

- ID: `DECISION-010`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: `DECISION-005` proposed supplier onboarding and procurement compliance as the V1 domain.
- Decision: Supplier onboarding and procurement compliance is the confirmed V1 domain.
- Consequences: V1 specifications, corpus fixtures, acceptance criteria, and demo materials will use this domain unless a later decision explicitly supersedes it.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`

### DECISION-011: Confirm Primary User And Buyer

- ID: `DECISION-011`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: `DECISION-007` proposed a primary user and organizational buyer for the V1 domain.
- Decision: The primary user is a supplier-risk or procurement-compliance professional. The primary buyer is the organization's procurement, supplier-risk, or compliance function.
- Consequences: Product workflows and language must support an accountable professional using an automated decision system.
- Related Prerequisites: `PREREQ-001`

### DECISION-012: Confirm Representative Matter

- ID: `DECISION-012`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: `DECISION-008` proposed a concrete supplier matter for the V1 precedent workflow.
- Decision: The representative matter is whether a supplier with incomplete beneficial-ownership evidence should be approved, rejected, or escalated.
- Consequences: The synthetic corpus and current-matter fixture must demonstrate this question without allowing Sybill to choose the final outcome.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`

### DECISION-013: Confirm Final-Decision And Human Write-Back Boundary

- ID: `DECISION-013`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: `DECISION-002` established decision support, and `DECISION-009` proposed the human-confirmation boundary for corpus entry.
- Decision: Sybill produces a cited precedent packet but does not make the final supplier decision. After the downstream decision has been made, it may enter Sybill's precedent corpus only after explicit confirmation by an authorized human.
- Consequences: Models and automated clients cannot make the outcome authoritative or confirm corpus entry. `PREREQ-002` must define the exact confirmation, validation, and initial-authority workflow.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`

### DECISION-014: Partial Approval Of PREREQ-002 Direction

- ID: `DECISION-014`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Arko reviewed the thirteen PREREQ-002 decision packages but withheld blanket approval for the detailed object schema, synthetic fixtures, and invariant set pending exact review.
- Decision: Approve packages `P2-02` through `P2-10` and `P2-12` in principle with amendments: unverified or disputed facts remain visible but cannot support authoritative conclusions; `DecisionMatter.relevant_at` alone selects applicable policy while record `created_at` and `decided_at` remain separate; reviewer confirmation and steward authority action are distinct timestamped events; confirmation creates an immutable draft version and activation appends a separate authority event; `DR-005` remains retrievable but excluded from active authority, while `DR-004` is the active baseline and Sybill produces no outcome.
- Consequences: `P2-01`, `P2-11`, and `P2-13` remain unresolved. `PREREQ-002` cannot close until the exact object fields, fixtures, invariants, and detected model inconsistencies are reviewed and reconciled.
- Related Prerequisites: `PREREQ-002`

### DECISION-015: Exact Matter And Decision Version Identity

- ID: `DECISION-015`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Stable aggregate IDs and sequence numbers cannot safely identify a corrected immutable version in citations, relationships, packets, or authority history.
- Decision: Use stable `matter_id` and `decision_id` across versions; globally unique immutable `matter_version_id` and `decision_version_id` for exact references; and sequential `matter_version` and `record_version` for human-readable order. Every packet binds one exact matter version, edits after packet generation create a new matter version, and every exact decision reference uses `decision_version_id`.
- Consequences: `relevant_at` and facts cannot change retrospectively. Decision records copy `relevant_at` and preserve separate `created_at` and `decided_at`.
- Related Prerequisites: `PREREQ-002`, `PREREQ-003`

### DECISION-016: Canonical Append-Only Authority, Evidence, And Relationship Model

- ID: `DECISION-016`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Mutable embedded lists would conflict with immutable decision versions and could attach authority or precedent treatment to the wrong version.
- Decision: Keep authority and precedent relationships outside immutable `DecisionRecord` content. Use append-only `AuthorityEvent` objects referencing exact decision versions, validated `PrecedentRelationship` objects for treatment, and canonical `FactEvidenceLink` objects for fact/evidence relationships. Expose reverse lists and current authority only as derived views.
- Consequences: Confirmation and activation remain separate audit events. Supersession references exact successor versions and is atomic with the corresponding relationship.
- Related Prerequisites: `PREREQ-002`, `PREREQ-003`

### DECISION-017: Valid Citation Domain And Policy Simplicity

- ID: `DECISION-017`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Invalid citation attempts and an undefined policy rank would introduce ambiguous deterministic behavior.
- Decision: Persist only validated `CitationEdge` objects in the domain graph; record rejected or unresolved attempts as separate audit events. Remove `PolicyVersion.authority_rank` from V1 and infer no policy hierarchy. New policy versions do not automatically change decision authority.
- Consequences: Invalid attempts never appear as supporting citations. Authority changes caused by policy developments require explicit Authority Steward events.
- Related Prerequisites: `PREREQ-002`, `PREREQ-003`

### DECISION-018: Approve SPEC-001 Corpus And Invariants

- ID: `DECISION-018`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Closure of `PREREQ-002` required exact review of the object model, complete fixture data, authority transitions, and deterministic invariants.
- Decision: Approve `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, its complete synthetic seed-data appendix, and the amended deterministic invariants. Retain six primary demo decisions and add two non-primary lifecycle fixtures for `draft` and `questioned` coverage.
- Consequences: `PREREQ-002` is complete. Technology-specific encodings, architecture, repository layout, runtime, dependencies, and test framework remain deferred to `PREREQ-003`; no implementation task is authorized.
- Related Prerequisites: `PREREQ-002`, `PREREQ-003`
