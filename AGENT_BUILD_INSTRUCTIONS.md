# Finné Memory Agent Build Instructions

## Document Status

- CONFIRMED: This document governs how specialized coding agents divide and hand off work.
- CONFIRMED: The product boundary and control line below apply to every agent prompt.
- CONFIRMED: Shared schemas, interfaces, authority rules, and ownership may change only with explicit approval from the Orchestrator and Arko.
- CONFIRMED: The mandatory lifecycle, stop conditions, audit documents, and commit gate below apply to every Work and Codex task.
- UNRESOLVED: Exact application code paths and module ownership. These cannot be assigned until the initial architecture and repository structure are approved.

## 1. Operating Rules

Every agent must read `AGENTS.md`, this document, `AI_BUILD_GOVERNANCE.md`, its assigned task in `TASKS.md`, the referenced specification, relevant PRD and architecture sections, applicable decisions, and `HACKATHON_RULES.md` before changing files.

Every agent prompt must contain this exact control line:

> You are implementing only the assigned spec. Do not add unrelated features, refactor unrelated files, or make product decisions silently. If the spec is ambiguous, stop and ask.

Agents must also:

- Reject one-shot or near-one-shot application generation.
- Implement only from an approved and committed bounded `SPEC-*`, referenced by an assigned task with acceptance criteria.
- Use one feature branch and pull request for one bounded feature or coherent repair.
- Treat `UNRESOLVED` information as unresolved.
- Surface assumptions and stop when they materially affect behavior, architecture, trust, interfaces, or scope.
- Preserve existing public interfaces and shared contracts unless the assigned spec explicitly authorizes a change and the required approvals are recorded.
- Save material prompts and planning artifacts contemporaneously under `prompts/`.
- Maintain `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md` as work occurs.
- Explain every changed file, critical function, state change, permission boundary, failure path, and model/deterministic boundary in plain English.
- Never commit directly. The human-controlled review gate in `AI_BUILD_GOVERNANCE.md` applies before every commit.
- Require Arko's personal manual verification of affected product behavior and an independent second-pass diff review before merge.
- Preserve small, coherent commits and a known-good checkpoint before risky changes.
- Avoid unrelated cleanup, dependency changes, broad rewrites, speculative features, and fabricated audit history.

### Mandatory Lifecycle

Every implementation or coherent repair must follow this order:

`DECIDE → WRITE AND APPROVE SPEC → COMMIT SPEC → CREATE FEATURE BRANCH → SAVE PROMPT → IMPLEMENT BOUNDED SLICE → EXPLAIN CHANGES → TEST → MANUALLY VERIFY → UPDATE AUDIT DOCUMENTS → REVIEW DIFF → COMMIT → OPEN/UPDATE PR → INDEPENDENT REVIEW → FIX AND RETEST → HUMAN MERGE → KNOWN-GOOD CHECKPOINT`

No step may be silently skipped. For documentation-only commits, implementation tests and manual product verification may be `NOT APPLICABLE` only when the reason is recorded; documentation validation, internal-link checking, status consistency, AI attribution, and human-decision traceability remain mandatory.

## 2. Shared Product Boundaries

- CONFIRMED: Finné Memory converts an autonomous agent's remembered operating history into bounded authority for its next action. Amended by `DECISION-022`.
- CONFIRMED: Finné Memory retrieves relevant past cases from Sibyl Memory, applies deterministic authority and citation rules, compares material facts, and emits a binding `AuthorizationDecision` — allow, constrain, block, or escalate — with a readable, citation-backed explanation.
- CONFIRMED: Finné Memory bounds the agent's authority. It does not select the business action within that bound, and the owner permission ceiling is always superior to learned authority.
- CONFIRMED: Finné Memory is not generic agent memory. Sibyl Memory provides persistent memory; Finné Memory converts remembered operating history into bounded, auditable authority.
- CONFIRMED: No agent may redefine Finné Memory as a payment, escrow, x402, refund, settlement, or transaction-dispute product.
- CONFIRMED: No agent may add service-delivery verification or other Finné/x402 behavior to Finné Memory.
- CONFIRMED: Deterministic records own authority status, identifiers, citations, supersession, policy dates, authority transitions, citation validity, and active-authority eligibility.
- CONFIRMED: Model output may assist with extraction, comparison, explanation, and drafting, but may not invent records, alter authority, establish unvalidated citations, override deterministic rules, or make the final decision.

## 3. Repository Ownership Map

Ownership means an agent may edit the listed area only when its assigned task authorizes the edit. It does not grant standing permission to make changes.

| Area | Default owner | Coordination requirement |
| --- | --- | --- |
| `PRD.md`, product specs, product acceptance criteria | Product Spec Agent | Arko approves material product decisions |
| `ARCHITECTURE.md`, cross-component contracts, integration assembly | Orchestrator / Integration Agent | Arko approves material architecture; affected agents review interfaces |
| `DECISIONS.md` | Orchestrator maintains chronology; proposing agent supplies entry | Never rewrite or delete history; Arko approves material decisions |
| `TASKS.md` | Orchestrator / Integration Agent | Product Spec Agent validates product traceability |
| `AGENT_BUILD_INSTRUCTIONS.md`, `AGENTS.md` | Orchestrator / Integration Agent | Arko approves governance or ownership changes |
| `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `REUSED_COMPONENTS.md`, `prompts/` | Orchestrator coordinates; every contributing agent updates its own entries | Entries must be contemporaneous, attributable, and must never fabricate history |
| `AI_BUILD_GOVERNANCE.md` | Orchestrator / Integration Agent | Arko approves voluntarily adopted build-governance changes |
| `HACKATHON_RULES.md` | Product Spec Agent / Submission Agent | Only sourced rules may be marked confirmed; do not invent event rules |
| `README.md`, demo script, pitch and submission material | Submission Agent | Product Spec Agent and Orchestrator review accuracy |
| Shared schemas and conceptual data contracts | Data Model Agent | Orchestrator and Arko approval required before change |
| Deterministic authority and citation behavior | Deterministic Core Agent | Must consume approved shared schemas and authority rules |
| Retrieval and precedent ranking | Retrieval Agent | Must expose approved candidate contract; may not determine authority |
| Model-assisted extraction, comparison, and drafting | AI Analysis Agent | Must consume validated records and expose schema-validated output |
| Backend routes and service orchestration | API Agent | Must consume approved component interfaces; may not redefine them |
| User-facing workflow | Frontend Agent | Must consume approved API contracts; may not encode authority as UI-only logic |
| Tests, adversarial cases, scope and security review | QA / Red Team Agent | May inspect all areas; edits require task-specific ownership or handoff |

RESOLVED: `docs/architecture/PREREQ-003_ARCHITECTURE.md` section 18 defines the concrete, non-overlapping repository layout, and section 17 defines the hard module constraints — `finne/memory/` is the only module importing `sibyl_memory_client`, `finne/base/` is the only module holding key material or reaching the network, `finne/authority/` is pure, and `finne/explain.py` is the only module permitted to call a model. Those constraints are enforced by `tests/test_import_boundaries.py`. The mapping takes effect when `DECISION-023` is approved.

## 4. Agent Roles

### Orchestrator / Integration Agent

- Owns repository structure proposals, approved shared-interface integration, task sequencing, conflict resolution, integration verification, and final technical review.
- May implement only Orchestrator-assigned specs; coordination authority does not imply permission to rewrite another agent's files.
- Must not approve its own material product or architecture change on Arko's behalf.

### Product Spec Agent

- Owns the PRD, bounded feature specifications, acceptance criteria, user and demo flows, and product traceability.
- May prepare product and demo documentation tasks.
- Must not select technical architecture or turn assumptions into confirmed facts without Arko's approval.

### Data Model Agent

- Owns approved schemas for decision records, matters, facts, evidence, sources, policies, citation graphs, authority states, candidates, packets, and briefs.
- May implement only specs that define or realize approved data contracts.
- Must not change authority semantics or shared schemas without Orchestrator and Arko approval.

### Deterministic Core Agent

- Owns approved authority-state behavior, supersession, active-eligibility checks, and citation validation.
- Must expose deterministic results through approved interfaces.
- Must not delegate authority decisions to a model or introduce new status semantics.

### Retrieval Agent

- Owns retrieval and ranking of factually relevant precedent candidates.
- Must expose candidates through the approved `PrecedentCandidate` contract and keep similarity distinct from authority.
- Must not mark a candidate authoritative or modify source records.

### AI Analysis Agent

- Owns model-assisted fact extraction, factual comparison, similarity/difference explanations, and brief drafting within approved schemas.
- Must consume deterministic identifiers and validated context; outputs must be validated before use.
- Must not invent sources or IDs, alter authority, create accepted citation edges, or make the final decision.

### API Agent

- Owns approved backend routes and orchestration between components.
- Must consume and expose approved contracts and preserve trust boundaries.
- Must not move authority, validation, or security rules into an unapproved layer.

### Frontend Agent

- Owns approved user-facing screens, interaction states, and the end-to-end demo workflow.
- Must represent similarity and authority separately and expose defined loading, empty, degraded, and failure states.
- Must not implement security or authority rules only in the client or change API contracts silently.

### QA / Red Team Agent

- Owns independent testing and review for acceptance criteria, scope violations, hallucinated citations, invalid authority transitions, permissions, failure handling, and security boundaries.
- May diagnose across the repository but must not silently rewrite implementation while acting as independent reviewer.
- Must rank findings as `BLOCKER`, `IMPORTANT`, or `NICE-TO-HAVE`.

### Submission Agent

- Owns README accuracy, demo script, pitch material, evidence collection, and final submission checklist.
- Must describe only demonstrated and verified behavior.
- Must not alter product behavior to improve the pitch or invent hackathon requirements.

### Spec Authorization Matrix

An agent may work on a spec category below only when `TASKS.md` assigns that specific task to the role. No role has blanket implementation authority.

| Agent role | Spec categories it may implement |
| --- | --- |
| Orchestrator / Integration Agent | Repository baseline, approved cross-component integration, migrations, and final assembly |
| Product Spec Agent | Product definition, acceptance criteria, user journeys, demo script, and other documentation-only specs |
| Data Model Agent | Approved shared schemas, serialization, provenance, and data-contract validation |
| Deterministic Core Agent | Approved authority transitions, supersession, eligibility, and citation-validation behavior |
| Retrieval Agent | Candidate retrieval, similarity scoring, and precedent ranking within the approved candidate contract |
| AI Analysis Agent | Schema-bound fact extraction, comparison, explanations, and brief drafting |
| API Agent | Approved backend routes and service orchestration |
| Frontend Agent | Approved screens, interaction states, and user workflow |
| QA / Red Team Agent | Test suites, adversarial fixtures, independent review, and security checks explicitly assigned as implementation work |
| Submission Agent | README, demo, pitch, evidence, and submission-readiness documentation |

Any spec spanning more than one category must identify one owning agent, all contributing agents, exact interface boundaries, and an integration task owned by the Orchestrator.

For how this ten-role fleet is currently staffed by two AI tools and Arko, see Section 11.

## 5. Spec Format

Every meaningful implementation spec must define:

- Spec ID and status.
- Goal and actor(s).
- Inputs and outputs.
- State changes.
- Business and deterministic rules.
- Permissions and trust boundaries.
- Interfaces consumed and exposed.
- Failure cases and degraded behavior.
- Invariants.
- Observable acceptance criteria.
- Testing requirements mapped to acceptance criteria.
- Allowed ownership area and files.
- Dependencies.
- Explicit out of scope.
- Stop and escalation conditions.

Specifications must be precise enough that two agents would implement substantially the same behavior.

Implementation may begin only after the bounded `SPEC-*` is explicitly approved by Arko and committed to the repository. A planning prerequisite, task description, chat message, or uncommitted draft is not implementation authorization.

## 6. Handoff Format

Every agent handoff must report:

- Agent role, task ID, and spec ID.
- Status: complete, incomplete, or blocked.
- Files changed and why.
- Interfaces consumed or exposed.
- Product behavior and state changes.
- Acceptance criteria satisfied or unsatisfied.
- Tests added and exact results.
- Manual checks performed.
- Assumptions encountered.
- Known limitations and deferred work.
- Security, privacy, data, or model-boundary implications.
- Decisions or approvals still required.
- Suggested next bounded task, if it follows directly.
- AI tools used, prompt paths, and assisted files or components.
- Human decisions, corrections, and rejected AI suggestions.
- Reused components and their provenance or an explicit `None`.
- Rollback point and independent-review status.
- Whether Arko has verified and understands the affected behavior.

An agent must not report completion when a required test was not run or an acceptance criterion remains unmet.

## 7. Review Protocol

1. The implementing agent explains the change against its task and spec.
2. The Orchestrator checks file ownership, interfaces, integration impact, and unintended scope.
3. The Product Spec Agent checks behavior against the PRD and acceptance criteria when product behavior changed.
4. The QA / Red Team Agent or another independent agent/session performs a second-pass diff review of tests, failure cases, authority and citation integrity, model hallucination risks, permissions, security boundaries, and spec compliance.
5. Arko resolves material product choices and approves shared-schema, interface, authority-rule, architecture, or ownership changes.
6. The human pre-commit gate in `AI_BUILD_GOVERNANCE.md` is completed.
7. Only Arko approves commits and performs the merge to the repository’s remote default branch.

Review findings must identify the violated requirement or risk and be ranked `BLOCKER`, `IMPORTANT`, or `NICE-TO-HAVE`. A `BLOCKER` prevents commit until resolved or explicitly waived by Arko with the rationale recorded.

## 8. Commit Protocol

- Agents do not commit directly.
- Only Arko may approve a commit, and only a human may merge to the repository’s remote default branch.
- One bounded feature or coherent repair belongs on one branch and pull request.
- Small, coherent commits must preserve progressive development history; one-shot or near-one-shot application commits are forbidden.
- The proposed commit must reference its task and spec.
- The full mandatory commit gate in `AI_BUILD_GOVERNANCE.md` must be completed for every Work and Codex task before a commit is proposed for approval.
- Shared-contract or architecture changes require the corresponding accepted entry in `DECISIONS.md` before commit.
- Maintain a known-good checkpoint before risky integration or migration work.

## 9. Forbidden Changes

No agent may, without explicit task scope and required approval:

- Redefine Finné Memory as a payment, escrow, x402, refund, settlement, transaction-dispute, or service-delivery verification product.
- Let Finné Memory select the business action within an authorized bound, exceed the owner permission ceiling, or grant the agent a power the owner did not delegate. Amended by `DECISION-022`: emitting a binding authorization bound is required behavior; selecting the action inside it is not.
- Change shared schemas, public interfaces, authority rules, or file ownership without explicit approval from the Orchestrator and Arko.
- Change permissions, stable interfaces, or the Finné Memory product thesis without explicit approval and a recorded decision.
- Add, remove, or reinterpret an authority status.
- Permit model output to alter deterministic authority or citation facts.
- Add an external integration, framework, major dependency, protocol, security model, or data store.
- Change another agent's owned files or refactor unrelated code.
- Add speculative features or hidden product rules.
- Weaken validation, permissions, auditability, tests, or failure handling to make a demo pass.
- Invent hackathon rules, sponsor requirements, test results, citations, sources, records, or capabilities.
- Commit secrets, credentials, private keys, personal data, unredacted environment files, unexplained reused code, improperly licensed assets, or fabricated audit history.

## 10. Escalation Rules

Stop work and return to the Orchestrator and Arko when:

- The change cannot be mapped to an approved committed specification or documented bug.
- An agent changes the product or adds behavior outside the specification.
- Shared schemas, authority rules, permissions, or interfaces would change without approval.
- Tests fail or acceptance criteria remain unproven.
- Arko cannot explain a critical file, state change, permission, or failure path.
- A model can bypass deterministic authority or citation controls.
- A secret, credential, private key, or unexplained reused component is present.
- The change is too large to review coherently.
- AI attribution or prompt traceability is missing.
- A one-shot generation obscures persistent human contribution.
- The spec is ambiguous in a way that affects behavior, state, permissions, trust, architecture, or acceptance criteria.
- Required product or architecture information is marked `UNRESOLVED`.
- A required interface is missing, contradictory, or would need a breaking change.
- Work would cross file ownership or modify a shared schema or authority rule.
- The assigned task appears to conflict with the PRD, a recorded decision, or hackathon rules.
- A new dependency, external integration, secret, privileged action, or sensitive-data flow is required.
- A model would need to make a deterministic or final decision.
- Tests expose a product-rule ambiguity rather than an implementation defect.
- The agent cannot satisfy an acceptance criterion within assigned scope.
- Existing user changes make the task unsafe to complete without coordination.

The escalation must state the blocking fact, affected spec or interface, options considered, consequences of each option, and the exact decision required. Do not continue by silently selecting an option.

## 11. Two-Tool Operating Model And Commit/Push Clarifications

- CONFIRMED: This section is recorded as `DECISION-025`. It clarifies how the mandatory lifecycle and the role fleet in Sections 4, 7, and 8 are staffed for this build. It changes no product rule, authority rule, or approval boundary; it makes an existing ambiguity explicit.

### Role Staffing For This Build

The ten-role fleet in Section 4 is not staffed by ten separate agents. For the current build:

- **Claude (Claude Code)** performs every implementer role assigned by `TASKS.md` — creates the feature branch, writes the implementation, runs initial tests, and explains the changed files. Claude also performs, as self-checks against its own work, the Section 7 item 2 check (file ownership, interfaces, integration impact, unintended scope — the Orchestrator role) and the Section 7 item 3 check (behavior against the PRD and acceptance criteria when product behavior changed — the Product Spec Agent role). These are named here explicitly so they cannot silently disappear inside a two-tool model: they are self-checks by the implementer, not independent review, and do not substitute for item 4.
- **Codex** is the independent reviewer required by Section 7 item 4, and only item 4. It reviews the diff against the governing specification and, separately, verifies that accepted findings were actually fixed. Using a distinct tool from the implementer is what makes this specific check genuinely independent rather than Claude reviewing Claude; items 2 and 3 above remain self-checks, not independent ones.
- **Arko** manually tests the product, decides which review findings to accept, approves the commit, pushes the branch, opens the pull request, and reviews and merges it. Arko retains every approval, verification, push, PR-creation, and merge action Sections 7 and 8 already reserve to a human.

This is an operating assignment, not a change to Section 4's role definitions. If a future task needs a role Claude and Codex do not jointly cover — for example a domain-specific security review — that gap must be named explicitly rather than assumed covered.

### Review Pass Cap

- CONFIRMED: At most two independent Codex review passes run per bounded change before a commit is proposed for Arko's approval. Claude drafts the review prompt for both passes automatically and unasked, regardless of how small the change looks — that default is unchanged. What is capped is repetition past two passes, not whether the first two happen.
- CONFIRMED: If a finding remains open after the second pass — including a finding Claude believes it already fixed but that has not been independently re-checked — Claude does not draft a third review prompt on its own. Claude stops, states plainly what is still open and why it wasn't resolved within two passes, and asks Arko how to proceed: approve with the fix as Claude's own self-verified correction, direct a specific change and authorize one more pass, or handle the remaining item as a separate follow-up task.
- CONFIRMED: This rule exists because an early run of this exact process drafted a third review prompt by default, with no upper bound, before Arko set this cap. See `DECISION-025` and `BUILD_LOG.md` 2026-09-03 for that instance.

### Commit Execution Clarified

- CONFIRMED: Section 8's "Agents do not commit directly" means an agent may not commit without Arko's prior, explicit, change-specific approval. It does not require Arko to personally type the `git commit` command.
- CONFIRMED: Once Arko has approved a specific commit's content and message, Claude may execute the commit as a tool call. The approval is what authorizes the commit; the keystroke is mechanical.
- CONFIRMED: This clarification does not extend to push, PR creation, or merge. Those remain actions Arko performs personally; see below.

### Push And Pull-Request Boundary

- CONFIRMED: Sections 7 and 8 are explicit that only Arko merges to the repository's remote default branch, but were silent on who pushes a branch or opens a pull request. That gap is closed here.
- CONFIRMED: Arko pushes the branch and opens the pull request personally, using authenticated Bash or the GitHub CLI. No agent runs `git push` or `gh pr create` on Arko's behalf.
- CONFIRMED: Claude may prepare a pull-request title and description for Arko to use, but does not submit it.

### Operating Table

| Action | Owner |
| --- | --- |
| Create feature branch | Claude |
| Write implementation | Claude |
| Run initial tests | Claude |
| Explain changed files | Claude |
| Manually test product | Arko |
| Review diff against specification | Codex |
| Decide which findings to accept | Arko |
| Fix accepted findings | Claude |
| Verify fixes | Codex |
| Approve commit | Arko |
| Create commit | Claude, after Arko's approval |
| Push branch | Arko, from authenticated Bash |
| Open PR | Arko, using GitHub CLI or Bash |
| Write PR draft | Claude may prepare it |
| Review PR and merge | Arko |

- CONFIRMED: Steps not shown in this table remain mandatory. This table assigns owners to steps that already sit inside the Mandatory Lifecycle in `AI_BUILD_GOVERNANCE.md`; it does not reorder that lifecycle. Two steps deserve their exact position stated, not just "folded in," because getting the order wrong would let the audit trail describe things that have not happened yet:
  - `SAVE PROMPT` happens **before** "Write implementation" begins — the material prompt is saved first, then implementation starts from it.
  - `UPDATE AUDIT DOCUMENTS` happens **after** "Manually test product" and after "Verify fixes," once real test results and manual-verification outcomes exist to record, and **before** "Approve commit." It is not tied to "Explain changed files," which only drafts the explanation that later becomes part of those updates; updating `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md` before manual verification has happened would misstate results that are not yet known.

## Mandatory Commit Gate

Every Work and Codex task must provide all of the following before Arko is asked to approve a commit:

- Named committed `SPEC-*` or documented-fix reference.
- Purpose of the change.
- Exact files changed and why.
- Behavior and state changes.
- Permissions and security implications.
- Deterministic versus model-driven behavior.
- Automated tests and results, mapped to acceptance criteria.
- Manual verification and result, performed personally by Arko for affected product behavior.
- Independent-review status.
- AI tools, prompt paths, and assisted files or components.
- Human decisions, corrections, or rejected suggestions.
- Reused components and provenance.
- Known limitations.
- Rollback point.
- Confirmation that Arko understands the change.

For documentation-only commits, implementation tests and manual product verification may be marked `NOT APPLICABLE` with a stated reason. Documentation validation, internal-link checking, status consistency, AI attribution, human-decision traceability, exact changed-file accounting, independent review status, and rollback identification remain required.
