# AI Usage

This is the repository-wide attribution record for material AI assistance. Entries must be contemporaneous and must identify tools, prompt paths, affected files or components, and the nature of assistance. Pull requests must include change-specific attribution as well.

## 2026-09-02: Planning And Governance Documentation

- AI tool: OpenAI Codex desktop agent.
- Human director: Arko.
- Prompt records: `prompts/2026-09-02-transferable-ai-build-governance.md`, `prompts/2026-09-02-governance-review-corrections.md`, and `prompts/2026-09-02-remote-readiness-documentation-fix.md`; prior material planning prompts predate adoption of the mandatory prompt-recording rule and must not be reconstructed as if they were contemporaneous.
- Assisted files: `AGENT_BUILD_INSTRUCTIONS.md`, `AGENTS.md`, `AI_BUILD_GOVERNANCE.md`, `HACKATHON_RULES.md`, `CONTRIBUTING.md`, `TASKS.md`, `ARCHITECTURE.md`, `README.md`, `DECISIONS.md`, `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `REUSED_COMPONENTS.md`, `prompts/2026-09-02-transferable-ai-build-governance.md`, and `prompts/2026-09-02-governance-review-corrections.md`.
- Codex drafting role: Translated Arko's approved requirements into repository governance, lifecycle gates, task authorization, source-boundary language, audit-document structure, and documentation-only validation requirements. Codex drafted and rewrote the listed files under Arko's direction.
- Codex review role: Performed the first independent review, reported `NOT READY FOR COMMIT`, identified three blockers and three important findings, and then applied only Arko's approved corrections. A clean independent second-pass governance review was subsequently completed against the exact 15-file boundary and all 27 review criteria; it raised no findings at any severity and was accepted by Arko.
- Remote-readiness and correction role: Performed read-only local and remote readiness checks, identified the default-branch terminology and stale review-attribution inconsistencies, and prepared `FIX-DOC-001` under Arko's bounded correction instruction. Assisted correction files are `AGENTS.md`, `AGENT_BUILD_INSTRUCTIONS.md`, `AI_BUILD_GOVERNANCE.md`, `AI_USAGE.md`, `BUILD_LOG.md`, `CONTRIBUTING.md`, `DECISIONS.md`, `HUMAN_DECISIONS.md`, and `prompts/2026-09-02-remote-readiness-documentation-fix.md`.
- Arko's role and approval boundaries: Arko selected the transferable rules and exclusions; required the governance/event-rule split; required the specification-label clarification; approved both documentation checkpoints and their commits; accepted the successful second-pass review; directed `FIX-DOC-001`; and retained exclusive authority over specification approval, commit approval, product-behavior verification, and merge to the repository’s remote default branch.
- Source limitation: Codex did not read or verify `ETHOnline_2026_Solo_AI_Build_Rules(1).pdf` in this Work session. The adopted rules came from Arko's saved instructions.
- Implementation code: None.

## 2026-09-02: FIX-DOC-002 Planning-File Attribution Correction

- Fix reference: `FIX-DOC-002: Complete planning-file AI attribution`.
- AI tool: OpenAI Codex desktop agent.
- Human director: Arko.
- Correction prompt: `prompts/2026-09-02-complete-planning-ai-attribution.md`.
- Historical prompt limitation: The material prompts for the earlier planning work predated the mandatory prompt-capture rule. They were not reconstructed, and no invented prompt path is attributed to that work.

| Materially AI-assisted file or bounded group | Codex assistance | Arko's decisions, corrections, and approval boundary |
| --- | --- | --- |
| `PRD.md` | Drafted and structured product requirements, user flows, boundaries, acceptance criteria, and internal-consistency updates from Arko's direction. | Arko confirmed the Sybill product boundary and the four V1 choices, corrected the human-confirmation boundary, and approved the resulting product-definition checkpoint; this does not imply that Arko manually authored Codex-drafted passages. |
| `docs/product/PREREQ-001_PRODUCT_DEFINITION_PROPOSAL.md` | Drafted and structured the product-definition proposal and reconciled it with the PRD after review. | Arko approved supplier onboarding, the primary user and buyer, the representative beneficial-ownership matter, and the final-decision and human-confirmed write-back boundaries. |
| `docs/product/PREREQ-002_DECISION_RECORD_AND_CORPUS_PROPOSAL.md` and `docs/product/PREREQ-002_REVIEW_PACKET.md` | Drafted and structured the proposed object model, authority workflow, permissions, fixtures, review tables, detected inconsistencies, and approval packet. | Arko withheld blanket approval of incorporated details until exact tables were shown, supplied amendments, and resolved the ten outstanding issues without reopening the product design. |
| `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md` | Converted approved decisions into the technology-neutral decision-record and precedent contract, structured deterministic invariants, and checked consistency across identifiers, authority, citations, policy dates, permissions, and write-back. | Arko approved the amended object model, exact-version references, append-only authority treatment, citation controls, matter versioning, invariants, and deferred technology-specific encodings to `PREREQ-003`. |
| `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md` | Constructed the synthetic data fixtures from approved requirements and performed identifier, relationship, authority-event, citation, temporal, and cross-reference validation. | Arko required a complete seed appendix, retained six primary demo records, required separate `draft` and `questioned` lifecycle fixtures, specified withdrawn and active-baseline behavior, and approved the validated corpus. |
| `docs/product/PREREQ-002_TRACEABILITY_REVIEW.md` | Drafted the documentation review and performed consistency, referential-integrity, temporal/state, invariant, and PRD-traceability validation. | Arko required the documentation and traceability review before closing `PREREQ-002`, reviewed the checkpoint, and approved the completed prerequisite commit; this approval is distinct from the AI-assisted validation work. |

- FIX-DOC-002 assistance: Codex identified the missing attribution during the final public PR-level review and, under Arko's bounded instruction, drafted this correction in `AI_USAGE.md`, recorded it in `BUILD_LOG.md`, and saved `prompts/2026-09-02-complete-planning-ai-attribution.md`.
- Product and implementation effect: None. This correction changes attribution only and does not alter product, architecture, corpus, authority, or implementation behavior.

## 2026-09-02: DECISION-021 Product And Repository Naming Migration

- Decision reference: `DECISION-021: Rename Sybill To Finné Memory`.
- AI tool: OpenAI Codex desktop agent.
- Human director: Arko.
- Prompt record: `prompts/2026-09-02-rename-product-finne-memory.md`.
- Codex assistance: Inventoried every tracked `Sybill`, `Sibyl`, former repository-name, and former GitHub-URL occurrence; classified each occurrence before editing; drafted current-facing naming updates and `DECISION-021`; and checked terminology, links, scope, and Git boundaries.
- Assisted files: `README.md`, `PRD.md`, `AGENTS.md`, `AGENT_BUILD_INSTRUCTIONS.md`, `AI_BUILD_GOVERNANCE.md`, `TASKS.md`, `DECISIONS.md`, `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `docs/product/PREREQ-001_PRODUCT_DEFINITION_PROPOSAL.md`, `docs/product/PREREQ-002_DECISION_RECORD_AND_CORPUS_PROPOSAL.md`, `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, `docs/product/PREREQ-002_REVIEW_PACKET.md`, `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`, and `prompts/2026-09-02-rename-product-finne-memory.md`.
- Arko's decisions and corrections: Arko confirmed `Finné Memory` as the product name, `Finne-Memory` as the repository name, and `finne-memory` as the technical slug. Arko corrected the initial overbroad instruction by confirming that `Sybill` remains the hackathon/event name and directed preservation of historical records and saved prompts.
- Approval boundary: This entry records preparation only. Arko has not approved staging or commit of the migration, and no product behavior or implementation authorization changed.

## 2026-09-03: DECISION-022 Domain Pivot And PREREQ-003 Architecture

- Decision references: `DECISION-022` (controlled domain pivot), `DECISION-023` (architecture).
- AI tool: **Claude Code (Anthropic), model Opus 5.** This is a different tool from the OpenAI Codex desktop agent used for all prior entries in this file. The change of tool is recorded rather than blended into earlier attribution.
- Human director: Arko.
- Prompt record: `prompts/2026-09-03-revised-direction-base-agent-authority.md`, saved contemporaneously before any file in this turn was changed.
- Claude's inspection role: Performed read-only inspection of branch, `HEAD`, working tree, index, remote, commit history, and merged pull-request state; read every document named in Arko's instruction; inventoried supplier-onboarding occurrences across all tracked Markdown; and verified the official event rules and the Sibyl Memory SDK surface from source.
- Claude's drafting role: Drafted `DECISION-022` and `DECISION-023`; rewrote `PRD.md`, `HACKATHON_RULES.md`, `ARCHITECTURE.md`, `TASKS.md`, and `README.md`; created `docs/product/ACTIVE_DEMO_DESIGN.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, and proposed `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`; added historical labels to six `docs/product/` files without rewriting their content; and reconciled three governance statements that the revised authority model contradicted.
- Assisted files: `README.md`, `PRD.md`, `ARCHITECTURE.md`, `TASKS.md`, `DECISIONS.md`, `HACKATHON_RULES.md`, `AGENTS.md`, `AGENT_BUILD_INSTRUCTIONS.md`, `AI_BUILD_GOVERNANCE.md`, `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `REUSED_COMPONENTS.md`, `docs/product/ACTIVE_DEMO_DESIGN.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`, `docs/product/PREREQ-001_PRODUCT_DEFINITION_PROPOSAL.md`, `docs/product/PREREQ-002_DECISION_RECORD_AND_CORPUS_PROPOSAL.md`, `docs/product/PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, `docs/product/PREREQ-002_REVIEW_PACKET.md`, `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`, `docs/product/PREREQ-002_TRACEABILITY_REVIEW.md`, and `prompts/2026-09-03-revised-direction-base-agent-authority.md`.
- Arko's decisions: Arko supplied the revised product thesis, the core authority model and its invariants, the Sibyl/Finné/Base relationship, the two-session demonstration and its exact amounts, the retained precedent model, the deterministic/model split, the architecture direction and its prohibitions, the velocity model, and the prohibition on code, scaffolding, dependencies, contract deployment, and onchain transactions in this turn.
- Claude's escalation: Claude identified that the revised model changes Finné Memory's output from advisory-only decision support to a binding deterministic authorization bound, which contradicts `DECISION-002`, `DECISION-013`, `AGENT_BUILD_INSTRUCTIONS.md` section 2 and section 9, and `AI_BUILD_GOVERNANCE.md`. Claude recorded the change explicitly in `DECISION-022` and reconciled the contradicting statements rather than applying the change silently, and surfaced it to Arko in the end-of-turn report.
- Verification performed and its limits: Official rules were verified on 2026-09-03 from the six official URLs listed in `HACKATHON_RULES.md`. The `sibyl-memory-client` version, licence, Python requirement, and API surface were verified from the PyPI JSON API and the official documentation. **The package is not installed on this machine and was not imported.** The published README documents the v0.4.x API surface while the current release is v0.8.0, so exact signatures are marked `VERIFY-AT-BUILD` in `PREREQ-003` rather than asserted as confirmed.
- Implementation code: None. No application code, scaffolding, dependency installation, contract deployment, or onchain transaction occurred.
- Git operations: None. Nothing was staged, committed, pushed, or merged.

## 2026-09-03: Planning Checkpoint Approval, MIT Licence, And Commit

- Decision reference: `DECISION-024`.
- AI tool: Claude Code (Anthropic), model Opus 5.
- Human director: Arko.
- Prompt record: `prompts/2026-09-03-revised-direction-base-agent-authority.md` and Arko's subsequent approval instruction recorded in `HUMAN_DECISIONS.md`.
- Claude's assistance: Added the MIT `LICENSE`; drafted `DECISION-024`; propagated the `ORG-Q2` resolution across `HACKATHON_RULES.md`, `README.md`, `PRD.md`, `ARCHITECTURE.md`, `TASKS.md`, `AI_BUILD_GOVERNANCE.md`, `REUSED_COMPONENTS.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, and `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`; updated the build sequence to reflect the approvals given; and created the feature branch and commit that Arko approved.
- Arko's decisions: Approved the planning checkpoint and the proposed commit; selected MIT.
- Claude's disclosure: The `LICENSE` copyright holder was inferred as `Arko Ganguli` from repository context, not supplied verbatim. This is flagged in `HUMAN_DECISIONS.md` for correction if a different entity is intended.
- Implementation code: None. No application code, scaffolding, dependency installation, contract deployment, or onchain transaction occurred.

## 2026-09-03: DECISION-025 Two-Tool Operating Model Addendum

- Decision reference: `DECISION-025`.
- AI tool: Claude Code (Anthropic). The session's model was switched mid-conversation from Opus 5 to Sonnet 5 by Arko via the `/model` command, carrying full conversation context forward. This is recorded as a retrospective, unverified self-report in `BUILD_LOG.md`'s 2026-09-03 fix entry below — written during a later corrective pass in the same session, not at the moment of the switch — not as contemporaneous or independent corroboration.
- Human director: Arko.
- Prompt record: `prompts/2026-09-03-two-tool-operating-model.md`. **Correction:** this file was not saved at the time of the original exchange. Claude's first draft of this entry stated the table did not need saving because it was "short" — an unauthorized exception to the prompt-preservation requirement in `AGENT_BUILD_INSTRUCTIONS.md` Section 1, decided unilaterally rather than asked about. An independent Codex review of this addendum flagged the omission as a `BLOCKER`. The prompt file was then written as the correction; it is not backdated to claim contemporaneity it does not have, and this limitation is stated in the file itself.
- Claude's assistance: Compared Arko's proposed table against `AGENT_BUILD_INSTRUCTIONS.md` Sections 7 and 8 before any file was changed, and reported three specific findings — the commit-execution ambiguity, the push/PR gap, and the role-fleet collapse — rather than adopting the table silently. After Arko confirmed, drafted `AGENT_BUILD_INSTRUCTIONS.md` Section 11, `DECISION-025`, and this and the related audit entries. A first-pass independent Codex review then found two BLOCKERs (this unsaved prompt, and a lifecycle-ordering compression affecting `SAVE PROMPT` and `UPDATE AUDIT DOCUMENTS`) and two IMPORTANT findings (this unverifiable model-switch claim, and no named owner for the Section 7 items 2–3 checks). All four were corrected; see `BUILD_LOG.md` for the full review record.
- Assisted files: `AGENT_BUILD_INSTRUCTIONS.md`, `DECISIONS.md`, `HUMAN_DECISIONS.md`, `AI_USAGE.md`, `BUILD_LOG.md`, `prompts/2026-09-03-two-tool-operating-model.md`.
- Arko's decisions: Supplied the operating table; confirmed adopting it formally rather than informally; approved the specific resolution of the commit-execution ambiguity in Claude's favor (Claude may execute a commit after explicit approval) and the push/PR boundary in Arko's favor (Arko performs both personally); ran the independent Codex review that caught the four findings above.
- Product and implementation effect: None. This is a process clarification; no product rule, authority rule, or approval boundary changed.
- Git operation status at time of writing: Not yet committed. Per the protocol this entry itself documents, Claude prepared the change, corrected it against Codex's first-pass review, and is awaiting Arko's explicit approval before executing the commit.

## 2026-09-03: Second Codex Review, Wording Fix, And Review-Pass Cap

- Decision reference: `DECISION-025` (amended).
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, second pass on the same pending change.
- Human director: Arko.
- Claude's assistance: Received Codex's second-pass finding (the "contemporaneous corroboration" overclaim), fixed the wording in all three locations it appeared, then drafted a third review prompt per the then-standing default of drafting review prompts automatically at every step. Arko stopped that before it ran and gave a direct instruction to cap independent review passes at two per bounded change and record that cap in governance immediately. Claude added the cap to `AGENT_BUILD_INSTRUCTIONS.md` Section 11 and to `DECISION-025`, and updated the corresponding feedback memory to reflect the cap rather than leaving the unbounded version in place.
- Assisted files: `AGENT_BUILD_INSTRUCTIONS.md`, `DECISIONS.md`, `AI_USAGE.md`, `BUILD_LOG.md`, `HUMAN_DECISIONS.md`, `prompts/2026-09-03-two-tool-operating-model.md`.
- Arko's decisions: Corrected the "contemporaneous corroboration" wording by way of Codex's finding; directly instructed the two-pass cap; directed that the cap be recorded in the rules immediately rather than only applied informally.
- Product and implementation effect: None. Process clarification only.
- Git operation status: Not yet committed. Two of the two permitted independent passes are complete; the pass-2 fix has not been independently re-verified by a third pass, per the new cap, and this is disclosed rather than presented as confirmed.

## 2026-09-03: HACKATHON_RULES.md AI-Attribution Submission Practice

- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Human director: Arko.
- Claude's assistance: Explained that attribution is unaffected by who runs `git push`, since it lives in commit trailers and the audit trail rather than in the pusher's identity. Drafted the new `HACKATHON_RULES.md` section at Arko's request, explicitly marked as self-imposed rather than an invented official rule, consistent with the document's own integrity requirement not to invent event rules.
- Assisted files: `HACKATHON_RULES.md`, `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Requested the section; explicitly waived the independent Codex review for this specific bounded change ("no need for codex"); directed that this commit not be pushed now and instead be pushed together with the prior commit later.
- Product and implementation effect: None.
- Git operation status: Committed on Claude's execution after Arko's explicit approval, per the standing commit-execution rule in `AGENT_BUILD_INSTRUCTIONS.md` Section 11. Not pushed.

## 2026-09-03: TASKS.md Status Reconciliation

- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Human director: Arko.
- Claude's assistance: Identified that `TASKS.md` no longer reflected reality after `DECISION-025` and the PR #3 merge, and corrected the build-sequence table, `PREREQ-003` status, and the unresolved-dependencies list to match. Explicitly recorded Arko's decision not to run a retroactive Codex review against `d82f224`, rather than silently marking that step complete or omitting it.
- Assisted files: `TASKS.md`, `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Directed the status-only correction; explicitly declined the retroactive independent review of `d82f224`.
- Product and implementation effect: None.
- Git operation status: Committed and merged into `master` via PR #4.

## 2026-09-03: SPEC-001 Review, Correction, And Approval

- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, two passes (the cap) on this bounded change.
- Human director: Arko.
- Claude's assistance: Identified and fixed a self-inflicted status-propagation bug (DECISION-023 described as unapproved in SPEC-001 despite being approved) before presenting SPEC-001 for review; drafted both Codex review prompts automatically per the standing default; fixed all findings from both passes, verifying each against the actual governing source documents (PREREQ-002's PrecedentRelationship and AuthorityEvent definitions, the Authority Transitions table) rather than accepting the review's description at face value; after Arko's approval, propagated the resulting "SPEC-001 approved" status across every live document that referenced it; resolved the resulting merge conflict against PR #4's independent TASKS.md reconciliation.
- Assisted files: ARCHITECTURE.md, DECISIONS.md, PRD.md, README.md, TASKS.md, docs/architecture/PREREQ-003_ARCHITECTURE.md, docs/product/ACTIVE_DEMO_DESIGN.md, docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md, BUILD_LOG.md, AI_USAGE.md.
- Arko's decisions: Directed the move to SPEC-001; ran both independent review passes; approved the resulting fixes and SPEC-001 itself as-is.
- Product and implementation effect: SPEC-001 is now the approved, committed specification governing the first implementation task. No application code exists yet; TASK-001 creation is the next step.
- Git operation status: Committed on Claude's execution after Arko's explicit approval ("approve as-is"), per AGENT_BUILD_INSTRUCTIONS.md section 11.

## 2026-09-03: TASK-001 Definition And Seam (a) Implementation

- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Human director: Arko.
- Prompt record: `prompts/2026-09-03-task-001-and-seam-a-kickoff.md`.
- Claude's assistance: Drafted `TASK-001` per `TASKS.md`'s Required Task Format. Wrote the first application code in this repository: `finne/models.py` (frozen dataclasses, schema-versioned, Decimal-only), `finne/policy.py` and `config/owner_policy.toml` (OP-001/LCP-001), `finne/authority/comparability.py`, `finne/authority/derivation.py`, and `finne/authority/engine.py` (the pure deterministic authority engine), plus three test files including `hypothesis`-based property tests. Made and recorded three routine implementation-level decisions where the governing documents deferred exact detail to implementation: the Python version (3.13.1, since 3.11 is unavailable locally), `HardPolicy`'s schema (a no-op-by-default optional override), and adding `yield_vault_aggressive` to the owner's approved target classes for corpus consistency with `CASE-005`.
- Assisted files: `TASKS.md`, `.gitignore`, `pyproject.toml`, `finne/models.py`, `finne/policy.py`, `finne/authority/comparability.py`, `finne/authority/derivation.py`, `finne/authority/engine.py`, `finne/__init__.py`, `finne/authority/__init__.py`, `finne/memory/__init__.py`, `finne/base/__init__.py`, `config/owner_policy.toml`, `tests/test_authority_invariants.py`, `tests/test_authority_states.py`, `tests/test_comparability.py`, `BUILD_LOG.md`, `AI_USAGE.md`, `prompts/2026-09-03-task-001-and-seam-a-kickoff.md`.
- Arko's decisions: Approved the build sequencing (core before web hosting); directed starting `TASK-001` and seam (a) immediately.
- Product and implementation effect: This is the first working component of Finné Memory's deterministic core. All 17 tests pass, including property tests proving four of the ten `SPEC-001` invariants hold under generated adversarial input, not just the documented demo scenarios.
- Git operation status: Not yet committed. Awaiting test verification (complete), independent review, and Arko's approval.

## 2026-09-03: First Codex Review Of Seam (a) And Corrections

- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, first pass on the seam (a) application code.
- Human director: Arko.
- Claude's assistance: Verified each of Codex's findings against the actual code before fixing (confirmed the float/NaN leak empirically, confirmed the tomllib/Python-version mismatch, confirmed the yield_vault_aggressive widening was functionally unnecessary by tracing that comparability.py never reads owner_policy). Fixed all four findings and added new tests specifically proving each one — not just patching the code silently.
- Assisted files: `finne/models.py`, `finne/authority/engine.py`, `config/owner_policy.toml`, `pyproject.toml`, `tests/test_authority_invariants.py`, `tests/test_authority_states.py`, `tests/test_models_validation.py` (new), `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Ran the independent Codex review.
- Product and implementation effect: No product behavior changed beyond correctness fixes to already-described seam (a) behavior. Test count grew from 17 to 59.
- Git operation status: Not yet committed. One of two permitted independent passes complete.

## 2026-09-03: Second Codex Review Of Seam (a) And Final Corrections

- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, second and final pass on seam (a) per the two-pass cap.
- Human director: Arko.
- Claude's assistance: Verified the TOML float-precision finding empirically before fixing (confirmed `Decimal(0.1)`'s exact expansion). Fixed the loader boundary and added `tests/test_policy.py`; added the two missing direct validation-coverage tests.
- Assisted files: `finne/policy.py`, `tests/test_policy.py` (new), `tests/test_models_validation.py`, `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Ran the second independent Codex review.
- Product and implementation effect: No product behavior changed beyond correctness fixes. Test count grew from 59 to 78.
- Git operation status: Not yet committed. Two of two permitted independent passes complete.

## 2026-09-04: Seam (b) — Sibyl Memory Adapter

- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Human director: Arko.
- Prompt record: `prompts/2026-09-04-seam-b-memory-adapter-kickoff.md`.
- Claude's assistance: Performed the VERIFY-AT-BUILD step by installing and empirically exercising sibyl-memory-client 0.8.0 against a real local database before writing any adapter code, rather than trusting the published (outdated) README. Designed and implemented finne/memory/schema.py and finne/memory/client.py, and wrote 21 round-trip tests against real temporary databases. Found and fixed a real bug during implementation (get_reference's JSON-stringified body shape) via a failing test, not by inspection. Corrected five already-approved documents to match verified reality, distinguishing fact-correction from a new architecture decision. Made finne/models.py's validation helpers public for reuse. Caught and corrected a process slip — this work had started directly on master instead of a feature branch — before any commit.
- Assisted files: `finne/memory/schema.py`, `finne/memory/client.py`, `tests/test_memory_roundtrip.py`, `finne/models.py`, `HACKATHON_RULES.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`, `ARCHITECTURE.md`, `TASKS.md`, `BUILD_LOG.md`, `AI_USAGE.md`, `prompts/2026-09-04-seam-b-memory-adapter-kickoff.md`.
- Arko's decisions: Confirmed the seam (a) merge; directed the start of seam (b).
- Product and implementation effect: Memory is now genuinely wired to persistence, though not yet connected to the authority engine (that's seam (c)). 99 tests pass, including 21 new round-trip tests against real Sibyl Memory databases.
- Git operation status: Not yet committed. Awaiting independent review and Arko's approval.

## 2026-09-04: Second Codex Review Of Seam (b) And Final Corrections

- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, second pass, verified live against the installed package rather than reading claims.
- Human director: Arko.
- Claude's assistance: Re-verified all four BLOCKER findings by directly reproducing Codex's exact test conditions against the live installed sibyl-memory-client before fixing anything (confirmed the limit//4 cap empirically across five limit values; confirmed the illegal transitions were genuinely acceptable before the fix). Fixed all six findings with a two-layer design for the transition matrix (intrinsic per-event validation plus cross-event chain consistency) and a truncation-detection design for the search cap, rather than superficial patches. Corrected an additional overclaim in PREREQ-003's prose discovered while fixing the documentation finding. Added 11 new regression tests, each proving one specific finding is fixed, and directly re-confirmed all four original bug scenarios against the live package after fixing.
- Assisted files: `finne/memory/schema.py`, `finne/memory/client.py`, `tests/test_memory_roundtrip.py`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Ran the second independent Codex review.
- Product and implementation effect: No product behavior changed beyond correctness fixes to already-described seam (b) behavior. Test count grew from 99 to 110.
- Git operation status: Not yet committed. Two of two permitted independent passes complete.

## 2026-09-04: Seam (c) — Retrieval And The Two Session Scripts

- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Human director: Arko.
- Prompt record: `prompts/2026-09-04-seam-c-retrieval-sessions-kickoff.md`.
- Claude's assistance: Implemented `finne/retrieval.py` connecting seam (a)'s authority engine to seam (b)'s memory adapter for the first time; a minimal, explicitly-labeled Base adapter stub distinguishing "not yet built" from "genuinely failed" so the demo is runnable before seam (d) exists; `scripts/reset_demo.py`, `session1.py`, and `session2.py` implementing the full two-session demo per `ACTIVE_DEMO_DESIGN.md`. Smoke-tested the complete flow end to end against real temporary databases before writing the automated test. Wrote `tests/test_fresh_session.py` using real `subprocess.run()` calls specifically because an in-process import cannot prove A3's fresh-process claim. Found a real bug through that test, not by inspection: `clear_all_case_data_for_demo_reset()` cannot clear `DV-001-V1`'s owner-policy-snapshot reference or authority-event journal entries, because `sibyl-memory-client` exposes no delete for either — correctly diagnosed as write-once immutability (invariant 8) working as designed, not a defect to patch around, and fixed by scoping the repeatable-rehearsal test to start from a fresh database file rather than weakening any immutability guarantee.
- Assisted files: `finne/retrieval.py` (new), `finne/base/adapter.py` (new), `finne/demo_config.py` (new), `finne/memory/client.py` (`clear_all_case_data_for_demo_reset()` added), `scripts/reset_demo.py` (new), `scripts/session1.py` (new), `scripts/session2.py` (new), `tests/test_retrieval.py` (new), `tests/test_fresh_session.py` (new), `BUILD_LOG.md`, `AI_USAGE.md`, `prompts/2026-09-04-seam-c-retrieval-sessions-kickoff.md`.
- Arko's decisions: Confirmed the seam (b) merge; directed the start of seam (c) ("yes go ahead on seam (c)").
- Product and implementation effect: The two-session demo is now runnable end to end for the authority-and-memory claim — Session 1 escalates at cold start and persists a constrained precedent; Session 2, a genuinely fresh process, retrieves it and autonomously constrains 25,000 to 10,000, citing it by name; the memory-emptied control escalates. The Base-execution claim remains seam (d)'s scope. 124 tests pass, including 14 new (5 subprocess-based, 9 retrieval).
- Git operation status: Not yet committed. Awaiting independent review and Arko's approval.

## 2026-09-04: First Codex Review Of Seam (c) And Corrections

- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, first pass on the seam (c) application code.
- Human director: Arko.
- Claude's assistance: A second, stale Codex response (reviewing pre-seam-(b)-round-2 code) was pasted first — identified as stale by checking the live test count and confirming every cited finding's fix marker was already in the tree, before asking Arko to confirm; Arko then sent the correct seam (c) review. Verified every finding against the live code and the governing docs before fixing anything: re-read `PREREQ-003` section 3's W1-W4 table to settle the outcome-timing question precisely (W1-W3 write on owner/decision confirmation, independent of Base; W4 only after Base settles), and re-read `ACTIVE_DEMO_DESIGN.md` section 7 step 11 to confirm the `PrecedentRelationship` persistence Claude had previously scoped out was actually required (a genuine unauthorized scope-narrowing on Claude's part, not a defensible interpretation). Fixed all three BLOCKERs, the IMPORTANT finding, and the NICE-TO-HAVE. Discovered and disclosed a significant downstream consequence of the correct BLOCKER-1 fix: `session1.py -> session2.py` can no longer honestly demonstrate A4/A5 (constrain citing `DV-001-V1`) until seam (d) exists, since W4's outcome-write timing means `DV-001-V1` has no eligible precedent without a real Base attempt — corrected `SPEC-001` section 12's test-mapping table accordingly (fact-correction: the design was already right, the table's assignment wasn't) and added a new test proving `session2.py`'s own constrain/cite/relationship logic directly via a seeded-outcome fixture, matching the technique `reset_demo.py` already uses for its synthetic corpus.
- Assisted files: `finne/base/adapter.py`, `finne/memory/schema.py`, `finne/memory/client.py`, `scripts/reset_demo.py`, `scripts/session1.py`, `scripts/session2.py`, `tests/test_fresh_session.py`, `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md`, `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Ran the first independent Codex review; corrected which review output was current mid-conversation.
- Product and implementation effect: No net new product capability, but a materially more honest one — `DV-001-V1`/`DV-002-V1` no longer get a fabricated outcome, `PrecedentRelationship` records are now actually persisted, and `reset_demo.py` fails clearly instead of leaving a confusing crash for a later run. The live two-session demo's A4/A5 claim now genuinely depends on seam (d), which was previously masked. Test count grew from 124 to 126 (net, after removing now-false assertions and adding the seeded-outcome and reset-residue tests).
- Git operation status: Not yet committed. One of two permitted independent passes complete.

## 2026-09-04: Second Codex Review Of Seam (c) And Final Corrections

- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, second and final permitted pass on seam (c).
- Human director: Arko.
- Claude's assistance: Reproduced every finding directly before fixing anything — the `BaseExecutionResult` truthiness gap (`attempted="yes", success="yes", tx_hash=123` constructed without error) and the `--owner-approved-amount 0` gap (activated as `ACTIVE` precedent authorizing `0.00`) were both confirmed live against real code/temporary databases, not taken on trust. For the `PrecedentRelationship` finding, read `PREREQ-002`'s full entity table to understand exactly what "validated `CitationID`" requires (a separate `CitationEdge` entity with its own validation and rejection-audit path) before deciding: rather than build that subsystem under time pressure for a feature required by none of `SPEC-001`'s fourteen acceptance criteria, took Codex's own offered alternative and fully removed the round-1 relationship-persistence code, correcting `ACTIVE_DEMO_DESIGN.md` to disclose the deferral explicitly with its rationale rather than silently reverting. Also reconciled `PREREQ-003`'s test table, which the round-1 `SPEC-001` correction had left inconsistent.
- Assisted files: `finne/base/adapter.py`, `finne/memory/schema.py`, `finne/memory/client.py`, `scripts/reset_demo.py`, `scripts/session1.py`, `scripts/session2.py`, `tests/test_fresh_session.py`, `docs/product/ACTIVE_DEMO_DESIGN.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, `BUILD_LOG.md`, `AI_USAGE.md`.
- Arko's decisions: Ran the second independent Codex review.
- Product and implementation effect: No product capability removed beyond the deferred (never-working-correctly) relationship persistence; five real bugs fixed (type-coherence gap in the Base result contract, zero-amount approval activating as precedent, an incomplete reset residue check, two stale test-mapping documents). Test count unchanged at 126 (net: relationship assertions removed, no new tests needed for the deferral itself).
- Git operation status: Not yet committed. Two of two permitted independent passes complete. Per `AGENT_BUILD_INSTRUCTIONS.md` section 11, a third pass requires Arko's explicit direction — not drafted automatically.
