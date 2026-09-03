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
- Amended by: `DECISION-022`. Finné Memory now emits a binding deterministic authorization bound (allow, constrain, block, escalate) rather than advisory-only decision support. The retained boundary is that Finné Memory bounds the agent's authority and never selects the business action or exceeds the owner ceiling.

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
- Status: `Superseded`
- Classification: CONFIRMED
- Context: `DECISION-005` proposed supplier onboarding and procurement compliance as the V1 domain.
- Decision: Supplier onboarding and procurement compliance is the confirmed V1 domain.
- Consequences: V1 specifications, corpus fixtures, acceptance criteria, and demo materials will use this domain unless a later decision explicitly supersedes it.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`
- Superseded by: `DECISION-022`, for the demonstration domain only. Supplier onboarding is retained as historical design work and is no longer the active V1 demo.

### DECISION-011: Confirm Primary User And Buyer

- ID: `DECISION-011`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Superseded`
- Classification: CONFIRMED
- Context: `DECISION-007` proposed a primary user and organizational buyer for the V1 domain.
- Decision: The primary user is a supplier-risk or procurement-compliance professional. The primary buyer is the organization's procurement, supplier-risk, or compliance function.
- Consequences: Product workflows and language must support an accountable professional using an automated decision system.
- Related Prerequisites: `PREREQ-001`
- Superseded by: `DECISION-022`. The active V1 user is the owner of an autonomous onchain treasury agent; the supplier-risk user is historical.

### DECISION-012: Confirm Representative Matter

- ID: `DECISION-012`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Superseded`
- Classification: CONFIRMED
- Context: `DECISION-008` proposed a concrete supplier matter for the V1 precedent workflow.
- Decision: The representative matter is whether a supplier with incomplete beneficial-ownership evidence should be approved, rejected, or escalated.
- Consequences: The synthetic corpus and current-matter fixture must demonstrate this question without allowing Sybill to choose the final outcome.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`
- Superseded by: `DECISION-022`. The active representative matter is a Base capital-deployment action proposed against an owner permission ceiling; the beneficial-ownership matter is historical.

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
- Amended by: `DECISION-022`. Owner confirmation is retained as the gate that turns a recorded case into active precedent, but Finné Memory now deterministically authorizes the action bound itself.

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

> Annotation added 2026-09-02: `SPEC-001` was the working label used when this decision was recorded. The approved artifacts were subsequently finalized under the `PREREQ-002_*` filenames listed below. They are planning product/data contracts and never authorized implementation.

- ID: `DECISION-018`
- Date: `2026-09-02`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Closure of `PREREQ-002` required exact review of the object model, complete fixture data, authority transitions, and deterministic invariants.
- Decision: Approve `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, its complete synthetic seed-data appendix, and the amended deterministic invariants. Retain six primary demo decisions and add two non-primary lifecycle fixtures for `draft` and `questioned` coverage.
- Consequences: `PREREQ-002` is complete. Technology-specific encodings, architecture, repository layout, runtime, dependencies, and test framework remain deferred to `PREREQ-003`; no implementation task is authorized.
- Related Prerequisites: `PREREQ-002`, `PREREQ-003`

### DECISION-019: Adopt Strict Human-Directed AI Build Governance

- ID: `DECISION-019`
- Date: `2026-09-02`
- Type: `Process`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Arko directed Sybill to adopt the transferable spec-driven, human-directed, progressively auditable operating rules identified from the ETHOnline solo AI build process while excluding all ETHOnline-specific product, sponsor, bounty, deadline, prize, submission, and demo content.
- Decision: Prohibit one-shot and near-one-shot builds; require an approved and committed bounded `SPEC-*` before implementation; use one bounded feature or coherent repair per branch and pull request; preserve material prompts under `prompts/`; maintain repository and pull-request AI attribution plus `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md`; require acceptance-criteria-mapped tests, Arko's manual verification, independent diff review, human commit approval, human-only merge to the repository’s remote default branch, small coherent commits, known-good checkpoints, the mandatory lifecycle, absolute stop conditions, and the full commit gate in `AGENT_BUILD_INSTRUCTIONS.md` and `AI_BUILD_GOVERNANCE.md`.
- Consequences: `TASK-001` cannot authorize implementation until it references an approved and committed bounded `SPEC-*`. Every Work and Codex task must satisfy the commit gate. Documentation-only changes may mark implementation tests and manual product verification `NOT APPLICABLE` with reasons, but documentation validation, link checking, status consistency, AI attribution, and human-decision traceability remain mandatory.
- Related Prerequisites: `PREREQ-003`

### DECISION-020: Distinguish Planning Contracts From Implementation Specifications

- ID: `DECISION-020`
- Date: `2026-09-02`
- Type: `Process`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Earlier planning used `SPEC-001` as a working label for the decision-record and corpus definition. Those approved artifacts now use `PREREQ-002_*` filenames, while the adopted build governance requires a separate bounded and committed `SPEC-*` before implementation.
- Decision: Treat `PREREQ-001` and `PREREQ-002` exclusively as approved planning contracts. No bounded implementation `SPEC-*` exists yet. The first bounded implementation specification may be created only after `PREREQ-003` is approved, and it must then pass the approval and commit gate before any implementation task can be authorized.
- Consequences: The completed prerequisite contracts cannot be cited as implementation authorization. `TASK-001` remains reserved, absent, and unauthorized, and no application implementation may begin.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`, `PREREQ-003`

### DECISION-021: Rename Sybill To Finné Memory

- ID: `DECISION-021`
- Date: `2026-09-02`
- Type: `Product / Repository Naming`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: The current product and repository require distinct confirmed names while the Sybill hackathon/event name and truthful historical records retain their original wording.
- Decision: Rename the product from `Sybill` to `Finné Memory`, rename the repository to `Finne-Memory`, and use `finne-memory` where accents or spaces are technically unsuitable. Present the current product as: “Finné Memory gives autonomous systems institutional memory and precedent for consequential decisions.”
- Historical-record rule: The product was renamed from Sybill to Finné Memory under DECISION-021. Historical references retain the former name. Existing decisions, logs, reviews, saved prompts, commit descriptions, and pull-request records are not rewritten. `Sybill` remains the hackathon/event name wherever it refers to the event, organizer, rules, eligibility, submission, deadline, or event-specific restrictions.
- Scope consequence: This naming decision does not change the approved product thesis, V1 domain, representative matter, authority model, corpus, permissions, implementation gates, or separation from the Finné/x402 project.
- Affected current-facing documents: `README.md`, `PRD.md`, `AGENTS.md`, `AGENT_BUILD_INSTRUCTIONS.md`, `AI_BUILD_GOVERNANCE.md`, `TASKS.md`, `docs/product/PREREQ-001_PRODUCT_DEFINITION_PROPOSAL.md`, `docs/product/PREREQ-002_DECISION_RECORD_AND_CORPUS_PROPOSAL.md`, `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, `docs/product/PREREQ-002_REVIEW_PACKET.md`, and `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`.
- Related Prerequisites: `PREREQ-001`, `PREREQ-002`, `PREREQ-003`

### DECISION-022: Controlled Domain Pivot To Base Agent Authority From Remembered History

- ID: `DECISION-022`
- Date: `2026-09-03`
- Type: `Product`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: The Sibyl Labs Hackathon requires a mandatory, load-bearing Sibyl Memory integration whose recall in a genuinely fresh session changes what the agent knows, decides, or does. The approved precedent-and-authority model satisfies that requirement, but the supplier-onboarding demonstration domain does not exercise cross-session behavioural change, does not use the mandatory memory substrate, and gives Base no genuine role.
- Decision: Change the demonstration domain, not the product. Finné Memory converts an autonomous agent's remembered operating history into bounded, auditable authority for its next action. The active V1 is: an autonomous treasury agent uses remembered operating history to determine its bounded authority for a materially similar Base action in a fresh session.

What is retained unchanged:

- The precedent and authority product is intact: immutable matter and decision versions, facts, evidence, sources, canonical fact-evidence links, policy versions, validated citations, precedent relationships, append-only authority events, owner confirmation, provenance, and rejected citation-attempt audit events.
- Authority states remain `draft`, `active`, `questioned`, `superseded`, and `withdrawn`. Only `active` precedents may support learned authority. Withdrawn and superseded cases remain retrievable and displayable but cannot authorize an action.
- Precedent relationships remain `follows`, `distinguishes`, `questions`, and `supersedes`.
- Similarity, authority, and outcome remain three separate dimensions.
- A model may suggest a relationship or a material difference; only deterministic validation and an authorized confirmation path may persist or apply it.

What changes:

- The demonstration domain changes from supplier onboarding and procurement compliance to Base agent-permission precedent. Supplier onboarding is no longer the active V1 demo.
- Sibyl Memory becomes the mandatory persistent-memory substrate and the sole source of truth for remembered agent experiences. No Supabase, PostgreSQL, pgvector, Pinecone, or other database may hold that state.
- Base becomes the intended execution and evidence layer. Finné derives the permitted action, the agent executes it on Base, the transaction result becomes outcome evidence, and the outcome is written into Sibyl Memory for a future fresh session.
- Product output changes from an advisory-only `PrecedentPacket` to a binding deterministic `AuthorizationDecision` that bounds the agent's next action as allow, constrain, block, or escalate, accompanied by a readable explanation. This amends `DECISION-002` and `DECISION-013`.

Owner-authority invariant:

- The owner defines the hard permission ceiling and that ceiling is always superior to learned authority.
- Effective authority is the strictest intersection of the owner permission ceiling, current hard policy, active remembered precedent constraints, learned constraint, and current action scope.
- Finné Memory may narrow an amount, narrow a permitted contract or function, add conditions, block, require escalation, or restore authority within the original owner ceiling under an owner-defined derivation policy.
- Finné Memory may never exceed the owner ceiling; invent an asset, contract, protocol, function, network, or action class; grant undelegated powers; treat past success as unlimited authority; let the agent rewrite its own authority policy; or let a language model determine final authorization.
- When relevant memory is missing, malformed, contradictory, withdrawn, or unavailable, the system fails safely by constraining, blocking, or escalating to the owner.

Boundary preservation:

- This is not a pivot into x402, payments, escrow, settlement, refunds, transaction disputes, or service-delivery verification. Base is used for authorized execution and outcome evidence only. Finné Memory remains distinct from the separate Finné/x402 project, and `DECISION-001` is unchanged.
- Finné Memory is not generic agent memory. Sibyl Memory provides persistent memory; Finné Memory converts remembered operating history into bounded, auditable authority.

Historical preservation:

- Historical decisions, logs, reviews, saved prompts, commit descriptions, and merged pull-request records are preserved unrewritten. `DECISION-010`, `DECISION-011`, and `DECISION-012` are marked superseded with annotations. `DECISION-002` and `DECISION-013` are annotated as amended.
- `docs/product/PREREQ-001_*` and `docs/product/PREREQ-002_*` are retained and labelled historical. The `PREREQ-002` object model, authority semantics, invariants, and validation approach carry forward; only its supplier-domain instantiation is superseded.

- Consequences: `PRD.md`, `ARCHITECTURE.md`, `TASKS.md`, `README.md`, and the active demo design are revised to the Base agent-permission use case. The active demo corpus is defined in `docs/product/ACTIVE_DEMO_DESIGN.md`. `HACKATHON_RULES.md` now carries verified official rules.
- Related Prerequisites: `PREREQ-001` (historical), `PREREQ-002` (model retained, domain superseded), `PREREQ-003`
- Related Specifications: proposed `SPEC-001`

### DECISION-023: Minimum Python Architecture For The Learned-Authority Slice

- ID: `DECISION-023`
- Date: `2026-09-03`
- Type: `Architecture`
- Status: `Proposed`
- Classification: PROPOSED — requires Arko's approval before `SPEC-001` may be approved and committed.
- Context: `PREREQ-003` required the minimum credible architecture. The earlier web-stack assumption is not viable: Sibyl Memory is a local-first, Python-native SQLite library, so the runtime must sit next to it rather than behind a web service.
- Decision: Adopt a single Python package with five modules — agent runtime, Sibyl Memory adapter, deterministic authority engine, Base adapter, and a terminal interface — plus a test suite for authority invariants and a two-script reproducible demo. Full detail, including every one of the nineteen required `PREREQ-003` decisions, is recorded in `docs/architecture/PREREQ-003_ARCHITECTURE.md`.
- Key choices: Python 3.11 with `venv` and `pip`; `sibyl-memory-client` as the only remembered-history store; owner policy as a version-controlled TOML file that Finné Memory can read but never write; a pure-function authority engine with no I/O; deterministic FTS5-backed precedent retrieval with a deterministic material-difference rule set; `web3.py` against a purpose-built `AuthorizationReceipt` demo contract on Base; a signing boundary in which only the Base adapter holds the key, loaded from the environment and never persisted to memory or the repository; and model assistance that is strictly optional and absent by default.
- Consequences: No Supabase, PostgreSQL, pgvector, vector database, LangChain, microservice, or cloud infrastructure is introduced. The deterministic path runs with no model API key. Exact `sibyl-memory-client` signatures must be verified against the installed package at the start of `SPEC-001` because the published README documents the v0.4.x surface while the current release is v0.8.0.
- Related Prerequisites: `PREREQ-003`
- Related Specifications: proposed `SPEC-001`

### DECISION-024: Adopt The MIT Licence

- ID: `DECISION-024`
- Date: `2026-09-03`
- Type: `Process`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: The Sibyl Labs Hackathon requires a public repository under an OSI-approved licence, MIT or Apache-2.0. The repository had no `LICENSE` file, which failed a stated submission requirement and was tracked as `ORG-Q2`.
- Decision: License the repository under the MIT Licence. `LICENSE` is the standard unmodified OSI MIT template, copyright `2026 Arko Ganguli`.
- Rationale: MIT is permissive, is explicitly permitted by the rules, and matches `sibyl-memory-client`, the mandatory memory substrate, which is also MIT. Every other dependency specified by `DECISION-023` is MIT-compatible; `hypothesis` is MPL-2.0 but is dev-only and not distributed.
- Consequences: `ORG-Q2` is closed and the licence submission requirement is satisfied. `pyproject.toml` must declare `license = "MIT"` when `SPEC-001` is implemented. Any future dependency with a copyleft distribution obligation requires an explicit decision before it is added.
- Human decision-maker: Arko, on 2026-09-03.
- Related: `HACKATHON_RULES.md` `ORG-Q2`, `REUSED_COMPONENTS.md`

### DECISION-025: Two-Tool Operating Model And Commit/Push Clarifications

- ID: `DECISION-025`
- Date: `2026-09-03`
- Type: `Process`
- Status: `Accepted`
- Classification: CONFIRMED
- Context: Arko proposed a concrete role-and-action table for the `SPEC-001` implementation phase, saved verbatim in `prompts/2026-09-03-two-tool-operating-model.md`, and asked for it to be checked against `AGENT_BUILD_INSTRUCTIONS.md` before being adopted. Comparison surfaced one genuine ambiguity in the existing text (whether "agents do not commit directly" forbids an agent from ever executing the commit, or only from committing without approval), one gap the existing text was silent on (who pushes a branch and opens a pull request), and one unstated structural fact (the ten-role fleet in Section 4 is staffed by two AI tools plus Arko, not ten separate agents). A first-pass independent Codex review of this same addendum then found two further gaps: the addendum did not name who performs the Section 7 items 2 and 3 checks (Orchestrator and Product Spec Agent) once the fleet collapses to two tools, and its compressed treatment of `SAVE PROMPT` and `UPDATE AUDIT DOCUMENTS` did not preserve the Mandatory Lifecycle's required ordering. A second Codex pass then found the fix for one of two remaining IMPORTANT findings itself overclaimed ("contemporaneous corroboration" for a same-session, after-the-fact self-report). Claude fixed that wording and had drafted a third review prompt before Arko stopped the loop and set an explicit cap.
- Decision: Adopt Arko's operating table as recorded in `AGENT_BUILD_INSTRUCTIONS.md` Section 11. Claude performs every implementer role and, as self-checks against its own work, the Section 7 item 2 and item 3 checks; Codex is the independent reviewer for Section 7 item 4 only — diff review and fix verification, capped at two passes per bounded change; Arko manually tests, decides on findings, approves commits, pushes, opens pull requests, and reviews and merges. "Agents do not commit directly" is clarified to mean an agent may not commit without Arko's prior, explicit, change-specific approval; the mechanical commit may then be executed by Claude. Push and PR creation are reserved to Arko personally via authenticated Bash or the GitHub CLI; no agent performs either. Prompt-saving and audit-document updates remain mandatory and keep the Mandatory Lifecycle's exact order: saving the prompt precedes implementation, and updating the audit documents follows manual verification and fix verification, before commit approval — not before test results and manual-verification outcomes exist to record. At most two independent Codex review passes run per bounded change; if a finding remains open after the second pass, Claude stops and asks Arko how to proceed rather than drafting a third prompt automatically.
- Consequences: No product rule, authority rule, or approval boundary changes. `AGENT_BUILD_INSTRUCTIONS.md` Section 4 gains a cross-reference to Section 11; Sections 7 and 8 are unchanged but are now read together with Section 11's clarification. The two-pass cap bounds review iteration without reducing the mandatory first two passes; it does not weaken the Section 7 item 4 requirement, it stops indefinite auto-repetition of it. This decision governs the conduct of `SPEC-001` once approved and any later implementation task, unless a future decision changes it.
- Human decision-maker: Arko, on 2026-09-03.
- Related: `AGENT_BUILD_INSTRUCTIONS.md` Sections 4, 7, 8, 11; `prompts/2026-09-03-two-tool-operating-model.md`
