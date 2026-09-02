# DECISION-021 Naming Migration Prompt

## Initial Naming Instruction From Arko

Prepare a bounded product and repository naming migration:

`DECISION-021: Rename Sybill to Finné Memory`

Confirmed naming:

- Product name: `Finné Memory`
- Repository name: `Finne-Memory`
- Technical slug where accents are unsuitable: `finne-memory`
- Former product name: `Sybill`

This is a naming change only. It does not change the approved product thesis, V1 domain, representative matter, authority model, corpus, permissions, implementation gates or separation from the Finné/x402 project.

Update current-facing documentation so the product is presented as:

> Finné Memory gives autonomous systems institutional memory and precedent for consequential decisions.

Requirements:

1. Search all tracked files for `Sybill`, `Sibyl`, `Sybill-Hackathon`, and the old GitHub URL.
2. Classify every occurrence as current product reference, historical record, immutable saved prompt, repository/path reference, or ambiguous.
3. Replace current product references with `Finné Memory`.
4. Replace current repository references with `Finne-Memory` and the new canonical GitHub URL.
5. Use `finne-memory` only where accents or spaces are technically unsuitable.
6. Preserve historical decisions, logs, reviews, prompts, commit descriptions and PR records that truthfully used “Sybill” at the time.
7. Do not rewrite saved prompts.
8. Add a concise historical annotation where needed: `The product was renamed from Sybill to Finné Memory under DECISION-021. Historical references retain the former name.`
9. Append chronological `DECISION-021` recording the old and new names, the reason for preserving historical references, confirmation that scope and behaviour do not change, and affected current-facing documents.
10. Update `README.md`, current product summaries, governance documents, agent instructions and contribution guidance where the active product name appears.
11. Update `AI_USAGE.md`, `HUMAN_DECISIONS.md` and `BUILD_LOG.md` to record this AI-assisted naming migration.
12. Save this material prompt as `prompts/2026-09-02-rename-product-finne-memory.md`.
13. Do not rename technology-neutral object names such as `DecisionRecord`, `AuthorityEvent`, or `PrecedentRelationship`.
14. Do not alter IDs, fixtures, authority states, citations, policy dates or acceptance criteria.
15. Do not begin `PREREQ-003`, create an implementation `SPEC-*`, create `TASK-001`, write code or install dependencies.

Deliver the exact files proposed for change, occurrence-classification table, exact proposed `DECISION-021`, diff summary, confirmation that product behaviour is unchanged, link and terminology validation, and proposed commit boundary and message. Do not stage or commit. Stop for review.

## Event-Name Correction From Arko

Stop the naming migration immediately.

Do not make further edits. Do not stage, commit, push, merge, restore, reset or discard anything.

The prior instruction was overbroad:

- `Sybill` is the hackathon/event name and must remain unchanged wherever it refers to the event, organizer, rules, eligibility, submission, deadline or event-specific restrictions.
- The product name is `Finné Memory`.
- The repository name is `Finne-Memory`.
- The technical slug is `finne-memory`.

First report every file already changed, every replacement already made, whether anything was staged, committed or pushed, the current Git status, which replacements incorrectly changed event references, and which replacements correctly changed product or repository references. Do not repair anything until Arko approves the classification.

## Approved Classification Instruction From Arko

Classify every occurrence before editing:

- `EVENT` — retain `Sybill`.
- `CURRENT_PRODUCT` — use `Finné Memory`.
- `REPOSITORY` — use `Finne-Memory`.
- `TECHNICAL_SLUG` — use `finne-memory`.
- `HISTORICAL_RECORD` — preserve the original wording.
- `SAVED_PROMPT` — preserve verbatim.
- `AMBIGUOUS` — do not change without approval.

Examples:

- “Sybill hackathon” → retain.
- “Official Sybill event rules” → retain.
- “Sybill provides institutional memory” → change to “Finné Memory provides institutional memory.”
- “Sybill V1 product” → change to “Finné Memory V1 product.”
- Historical decision saying the project was originally called Sybill → preserve, then add the later naming decision.
- Saved prompts → never rewrite.

Produce the classification table and corrected proposed diff. Do not stage or commit.
