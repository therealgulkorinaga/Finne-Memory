# Transferable AI Build Governance Prompt

## Record

- Date: `2026-09-02`
- Human director: Arko
- AI tool: OpenAI Codex desktop agent
- Classification: CONFIRMED
- Scope: Governance documentation only; no application implementation authorized
- Source note: Arko identified `ETHOnline_2026_Solo_AI_Build_Rules(1).pdf` as the source inspiration. The workspace could not independently read the PDF because macOS denied Downloads access, so the repository adopts only the rules explicitly directed below.

## Material Instruction

Adopt the transferable operating rules from the named ETHOnline document as mandatory Sybill build governance. Do not import the ETHOnline-specific Finne product thesis, stablecoin workflow, sponsors, bounties, deadline, prize cap, submission format, or demo requirements.

Require:

1. No one-shot or near-one-shot application generation.
2. No implementation before an approved and committed bounded `SPEC-*`.
3. One bounded feature or coherent repair per branch and pull request.
4. Contemporaneous material prompts and planning artifacts under `prompts/`.
5. Repository-wide and pull-request AI attribution naming tools, prompts, and affected files or components.
6. Maintenance of `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md`.
7. Plain-English explanation of every changed file, critical function, state change, permission boundary, failure path, and deterministic/model boundary.
8. Comments for non-obvious business rules, invariants, security boundaries, and model limitations, not obvious syntax.
9. Automated tests mapped to acceptance criteria.
10. Arko's personal manual verification of affected product behavior.
11. Independent second-pass diff review before merge.
12. Human approval of commits and human-only merge to `main`.
13. Small coherent commits preserving progressive history.
14. Known-good checkpoints before risky changes.
15. No silent changes to the Sybill thesis, authority rules, permissions, schemas, or stable interfaces.
16. No secrets, unexplained reused code, improperly licensed assets, or fabricated audit history.

Adopt this mandatory lifecycle:

`DECIDE → WRITE AND APPROVE SPEC → COMMIT SPEC → CREATE FEATURE BRANCH → SAVE PROMPT → IMPLEMENT BOUNDED SLICE → EXPLAIN CHANGES → TEST → MANUALLY VERIFY → UPDATE AUDIT DOCUMENTS → REVIEW DIFF → COMMIT → OPEN/UPDATE PR → INDEPENDENT REVIEW → FIX AND RETEST → HUMAN MERGE → KNOWN-GOOD CHECKPOINT`

Adopt these absolute stop conditions:

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

Apply this commit gate to every Work and Codex task:

- Named committed `SPEC-*` or documented-fix reference.
- Purpose of the change.
- Exact files changed and why.
- Behavior and state changes.
- Permissions and security implications.
- Deterministic versus model-driven behavior.
- Automated tests and results.
- Manual verification and result.
- Independent-review status.
- AI tools, prompt paths, and assisted files or components.
- Human decisions, corrections, or rejected suggestions.
- Reused components.
- Known limitations.
- Rollback point.
- Confirmation that Arko understands the change.

For documentation-only commits, implementation tests and manual product verification may be `NOT APPLICABLE` only with a stated reason. Documentation validation, internal-link checking, status consistency, AI attribution, and human-decision traceability remain mandatory.

Do not commit the governance changes until Arko approves the exact proposed edits, affected files, and Sybill-specific commit checklist.
