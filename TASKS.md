# Finné Memory Issue And Task Registry

This is the implementation-oriented issue list. It is intentionally short. Do not expand every possible workstream into a backlog.

## Implementation Readiness

- Status: SPEC-001 APPROVED / TASK-001 MAY BE CREATED
- Position: `DECISION-022` through `DECISION-025` are approved and merged into `master` (PR #3, PR #4). The MIT licence is in place. `SPEC-001` is approved by Arko (2026-09-03).
- Consequence: `TASK-001` may now be created and implementation may begin under it.

## Immediate Build Sequence

| Step | Item | Owner | Status |
| --- | --- | --- | --- |
| 1 | ~~Approve `DECISION-022` (domain pivot)~~ | Arko | **DONE 2026-09-03** |
| 2 | ~~Approve `DECISION-023` and `docs/architecture/PREREQ-003_ARCHITECTURE.md`~~ | Arko | **DONE 2026-09-03** |
| 3 | ~~Resolve `ORG-Q2` and add the `LICENSE` file~~ | Arko | **DONE 2026-09-03** — MIT, `DECISION-024` |
| 4 | ~~Independent review of this planning checkpoint~~ | Independent reviewer | **WAIVED 2026-09-03 by Arko** — see note below; not run against the original pivot content |
| 5 | ~~Commit the planning checkpoint~~ | Arko | **DONE 2026-09-03** — `d82f224`, `fab9cff`, `39d8c02`, merged into `master` via PR #3 |
| 6 | ~~Approve and commit `SPEC-001`~~ | Arko | **DONE 2026-09-03** |
| 7 | Create `TASK-001` from `SPEC-001` | Orchestrator | **Unblocked — the next step** |
| 8 | Implement `SPEC-001` | Implementation agent | Blocked by step 7 |
| 9 | Ask the organisers `ORG-Q1` (Base mainnet vs Sepolia) | Arko | Can run in parallel; not yet asked |

Note on step 4: `DECISION-025` (the two-tool operating model and Codex review-pass cap) was established after `d82f224` was committed, so that original planning rewrite — the `PRD.md`/`ARCHITECTURE.md`/`PREREQ-003`/`ACTIVE_DEMO_DESIGN.md`/`SPEC-001`/`HACKATHON_RULES.md` content — never went through an independent Codex review. Arko explicitly decided not to run one retroactively (2026-09-03). `DECISION-025`'s own addendum did go through two Codex passes (findings fixed; see `BUILD_LOG.md`), and the AI-attribution submission-practice note went through one explicitly-waived pass. Both are merged.

Per the velocity model in the governing instruction: one decision, one PRD, one architecture document, one specification, one independent review, then build. Do not add documentation that documents other documentation.

## Workflow

The mandatory lifecycle in `AGENT_BUILD_INSTRUCTIONS.md` applies. Implementation requires an approved and committed bounded `SPEC-*` before a feature branch or implementation task may authorize code changes.

## Required Task Format

Each implementation task must include: Task ID; Title; Status (`CONFIRMED | PROPOSED | ASSUMPTION | UNRESOLVED | DEFERRED`); Owner role; Spec reference; Objective; Why this task exists; Dependencies; Exact scope; Explicit exclusions; Files or components expected to be affected; Interfaces consumed and exposed; Functional acceptance criteria; Technical acceptance criteria; Testing requirements; Documentation requirements; Handoff requirements; Stop conditions; Mandatory commit-gate requirements; Definition of Done.

## Prerequisites

### PREREQ-001: Confirm V1 Product Choices

- Status: COMPLETE / HISTORICAL
- Outcome: Closed 2026-09-02 with the supplier-onboarding V1 approved under `DECISION-010`, `DECISION-011`, and `DECISION-012`.
- Superseding decision: `DECISION-022` changed the active V1 to Base agent-permission precedent. The problem framing and the similarity-versus-authority principle carry forward; the supplier user, buyer, and matter are historical.
- Current-facing replacement: `PRD.md` sections "Target Users" and "Active V1 Use Case".

### PREREQ-002: Define Decision Record And Precedent Corpus

- Status: COMPLETE / MODEL RETAINED, DOMAIN SUPERSEDED
- Outcome: Closed 2026-09-02. The object model, authority semantics, transitions, citation rules, invariants, permissions, and negative cases remain the authoritative contract.
- Superseding decision: `DECISION-022` replaced the supplier-domain instantiation only.
- Current-facing replacement: `docs/product/ACTIVE_DEMO_DESIGN.md` is the active corpus. `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md` is retained as a historical worked example.
- Carried-forward obligation: the active corpus needs its own referential-integrity validation during `SPEC-001`, equivalent to what `PREREQ-002_TRACEABILITY_REVIEW.md` did for the supplier corpus.

### PREREQ-003: Define Initial Architecture And Ownership Map

- Status: COMPLETE / APPROVED AND COMMITTED
- Owner role: Orchestrator / Integration Agent
- Output: `docs/architecture/PREREQ-003_ARCHITECTURE.md`, recorded as `DECISION-023`; summarised in `ARCHITECTURE.md`.
- Objective: Decide the minimum credible architecture for the two-session learned-authority slice.
- Decided: agent runtime; Sibyl Memory integration method; memory read/write boundary; structured memory format; owner-policy representation; deterministic authority engine; precedent retrieval; material-difference handling; Base adapter; key and signing boundary; safe demo contract and action; fresh-session reset procedure; model-optional behaviour; testing approach; local run procedure; demonstration approach; module boundaries; repository layout; failure behaviour.
- Ownership map: section 18 replaces the `UNRESOLVED` logical areas in `AGENT_BUILD_INSTRUCTIONS.md` section 3 with concrete, non-overlapping paths.
- Acceptance criteria: SATISFIED. Every required decision is made; trust boundaries are explicit; each implementation area has non-overlapping file ownership; material technology choices are approved (`DECISION-023`) and committed.
- Remaining: None. Superseded by the `SPEC-001` approval gate below as the next planning step.

## Specifications

### SPEC-001: Fresh-Session Learned-Authority Vertical Slice

- Status: APPROVED by Arko 2026-09-03 — not yet implemented
- Location: `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`
- Objective: Prove that remembered operating history changes what an autonomous agent is permitted to do in a genuinely fresh session, deterministically, bounded by owner authority, and auditably.
- Observable outcome: a fresh process proposes 25,000 USDC and is bound to 10,000 USDC by a precedent retrieved from Sibyl Memory, and cannot do so when that memory is removed.
- Acceptance criteria: 14, mapped to 8 test files.
- Blocking dependencies: approval and commit of this specification. `DECISION-023` is already approved and committed.
- Suggested split points if Arko prefers smaller commits: section 14 of the specification names five seams.

## Unresolved Dependencies

- RESOLVED: Minimum shared interfaces and schemas — `PREREQ-003` sections 3, 4, and 17; `SPEC-001` section 7.
- RESOLVED: Authorization and trust boundaries — `PREREQ-003` sections 5, 6, 10; `SPEC-001` section 6.
- RESOLVED: Architecture, repository structure, component boundaries, file ownership, runtime, dependency policy, and test approach — `PREREQ-003` sections 1, 14, 17, 18.
- RESOLVED: Event-specific technology restrictions — `HACKATHON_RULES.md` now carries verified rules.
- RESOLVED: First vertical slice with observable acceptance criteria — `SPEC-001` sections 11 and 12.
- UNRESOLVED: `ORG-Q1` — Base mainnet versus Base Sepolia. Non-blocking; the network is one configuration value.
- RESOLVED: `ORG-Q2` — repository licensed MIT under `DECISION-024`; `LICENSE` exists at repository root.
- UNRESOLVED: `VERIFY-AT-BUILD` — exact `sibyl-memory-client` 0.8.0 signatures. Non-blocking; first step of `SPEC-001` implementation, with a documented fallback.
- RESOLVED: Arko approved `DECISION-022`, `DECISION-023`, and the licence choice on 2026-09-03; all merged into `master` via PR #3.
- RESOLVED: `DECISION-025` establishes the two-tool operating model (Claude implements, Codex independently reviews, capped at two passes per change, Arko approves/pushes/merges) governing `SPEC-001`'s implementation; merged into `master` via PR #4.
- RESOLVED: Arko approved `SPEC-001` on 2026-09-03. `TASK-001` may now be created.

## TASK-001 Creation Gate

The Orchestrator may draft `TASK-001` only when:

1. Its governing product behavior is `CONFIRMED`. — Satisfied by `DECISION-022`.
2. Its referenced specification is approved and contains inputs, outputs, state changes, rules, permissions, failures, invariants, acceptance criteria, and out-of-scope behavior. — Satisfied. `SPEC-001` contains all of these and is approved.
3. Its consumed and exposed interfaces are documented. — Satisfied by `SPEC-001` section 7.
4. Its exact ownership area and expected files are known. — Satisfied by `PREREQ-003` section 18.
5. Its architecture and dependencies are approved in `ARCHITECTURE.md` and recorded in `DECISIONS.md`. — Recorded as `DECISION-023`, approved and committed.
6. Its testing approach and required test cases are defined. — Satisfied by `SPEC-001` section 12.
7. It can be completed and independently reviewed without another agent making a product or architecture decision. — Satisfied, subject to the two `VERIFY-AT-BUILD` and `ORG-Q1` items, both of which have documented defaults.
8. Its bounded `SPEC-*` has been approved by Arko and committed before implementation authorization. — Satisfied. Approved 2026-09-03.
9. Its prompt, attribution, audit-document, manual-verification, independent-review, and mandatory commit-gate obligations are explicit. — Satisfied by `AI_BUILD_GOVERNANCE.md`.

Gate status: **9 of 9 conditions satisfied. `TASK-001` may be created.**

## Current Expected Delivery

- CONFIRMED: No application-code delivery is authorized. The current turn delivered planning documents only.
- CONFIRMED: No implementation agent may scaffold a project, select a stack beyond what `DECISION-023` records, add dependencies, define schemas in code, or implement product behavior before `TASK-001` exists.
- CONFIRMED: `TASK-001` cannot authorize implementation unless it references an approved and committed bounded `SPEC-*`.
- CONFIRMED: The first implementation delivery must be exactly the files, behavior, tests, and documentation specified by `SPEC-001` and an approved `TASK-001`.

## Deferred Groups

Planning placeholders only, all downstream of `SPEC-001`:

- Demo recording, build-in-public posts, and the submission checklist.
- README memory read/write table and Prior Work declaration (required by the event; drafted during `SPEC-001`).
- Retrieval ranking quality beyond deterministic candidate generation.
- Any second domain instantiation of the retained `PREREQ-002` model.
