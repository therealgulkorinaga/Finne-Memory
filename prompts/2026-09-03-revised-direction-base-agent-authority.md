# 2026-09-03 Revised Direction: Base Agent Authority From Remembered History

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Opus 5.
- Capture status: Contemporaneous. Saved before any file in this turn was changed.
- Governing outputs: `DECISION-022`, `DECISION-023`, revised `PRD.md`, revised `HACKATHON_RULES.md`, `docs/product/ACTIVE_DEMO_DESIGN.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, and proposed `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`.

## Material Instruction From Arko (verbatim)

You are taking over as the lead builder of Finné Memory for the Sibyl Labs Hackathon.

Read this entire instruction before acting.

Your task in this turn is to reconcile the repository with the revised product direction, update the minimum necessary planning documents, and create one concise build-ready architecture specification.

Do not write application code, create scaffolding, install dependencies, deploy contracts, or execute onchain transactions in this turn.

Do not create reviews of reviews or additional governance layers.

### 1. Naming

The names have distinct meanings:

- Sibyl Labs: hackathon organiser
- Sibyl Memory: organiser's mandatory persistent-memory infrastructure
- Finné: umbrella venture
- Finné Memory: our product
- Finne-Memory: GitHub repository
- finne-memory: technical slug

Never describe our product as Sibyl.

Never claim that Finné Memory provides generic agent memory. Sibyl Memory provides persistent memory. Finné Memory converts remembered operating history into bounded, auditable authority.

### 2. Revised product thesis

Finné Memory converts an autonomous agent's remembered operating history into bounded authority for its next action.

Short formulation:

"Sibyl lets agents remember. Finné determines what that memory authorizes them to do next."

The problem:

Autonomous agents can be given mechanical permissions such as:

- maximum spending limits;
- approved assets;
- approved contracts;
- approved protocols;
- approved functions;
- permitted time windows.

Those rules define what an agent is technically allowed to do, but they do not capture the institutional meaning of the agent's previous performance.

They do not answer:

- What happened when the agent exercised a similar permission before?
- Under what circumstances was the earlier action approved?
- What amount or scope was considered safe?
- Did the action succeed or fail?
- Was the earlier decision later questioned or withdrawn?
- What conditions made the earlier case safe?
- What is materially different now?
- What narrower authority has the agent earned from experience?

Finné Memory turns persisted experiences into structured precedents and uses those precedents to derive a narrower, explainable action authority.

### 3. Core authority model

The owner defines the hard permission ceiling.

Example:

- Maximum owner permission: 25,000 USDC
- Approved network: Base
- Approved asset: USDC
- Approved action class: capital deployment
- Approved protocol or contract classes: explicitly defined
- Unknown situations: require constrained action or owner review

Finné Memory may:

- narrow the amount;
- narrow the permitted contract or function;
- add conditions;
- block an action;
- require escalation;
- restore authority within the original owner ceiling when an owner-defined derivation policy permits it.

Finné Memory may never:

- exceed the owner's permission ceiling;
- invent a new asset, contract, protocol, function, network, or action class;
- grant the agent powers the owner did not delegate;
- treat past success as unlimited authority;
- let the agent rewrite its own authority policy;
- let a language model determine final authorization.

The owner ceiling is always superior to learned authority.

Effective authority is the strictest combination of:

1. owner permission ceiling;
2. current hard policy;
3. active remembered precedents;
4. learned constraint;
5. current action facts.

### 4. Relationship between Sibyl, Finné, and Base

#### Sibyl Memory

Sibyl Memory is the mandatory persistent-memory substrate.

It stores and recalls, across genuinely fresh sessions:

- past action proposals;
- relevant context;
- owner permissions;
- permission decisions;
- constraints applied;
- actions taken;
- Base transaction references;
- observed outcomes;
- incidents;
- precedent status;
- later treatment.

Sibyl Memory must be load-bearing.

The application must directly write important state into Sibyl Memory and retrieve it in a fresh process/session.

If Sibyl Memory is removed, the agent must lose the operating history required to derive learned authority. The product must therefore materially degrade or fail safely.

Do not build a competing generic memory database.

Do not use Supabase, PostgreSQL, pgvector, Pinecone, or another database as the source of truth for remembered agent experiences.

#### Finné Memory

Finné Memory operates above Sibyl Memory.

It provides:

1. owner permission model;
2. decision schema;
3. precedent construction;
4. precedent comparison;
5. material-difference detection;
6. authority-state treatment;
7. learned-constraint derivation;
8. deterministic action authorization;
9. readable explanation;
10. outcome feedback.

#### Base

Base is the onchain execution and evidence layer.

The intended sequence is:

Finné derives permitted action
-> agent executes the permitted action on Base
-> transaction result becomes outcome evidence
-> outcome is written into Sibyl Memory
-> a future fresh session recalls and uses it.

Base must perform genuine work, not appear as a decorative integration.

### 5. Hackathon requirements

Use the official sources:

- https://hack.sibyllabs.org/
- https://hack.sibyllabs.org/rules
- https://hack.sibyllabs.org/submissions
- https://docs.sibyllabs.org/
- https://docs.sibyllabs.org/memory
- https://docs.sibyllabs.org/memory/integrations

Record the verified requirements in HACKATHON_RULES.md.

Binding requirements include:

- Build window: September 1-10, 2026
- Submission deadline: September 10, 2026 at 23:59 UTC
- Sibyl Memory is mandatory
- Memory must be load-bearing
- A fresh session must recall persisted context
- Retrieved memory must change a decision, action, or result
- Thin wrappers and decorative integrations are ineligible
- README must identify critical-path memory reads and writes
- Public repository must use an OSI-approved licence: MIT or Apache-2.0
- Demo must be 2-5 minutes
- Demo must visibly show the fresh-session recall moment
- Two build-in-public posts are required
- Base and Virtuals are optional partner stacks
- One verified partner stack gives a 1.15 multiplier
- Both verified stacks give a 1.25 multiplier
- Base requires deployment plus an executed onchain action visible in the demo
- Do not assume Base Sepolia qualifies unless verified with the organisers

Do not import ETHOnline-specific rules into this project.

### 6. Fresh-session demonstration

The demo must have two genuinely separate sessions.

#### Session 1: Establish experience

The owner has defined a maximum permission ceiling of 25,000 USDC.

An autonomous treasury agent encounters a new Base opportunity.

The agent proposes an action of up to 25,000 USDC.

Because no relevant precedent exists, Finné Memory must not silently authorize the full amount.

The safe cold-start behaviour is:

- constrain the action;
- block it; or
- require owner approval.

For the demo, the owner approves a constrained authority of 10,000 USDC under defined conditions.

The agent executes a safe demonstration action on Base.

Do not place 10,000 USDC of real funds at risk. The amount may be represented in the policy and authorization record while the executed demonstration uses a safe minimal-value transaction or purpose-built demo contract.

Sibyl Memory persists:

- owner ceiling;
- proposed action;
- circumstances;
- material facts;
- constrained authority;
- decision;
- action;
- Base transaction reference;
- observed outcome;
- supporting evidence;
- precedent status.

Then terminate the agent process/session completely.

#### Session 2: Memory changes behaviour

Start a genuinely fresh agent session.

The new session receives:

- the owner's general 25,000-USDC ceiling;
- a materially similar Base opportunity;
- no copied in-memory session state.

The agent initially considers or proposes the broader action.

Finné Memory retrieves the earlier case from Sibyl Memory.

Finné determines:

- the prior case is materially comparable;
- the precedent remains active;
- the current facts satisfy the relevant conditions;
- remembered experience supports autonomous authority only up to 10,000 USDC.

The action changes:

25,000 USDC proposed
-> 10,000 USDC authorized
-> 10,000-USDC policy amount represented
-> safe Base demonstration action executed.

The changed action must be visible and attributable to the recalled memory.

Without Sibyl Memory:

- Finné cannot retrieve the precedent;
- Finné cannot derive the 10,000-USDC learned authority;
- the safe fallback is block, constrain further, or require owner approval.

### 7. Precedent model retained from existing work

Preserve the useful generic model already approved:

- immutable matter versions;
- immutable decision versions;
- facts;
- evidence;
- sources;
- canonical fact-evidence links;
- policy versions;
- citations;
- precedent relationships;
- append-only authority events;
- human or owner confirmation;
- provenance;
- rejected citation-attempt audit events.

Authority states remain:

- draft;
- active;
- questioned;
- superseded;
- withdrawn.

Only active precedents may support learned authority.

Withdrawn and superseded cases may be retrieved and displayed but cannot authorize an action.

Similarity, authority, and outcome remain separate.

A highly similar precedent may be withdrawn.

A less similar precedent may remain active.

### 8. Precedent relationships

Retain:

- follows;
- distinguishes;
- questions;
- supersedes.

A model may suggest a relationship or material difference.

Only deterministic validation and an authorized confirmation path may persist or apply it.

### 9. Deterministic versus model responsibilities

Deterministic code owns:

- owner permission ceiling;
- effective action authority;
- permission intersection;
- amount limits;
- approved network, asset, contract, protocol, and function scope;
- authority states;
- authority transitions;
- terminal-state enforcement;
- valid citations;
- precedent eligibility;
- policy versions;
- exact identifier resolution;
- outcome recording;
- safe fallback behaviour;
- final allow, constrain, block, or escalate result;
- prohibition on exceeding owner authority.

A model may assist with:

- extracting proposed facts from natural language;
- suggesting comparable precedents;
- explaining factual similarities;
- explaining material differences;
- drafting a readable precedent explanation;
- proposing follow or distinguish treatment.

A model may not:

- expand authority;
- authorize an action;
- change an authority state;
- create a valid citation;
- confirm a precedent;
- sign a transaction;
- hold a private key;
- submit a Base transaction;
- bypass deterministic rules.

The deterministic system must work without a model API key.

### 10. Safe authorization formula

Design the architecture around a deterministic formulation conceptually equivalent to:

effective_authority =
intersection(
    owner_permission_ceiling,
    current_hard_policy,
    active_precedent_constraints,
    learned_constraint,
    current_action_scope
)

The exact implementation may differ, but the invariant must remain:

effective authority can never exceed owner authority.

When relevant memory is missing, malformed, contradictory, withdrawn, or unavailable, the system must fail safely.

### 11. Revised active use case

Replace supplier onboarding as the active V1 demonstration.

The active V1 is now:

"An autonomous treasury agent uses remembered operating history to determine its bounded authority for a materially similar Base action in a fresh session."

The previous supplier-onboarding material must remain visible as historical design work where appropriate.

Do not silently rewrite historical decisions, saved prompts, build logs, previous commits, or merged PR records.

Current-facing product and architecture documents must use the revised Base agent-permission use case.

Add a chronological product decision recording the controlled domain pivot.

The decision must state:

- the precedent and authority product remains intact;
- the demonstration domain changes;
- Sibyl Memory becomes the mandatory memory substrate;
- Base becomes the intended execution/evidence layer;
- supplier onboarding is no longer the active V1 demo;
- historical records remain preserved;
- this is not a pivot into x402, payments, escrow, settlement, or disputes.

### 12. Separation from the other Finné project

Finné Memory must remain distinct from the separate Finné/x402 project.

Finné Memory is about:

- remembered operating history;
- decision precedent;
- learned constraints;
- delegated authority;
- action permissions;
- cross-session behavioural change.

It is not about:

- agents buying services;
- x402 payments;
- escrow;
- settlement;
- refunds;
- transaction disputes;
- service-delivery verification.

Base is used for authorized execution and outcome evidence, not to convert this into an agent-commerce product.

### 13. Architecture direction

Reconsider the earlier web-stack assumptions because Sibyl Memory is local-first and Python-native.

Evaluate and choose the smallest credible architecture.

The likely direction is:

- Python agent runtime;
- sibyl-memory-client for direct persistent-memory access;
- deterministic Finné authority engine;
- structured local policy configuration;
- minimal Base adapter;
- minimal web or terminal interface;
- automated tests for authority invariants;
- a reproducible two-session demo.

Do not add:

- Supabase as remembered-history storage;
- PostgreSQL as the primary precedent store;
- pgvector;
- a separate vector database;
- LangChain unless indispensable;
- microservices;
- unnecessary agent orchestration;
- complex cloud infrastructure.

Verify the actual Sibyl SDK APIs from the installed package or official documentation before specifying interfaces.

### 14. Base demonstration

Propose the safest Base integration that performs genuine work.

Possible direction:

- deploy a minimal demonstration contract;
- submit a low-value or zero-value contract interaction;
- include the permitted policy amount in an authorization or action receipt;
- record the transaction hash and result;
- write the outcome back to Sibyl Memory.

Do not assume that representing a 10,000-USDC authorization requires transferring 10,000 USDC.

Identify whether Base mainnet or Base Sepolia is required for the partner multiplier. Mark this as an organizer-verification question if the official rules do not resolve it.

### 15. Current repository state

Before editing, inspect:

- current branch;
- HEAD;
- working tree;
- index;
- remote;
- recent commits;
- merged and open PR state where available;
- product naming migration status.

Read:

- README.md
- AGENTS.md
- PRD.md
- ARCHITECTURE.md
- TASKS.md
- DECISIONS.md
- AGENT_BUILD_INSTRUCTIONS.md
- AI_BUILD_GOVERNANCE.md
- HACKATHON_RULES.md
- AI_USAGE.md
- HUMAN_DECISIONS.md
- BUILD_LOG.md
- REUSED_COMPONENTS.md
- all files under docs/product/
- all saved prompts relevant to the current state.

Follow repository instructions, but do not create recursive review bureaucracy.

### 16. Required work in this turn

After inspection:

1. Report the exact repository and naming-migration status.
2. Identify every current-facing document that still treats supplier onboarding as the active V1.
3. Create one chronological decision for the controlled domain pivot.
4. Update the PRD to the Finné/Sibyl/Base model.
5. Update HACKATHON_RULES.md from the official Sibyl sources.
6. Update the active synthetic demo design from supplier onboarding to Base agent-permission precedent.
7. Preserve historical material and label it historical where necessary.
8. Update ARCHITECTURE.md.
9. Create one concise: `docs/architecture/PREREQ-003_ARCHITECTURE.md`
10. Update TASKS.md to reflect the revised prerequisites and immediate build sequence.
11. Update AI_USAGE.md, HUMAN_DECISIONS.md, BUILD_LOG.md, and REUSED_COMPONENTS.md truthfully.
12. Save this material instruction under prompts.
13. Propose the first bounded implementation specification: `SPEC-001: Fresh-session learned-authority vertical slice`
14. Do not implement SPEC-001 yet.

### 17. PREREQ-003 must decide

The architecture document must decide:

- agent runtime;
- Sibyl Memory integration method;
- memory read/write boundary;
- structured memory format;
- owner-policy representation;
- deterministic authority engine;
- precedent retrieval;
- material-difference handling;
- Base adapter;
- key and signing boundary;
- safe demo contract/action;
- fresh-session reset procedure;
- model-optional behaviour;
- testing approach;
- local run procedure;
- deployment or demonstration approach;
- module boundaries;
- repository layout;
- failure behaviour.

Keep it concise and buildable.

Do not create multiple proposals, review packets, or architecture alternatives unless a genuine blocker prevents a decision.

### 18. Proposed first implementation specification

Prepare SPEC-001 around one vertical outcome:

Session 1:
- establish owner ceiling;
- propose broader action;
- constrain or obtain approval for 10,000;
- execute safe Base demonstration;
- write context, decision, action, transaction, and outcome to Sibyl Memory.

Fresh session:
- start with no process memory;
- receive a similar action proposal;
- retrieve the prior case from Sibyl Memory;
- validate that the precedent is active;
- compare material facts;
- derive learned authority of 10,000;
- change the proposed action;
- execute the safe Base action;
- persist the new outcome.

Required negative behaviours:

- no Sibyl memory -> safe fallback;
- withdrawn precedent -> cannot authorize;
- materially different facts -> cannot silently follow;
- requested amount above owner ceiling -> blocked;
- model failure -> deterministic path still works;
- malformed memory -> safe failure;
- Base failure -> no false success;
- duplicate execution -> no inconsistent outcome record.

### 19. Speed rule

We are now operating under a velocity model:

- one concise decision;
- one updated PRD;
- one architecture document;
- one implementation specification;
- one independent review;
- then build.

Do not create documentation merely to document other documentation.

Routine reversible technical choices should be made and explained, not escalated as blockers.

Escalate only:

- product-scope contradictions;
- owner-authority violations;
- key/signing risks;
- mandatory hackathon-rule uncertainty;
- inability to make Sibyl Memory load-bearing;
- inability to demonstrate a genuine Base action.

### 20. End-of-turn output

After making the planning changes, return:

1. repository status;
2. files changed;
3. revised product summary;
4. exact fresh-session demo;
5. architecture chosen;
6. where Sibyl Memory is written and read;
7. why memory is load-bearing;
8. how Base performs genuine work;
9. deterministic/model boundary;
10. SPEC-001 summary;
11. unresolved organiser questions;
12. tests that will prove the core claims;
13. proposed commit boundary and message.

Do not stage, commit, push, merge, install dependencies, write application code, or begin SPEC-001 implementation.

Stop for Arko's approval.

## Interpretation Notes Recorded By Claude

- The instruction's naming section corrects the repository's prior spelling. `Sibyl Labs` / `Sibyl Memory` is the organiser and its infrastructure. Historical repository text using `Sybill` is preserved unchanged as truthful contemporaneous record.
- The instruction materially changes the product output from advisory-only decision support to a binding deterministic authorization bound. This is recorded as an explicit scope change in `DECISION-022` rather than applied silently.
