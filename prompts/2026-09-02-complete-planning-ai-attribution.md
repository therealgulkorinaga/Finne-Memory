# Complete Planning-File AI Attribution Prompt

## Record

- Date: `2026-09-02`
- Human director: Arko
- AI tool: OpenAI Codex desktop agent
- Fix reference: `FIX-DOC-002: Complete planning-file AI attribution`
- Scope: `AI_USAGE.md`, `BUILD_LOG.md`, and this prompt only
- Prohibitions: Do not stage, commit, push, modify pull-request metadata, merge, begin `PREREQ-003`, create an implementation specification, or change product, architecture, corpus, authority, or implementation behavior

## Material Instruction

Explicitly attribute AI assistance for `PRD.md` and all six named `PREREQ-001` and `PREREQ-002` planning, corpus, review, and traceability files omitted from the first public pull-request attribution. For each file or precisely bounded group, state whether Codex assisted with drafting, structuring, consistency checking, synthetic-data construction, traceability review, or validation, and distinguish that assistance from what Arko decided, corrected, approved, or withheld.

Disclose that the earlier material prompts predated the mandatory prompt-capture rule and were not reconstructed. Do not invent prompt paths or imply that Arko manually authored AI-generated passages.

Record public draft PR #1 and its URL, the final remote PR-level review, the single incomplete-attribution `BLOCKER`, all seven omitted files, the `NOT READY` result, creation of `FIX-DOC-002`, and the fact that the pull request remains draft and unmerged.

Attribute Codex assistance with this correction prompt and the three affected files. Preserve the implementation gates: `PREREQ-003` remains unresolved, no bounded implementation `SPEC-*` exists, and `TASK-001` remains unauthorized.

After correction, perform an independent read-only review of exactly the three scoped files. The reviewer must not modify files or Git state. Do not stage or commit the correction.
