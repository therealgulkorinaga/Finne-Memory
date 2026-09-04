# 2026-09-04 Seam (c) Codex Review — Round 2 Of 2

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5. Independent reviewer: Codex, second and — per the two-pass cap — final permitted pass on seam (c).
- Capture status: Drafted by Claude automatically and unasked, per the standing default, and saved to `prompts/` in the same turn as the fixes it reviews (not left only in chat this time).
- Governing outputs under review: fixes applied in response to round 1 (`prompts/2026-09-04-seam-c-codex-review-round-1.md`) — `finne/base/adapter.py` (`BaseExecutionResult.__post_init__`), `finne/memory/schema.py` (`PrecedentRelationshipRecord`, `RelationshipType`), `finne/memory/client.py` (`write_precedent_relationship`, `read_precedent_relationships_from`, tenant-guarded `clear_all_case_data_for_demo_reset`), `scripts/reset_demo.py` (pre-flight residue check), `scripts/session1.py` and `scripts/session2.py` (rewritten W1-W4 timing, explicit owner-override decision, relationship persistence, stop-on-non-authorizing-decision), `tests/test_fresh_session.py` (substantially rewritten), `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md` section 12 (A4/A5 reassigned to `test_base_adapter.py`).
- Review pass cap: this is pass 2 of the 2 permitted independent passes per `DECISION-025`. If this pass finds anything still open, Claude stops and asks Arko how to proceed rather than drafting a third prompt automatically.

## Review Prompt (verbatim, to give to Arko to run against Codex)

Review request: Finné Memory, seam (c) round 2 — fixes for the round 1 findings.

Context: Round 1 found three BLOCKERs, one IMPORTANT, and one NICE-TO-HAVE. All five were fixed. The BLOCKER-1 fix (correct W1-W4 outcome-write timing) had a significant downstream consequence: `session1.py -> session2.py` alone can no longer honestly demonstrate `constrain` citing `DV-001-V1` — `DV-001-V1` has no recorded outcome while `finne/base/adapter.py` remains a stub, so it is correctly ineligible as precedent, and Session 2 now honestly escalates too. This was previously masked by the outcome-timing bug. `SPEC-001` section 12 was corrected to move A4/A5's live-demonstration ownership to `test_base_adapter.py` (seam d), and `test_fresh_session.py` now proves the underlying retrieval/derivation/relationship-persistence logic via a seeded-outcome fixture instead.

Please verify independently (against the live code, not this description):

1. `session1.py`/`session2.py` — confirm W1 (case version), W2 (owner-policy snapshot), and W3 (authority events) are written unconditionally once a decision authorizes a non-zero amount, and W4 (the outcome) is written if and only if `base_result.attempted` is `True` — with `Outcome.FAILURE` (not silently dropped) on an attempted-but-failed result. Confirm no code path can still reach a written `Outcome.SUCCESS` without `base_result.attempted and base_result.success` both true.
2. The owner-override decision construction in `session1.py` (`dataclasses.replace(decision, result=CONSTRAIN, authorized_amount=owner_approved_amount, binding_constraint="owner_manual_approval", ...)`) — is this a correct, coherent `AuthorizationDecision` (check `__post_init__`'s invariants), and does it correctly avoid ever submitting or persisting the engine's original zero-amount escalate decision as if it were what was authorized?
3. `PrecedentRelationshipRecord`/`write_precedent_relationship`/`read_precedent_relationships_from` in `finne/memory/schema.py` and `finne/memory/client.py` — correct append-only semantics, correct journal-search filtering (kind + `from_decision_version_id` match), correct truncation detection reusing the seam (b) pattern? Are `fact_ids`/`citation_ids` populated with real, meaningful values rather than placeholders?
4. `session2.py`'s relationship-writing — is gating it on `_FOLLOWED_DECISION_VERSION_ID in decision.cited_precedents` (rather than on Base having attempted) the right reading of `ACTIVE_DEMO_DESIGN.md` section 7 step 11's "now that DV-002-V1 exists" condition? Or should this wait for W4 too?
5. `reset_demo.py`'s pre-flight check (`_check_no_live_created_residue`) — does it correctly detect every scenario where a same-tenant reset would leave residue, including a run where only `session1.py` (not `session2.py`) has executed?
6. `BaseExecutionResult.__post_init__` — does the enforced contract (unattempted: no success, no hash; attempted-success: non-empty hash required) correctly reject every incoherent construction, and does anything in the current call sites attempt to construct one?
7. `tests/test_fresh_session.py`'s new seeded-outcome test — does seeding `DV-001-V1`'s outcome directly through `MemoryStore` (bypassing `session1.py`) still constitute a genuine test of `session2.py`'s own logic, or does it risk hiding a bug that only a real `session1.py`-produced record would expose?
8. Is there any other place in seam (c) where an outcome, decision, or transaction reference could still be fabricated or misrepresented, that round 1 did not surface?

## Status

Awaiting Arko running this against Codex and pasting back the findings. This is the second and final permitted pass for seam (c) per `DECISION-025`'s cap — any finding still open after this pass will be surfaced to Arko rather than triggering an automatic third round.
