# Finné Memory

**Finné Memory converts an autonomous agent's remembered operating history into bounded authority for its next action.**

> Sibyl lets agents remember. Finné determines what that memory authorizes them to do next.

An agent with a 25,000 USDC ceiling and no memory of its own history will propose 25,000 USDC on its first day and on its hundredth. Mechanical permissions — spending limits, approved assets, approved contracts, permitted time windows — say what an agent is *technically allowed* to do. They say nothing about what it has *earned*: what happened last time, under what circumstances it was approved, what scope was considered safe, whether the outcome held up, and what is materially different now.

Finné Memory turns persisted experiences into structured precedents and uses those precedents to derive a narrower, explainable action authority.

Finné Memory is **not** generic agent memory. Sibyl Memory provides the persistent memory. Finné Memory operates above it and converts remembered operating history into bounded, auditable authority.

## Naming

| Name | Meaning |
| --- | --- |
| Sibyl Labs | Hackathon organiser |
| Sibyl Memory | The organiser's mandatory persistent-memory infrastructure |
| Finné | Umbrella venture |
| Finné Memory | This product |
| `Finne-Memory` | GitHub repository |
| `finne-memory` | Technical slug |

Canonical repository: [github.com/therealgulkorinaga/Finne-Memory](https://github.com/therealgulkorinaga/Finne-Memory)

The product was renamed from Sybill to Finné Memory under `DECISION-021`. Historical references retain the former name and the former event spelling; they are preserved unrewritten as truthful contemporaneous record.

## Status

Planning complete, pending approval. **Implementation has not started.** No application code, scaffolding, or dependencies exist yet.

- Active V1 and domain pivot: `DECISION-022`
- Architecture: `docs/architecture/PREREQ-003_ARCHITECTURE.md` (`DECISION-023`, awaiting approval)
- First specification: `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md` (proposed)
- Remaining gate: Arko's approval and commit of `DECISION-023` and `SPEC-001`

## The Demonstration

Two genuinely separate processes.

**Session 1.** Owner ceiling is 25,000 USDC on Base. The agent proposes 25,000. No comparable precedent exists, so Finné Memory escalates rather than silently authorizing the full amount. The owner approves a constrained authority of 10,000 USDC. The agent executes a safe zero-value Base action recording that authorization. The complete case — proposal, facts, ceiling, constrained authority, decision, action, transaction reference, outcome, precedent status — is written into Sibyl Memory. **The process exits.**

**Session 2.** A fresh process. Same 25,000 ceiling, a materially similar opportunity, no carried-over state. The agent proposes the broader action. Finné Memory retrieves the earlier case from Sibyl Memory, confirms it is materially comparable and still `active`, and derives learned authority of 10,000 USDC.

**25,000 USDC proposed → 10,000 USDC authorized**, attributable on screen to the precedent it recalled.

**Control.** Delete the memory and Session 2 retrieves nothing, derives zero autonomous authority, and escalates. It cannot proceed.

## Where Sibyl Memory Is Load-Bearing

The critical-path reads and writes are specified in `docs/architecture/PREREQ-003_ARCHITECTURE.md` section 3. In short:

- **Writes (Session 1):** immutable case version, owner-policy snapshot, append-only authority events, execution outcome and Base transaction reference.
- **Reads (Session 2):** candidate precedent generation, exact case retrieval, authority-state fold, outcome lookup.

Remove those reads and the agent cannot derive learned authority. It falls back to escalation and cannot act autonomously. That is the whole product, not a stored preference.

At implementation, this table moves into this README as the event's required memory-location section.

## How Base Performs Genuine Work

Finné derives the permitted action → the agent executes it on Base → the transaction result becomes outcome evidence → the outcome is written into Sibyl Memory → a future fresh session recalls and uses it.

A purpose-built `AuthorizationReceipt` contract records the authorized policy amount and a hash of the facts and precedents relied upon. Every demonstration transaction carries **zero value**: representing a 10,000 USDC authorization does not require moving 10,000 USDC. The transaction result is the outcome evidence that feeds the next session's derivation eligibility.

## Boundaries

Finné Memory is not a payment, escrow, x402, refund, settlement, transaction-dispute, or service-delivery verification product. Those belong to the separate Finné/x402 direction. Base is used here for authorized execution and outcome evidence only.

## Documentation

**Current-facing**

- `PRD.md` — product requirements
- `ARCHITECTURE.md` — architecture summary and constraint register
- `docs/architecture/PREREQ-003_ARCHITECTURE.md` — the full architecture decision
- `docs/product/ACTIVE_DEMO_DESIGN.md` — active demo corpus, fixtures, and negative cases
- `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md` — proposed first specification
- `HACKATHON_RULES.md` — verified official event rules and open organiser questions
- `TASKS.md` — task registry and immediate build sequence
- `DECISIONS.md` — chronological product, architecture, and process decisions

**Governance**

- `AGENTS.md` — standing operating manual for agents
- `AGENT_BUILD_INSTRUCTIONS.md` — roles, ownership, handoffs, reviews, escalation
- `AI_BUILD_GOVERNANCE.md` — mandatory AI-build lifecycle and control gates
- `CONTRIBUTING.md` — collaboration workflow

**Audit**

- `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `REUSED_COMPONENTS.md`, `prompts/`

**Historical**

- `docs/product/PREREQ-001_*` and `docs/product/PREREQ-002_*` — the supplier-onboarding design, superseded as a domain by `DECISION-022`. The `PREREQ-002` object model, authority semantics, and invariants carry forward unchanged and remain authoritative.

## Licence

MIT. See [`LICENSE`](LICENSE). Chosen under `DECISION-024` and consistent with `sibyl-memory-client`, which is also MIT.
