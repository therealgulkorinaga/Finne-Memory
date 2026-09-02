# AI Build Governance

## Source Status

- CONFIRMED: These are voluntarily adopted Sybill build-governance controls, not verified official event rules.
- CONFIRMED: This repository also follows the spec-driven AI coding playbook previously extracted from `Hackathon_AI_Coding_Rules.pdf`.
- CONFIRMED: Arko directed the project to adopt the transferable operating rules listed in the prompt saved at `prompts/2026-09-02-transferable-ai-build-governance.md` as mandatory Sybill build governance.
- CONFIRMED: The named `ETHOnline_2026_Solo_AI_Build_Rules(1).pdf` was not readable from this workspace because macOS denied access to Downloads. This repository therefore attributes the newly adopted rules to Arko's explicit instruction and does not claim independent verification of that PDF.
- CONFIRMED: No ETHOnline-specific Finne product thesis, stablecoin workflow, sponsor, bounty, deadline, prize cap, submission format, or demo requirement is imported into Sybill.
- CONFIRMED: Official event eligibility, restrictions, deadlines, submission requirements, and technical constraints are tracked separately in `HACKATHON_RULES.md`.

## Human-Directed Development Model

- CONFIRMED: AI coding agents may write implementation code only within an approved, committed, bounded specification.
- CONFIRMED: Arko owns product decisions, specification approval, manual verification, commit approval, and merge to the repository’s remote default branch.
- CONFIRMED: The current remote default branch is `master`. The human-only merge rule follows the remote default branch if its name changes.
- CONFIRMED: One-shot and near-one-shot application generation are forbidden because they obscure progressive development and persistent human contribution.
- CONFIRMED: One bounded feature or coherent repair belongs on one feature branch and pull request.
- CONFIRMED: Commits must be small, coherent, explainable, attributable, and preserve progressive development history.
- CONFIRMED: A known-good checkpoint must exist before risky changes and after a human-approved merge.

## Mandatory Lifecycle

Every implementation or coherent repair must follow this lifecycle in order:

`DECIDE → WRITE AND APPROVE SPEC → COMMIT SPEC → CREATE FEATURE BRANCH → SAVE PROMPT → IMPLEMENT BOUNDED SLICE → EXPLAIN CHANGES → TEST → MANUALLY VERIFY → UPDATE AUDIT DOCUMENTS → REVIEW DIFF → COMMIT → OPEN/UPDATE PR → INDEPENDENT REVIEW → FIX AND RETEST → HUMAN MERGE → KNOWN-GOOD CHECKPOINT`

No implementation may begin before its bounded `SPEC-*` is approved by Arko and committed. A task, planning prerequisite, chat instruction, or uncommitted specification draft is not implementation authorization.

## Specification And Scope Control

Every implementation task must reference one approved, committed `SPEC-*` or one documented repair for behavior already governed by a committed specification.

Every bounded specification must define:

- Spec ID and approval status.
- Goal and actors.
- Inputs and outputs.
- Behavior and state changes.
- Business and deterministic rules.
- Permissions and trust boundaries.
- Interfaces consumed and exposed.
- Failure paths and degraded behavior.
- Deterministic versus model-driven behavior.
- Invariants.
- Observable acceptance criteria.
- Automated tests mapped to acceptance criteria.
- Allowed files and ownership area.
- Dependencies and rollback considerations.
- Explicit exclusions.
- Stop and escalation conditions.

No agent may silently change the Sybill thesis, authority rules, permissions, schemas, stable interfaces, security boundaries, or product behavior. Material changes require Arko's approval, an updated specification, and a chronological entry in `DECISIONS.md` before implementation.

## Prompt And AI Attribution

- Material prompts and planning artifacts must be saved contemporaneously under `prompts/`.
- `AI_USAGE.md` must identify AI tools, prompt paths, affected files or components, and the nature of assistance at repository and change level.
- Every pull request must identify the AI tools used, relevant prompt paths, and assisted files or components.
- `HUMAN_DECISIONS.md` must record Arko's material decisions, corrections, rejected suggestions, and approvals.
- `BUILD_LOG.md` must chronicle bounded work, tests, manual verification, reviews, commits, pull requests, merges, and known-good checkpoints.
- `REUSED_COMPONENTS.md` must identify reused code, libraries, assets, datasets, templates, licenses, sources, and modifications, or explicitly record that none were introduced.
- Audit history must be contemporaneous and truthful. Fabricated or retroactively invented attribution is forbidden.

## Explanation Standard

Before commit approval, the change must include a plain-English explanation of:

- Every changed file and why it changed.
- Every critical function or module affected.
- Every behavior and state change.
- Every permission and security boundary affected.
- Every failure path and degraded behavior affected.
- Every deterministic versus model-driven boundary affected.
- Known limitations and deliberate exclusions.

Arko must be able to explain each critical file, state change, permission boundary, and failure path before approving the commit.

## Code Commenting Standard

Comments are required where they explain non-obvious:

- Business rules.
- Invariants and state-transition restrictions.
- Permission or security boundaries.
- Model limitations, validation boundaries, and fallback behavior.
- Necessary workarounds or dependency constraints.

Comments must not narrate obvious syntax, assignments, loops, conditionals, or self-explanatory calls.

## Testing And Verification

- Automated tests must map explicitly to specification acceptance criteria.
- Critical state transitions and permission boundaries require positive and negative tests.
- Authority and citation controls must be deterministic and tested against model bypass attempts.
- Model-assisted behavior requires schema validation, bounded inputs and outputs, malformed-output handling, and unavailable-model behavior.
- Arko must personally verify affected product behavior and record the result before commit approval.
- An independent agent, session, or reviewer must perform a second-pass diff review before merge.
- Failed tests or unproven acceptance criteria block commit and merge.

For documentation-only commits, implementation tests and manual product verification may be marked `NOT APPLICABLE` only with a stated reason. Documentation validation, internal-link checking, status consistency, AI attribution, human-decision traceability, and an independent-review status remain mandatory.

## Mandatory Commit Gate

Every Work and Codex task must provide this completed checklist before asking Arko to approve a commit:

- Named committed `SPEC-*` or documented-fix reference.
- Purpose of the change.
- Exact files changed and why.
- Behavior and state changes.
- Permissions and security implications.
- Deterministic versus model-driven behavior.
- Automated tests and results mapped to acceptance criteria.
- Manual verification and result.
- Independent-review status.
- AI tools, prompt paths, and assisted files or components.
- Human decisions, corrections, or rejected suggestions.
- Reused components and provenance.
- Known limitations.
- Rollback point.
- Confirmation that Arko understands the change.

Agents do not approve commits. Arko provides human commit approval, and only a human may merge to the repository’s remote default branch.

## Pull Request And Review Rules

- A pull request must cover one bounded feature or coherent repair.
- The pull request must reference its committed specification or documented fix and acceptance criteria.
- The pull request must contain the completed commit gate and link its prompt and audit records.
- Independent review must diagnose before editing and check scope, behavior, tests, permissions, authority and citation integrity, model boundaries, security, dependencies, reused components, and rollback safety.
- Findings are ranked `BLOCKER`, `IMPORTANT`, or `NICE-TO-HAVE`.
- A `BLOCKER` prevents merge until fixed and retested or explicitly resolved by Arko with the rationale recorded.
- The implementing agent may fix approved findings, but the independent reviewer must recheck the resulting diff.

## Security, Licensing, And Repository Hygiene

- Never commit secrets, credentials, private keys, access tokens, personal data, or unredacted environment files.
- Never include unexplained reused code, improperly licensed assets, or components without provenance.
- Dependency additions must be justified, reviewed, licensed appropriately, and recorded in `REUSED_COMPONENTS.md` and relevant architecture documentation.
- Privileged actions must be narrow, explicit, and enforced at the correct deterministic boundary.
- Models must not create or bypass authority events, accepted citations, permissions, human confirmations, or final outcomes.
- Never fabricate tests, audit events, prompts, reviews, human decisions, commits, or development history.

## Absolute Stop Conditions

Stop work immediately and return to Arko and the Orchestrator when:

- The change cannot be mapped to an approved committed specification or documented bug.
- An agent changes the product or adds behavior outside the specification.
- Shared schemas, authority rules, permissions, or interfaces change without approval.
- Tests fail or acceptance criteria are unproven.
- Arko cannot explain a critical file, state change, permission, or failure path.
- A model can bypass deterministic authority or citation controls.
- A secret, credential, private key, or unexplained reused component is present.
- The change is too large to review coherently.
- AI attribution or prompt traceability is missing.
- A one-shot generation obscures persistent human contribution.

Work also stops when required information is `UNRESOLVED`, ownership would be crossed, a dependency or integration lacks approval, independent review finds an unresolved `BLOCKER`, or completing the change would require an undocumented product or architecture decision.

## Sybill Product Guardrails

- No agent may redefine Sybill as a payment, escrow, x402, refund, settlement, transaction-dispute, transaction-performance-verification, or service-delivery-verification product.
- Sybill does not make the final supplier outcome.
- Similarity, authority, precedent treatment, and outcome remain separate.
- Models may assist extraction, comparison, explanation, and drafting but cannot establish deterministic authority or citation facts.
- Shared schemas, stable interfaces, authority rules, permissions, and ownership require explicit Orchestrator and Arko approval.
- The exact implementation-agent control line in `AGENT_BUILD_INSTRUCTIONS.md` is mandatory.

## Official Event-Rule Boundary

- CONFIRMED: `HACKATHON_RULES.md` is the sole register for verified official Sybill event rules.
- CONFIRMED: Unresolved official event restrictions block implementation authorization until they are explicitly resolved or ruled inapplicable.
- CONFIRMED: This governance document does not establish event eligibility, sponsor requirements, submission requirements, deadlines, or technical restrictions.
