# AI Usage

This is the repository-wide attribution record for material AI assistance. Entries must be contemporaneous and must identify tools, prompt paths, affected files or components, and the nature of assistance. Pull requests must include change-specific attribution as well.

## 2026-09-02: Planning And Governance Documentation

- AI tool: OpenAI Codex desktop agent.
- Human director: Arko.
- Prompt records: `prompts/2026-09-02-transferable-ai-build-governance.md` and `prompts/2026-09-02-governance-review-corrections.md`; prior material planning prompts predate adoption of the mandatory prompt-recording rule and must not be reconstructed as if they were contemporaneous.
- Assisted files: `AGENT_BUILD_INSTRUCTIONS.md`, `AGENTS.md`, `AI_BUILD_GOVERNANCE.md`, `HACKATHON_RULES.md`, `CONTRIBUTING.md`, `TASKS.md`, `ARCHITECTURE.md`, `README.md`, `DECISIONS.md`, `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `REUSED_COMPONENTS.md`, `prompts/2026-09-02-transferable-ai-build-governance.md`, and `prompts/2026-09-02-governance-review-corrections.md`.
- Codex drafting role: Translated Arko's approved requirements into repository governance, lifecycle gates, task authorization, source-boundary language, audit-document structure, and documentation-only validation requirements. Codex drafted and rewrote the listed files under Arko's direction.
- Codex review role: Performed the first independent second-pass review, reported `NOT READY FOR COMMIT`, identified three blockers and three important findings, and then applied only Arko's approved corrections. A clean second-pass review by an independent agent or session is still required.
- Arko's role and approval boundaries: Arko selected the transferable rules and exclusions; required the governance/event-rule split; required the specification-label clarification; approved the prerequisite checkpoint and its commit; and retained exclusive authority over specification approval, commit approval, product-behavior verification, and merge to `main`.
- Source limitation: Codex did not read or verify `ETHOnline_2026_Solo_AI_Build_Rules(1).pdf` in this Work session. The adopted rules came from Arko's saved instructions.
- Implementation code: None.
