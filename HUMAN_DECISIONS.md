# Human Decisions

This ledger records material human decisions, corrections, rejected AI suggestions, and approvals. It supplements the chronological product and architecture log in `DECISIONS.md`; it does not replace it.

## 2026-09-02: Transferable AI Build Governance

- Human decision-maker: Arko.
- Decision reference: `DECISION-019`.
- Decision: Adopt the explicitly listed spec-driven, human-directed, progressively auditable operating rules as mandatory Sybill governance.
- Required exclusions: Do not import the ETHOnline-specific Finne thesis, stablecoin workflow, sponsors, bounties, deadline, prize cap, submission format, or demo requirements.
- Correction to prior process: An approved task or planning prerequisite alone is insufficient for implementation; the bounded `SPEC-*` must also be approved and committed first.
- Human-only controls: Arko approves commits, personally verifies affected product behavior, confirms understanding, and controls merge to the repository’s remote default branch.
- Rejected or deferred suggestions: No unseen PDF content was treated as confirmed. Event-specific Sybill hackathon rules remain `UNRESOLVED`.
- Approval status: Governance direction and the resulting governance checkpoint were approved by Arko after the successful independent second-pass review.

## 2026-09-02: Governance Review Corrections

- Human decision-maker: Arko.
- Decision reference: `DECISION-020`.
- Decision: Separate voluntary build governance into `AI_BUILD_GOVERNANCE.md` and retain `HACKATHON_RULES.md` only as the unresolved official event-rule register.
- Specification clarification: `PREREQ-001` and `PREREQ-002` are planning contracts. No bounded implementation `SPEC-*` exists, and none may be created until `PREREQ-003` is approved.
- Audit correction: Attribute the saved prompts and all materially AI-assisted files; explicitly identify the Arko-supplied lifecycle, stop conditions, and commit checklist as reused text.
- Approval boundary at the correction checkpoint: Staging, commit, push, merge, `PREREQ-003`, and `TASK-001` authorization remained prohibited. The clean second-pass review and later commit approval were subsequently completed; the other prohibitions remain in force unless Arko explicitly changes them.
