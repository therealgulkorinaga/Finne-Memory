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
