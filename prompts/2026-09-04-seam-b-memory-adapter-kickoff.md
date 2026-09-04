# 2026-09-04 Seam (b) Kickoff: Sibyl Memory Adapter

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Capture status: Contemporaneous, saved before this turn's file changes.
- Governing outputs: `finne/memory/schema.py`, `finne/memory/client.py`, `tests/test_memory_roundtrip.py`, and corrections to `HACKATHON_RULES.md`, `PREREQ-003_ARCHITECTURE.md`, `SPEC-001`, `ARCHITECTURE.md`, `TASKS.md` reflecting the empirically-verified `sibyl-memory-client` API.

## Material Instruction From Arko (verbatim)

> I have merged lets go to (b)

Confirming the seam (a) PR (`#7`) was merged, and directing the start of seam (b) — "the Sibyl Memory adapter and round-trip tests" — per the build order already named in `SPEC-001` section 14 and authorized under `TASK-001`.

## Interpretation Notes Recorded By Claude

- Before writing any adapter code, Claude installed the real `sibyl-memory-client==0.8.0` package and empirically verified its API against a live local database — not just read the published documentation, which was already known (per `DECISION-023`) to describe an older surface. This is the `VERIFY-AT-BUILD` step `SPEC-001` and `PREREQ-003` both named as the first required action of this seam.
- Material findings from that verification, all confirmed by direct construction and exercise, not inference:
  1. `MemoryClient.local()` requires no `sibyl init` credentials for local operations — `account_id`/`session_token`/`credentials_*` are optional kwargs defaulting to `None`. This resolves `HACKATHON_RULES.md`'s `ORG-Q3`, previously recorded as requiring judges to have their own credentials.
  2. `set_entity` does not enforce immutability — it silently overwrites. Confirmed the adapter-level immutability design in `PREREQ-003` section 3 is necessary, not optional.
  3. `get_entity` raises `NotFoundError` for a missing name; `get_reference` and `get_state` return `None` instead — an inconsistency not documented anywhere.
  4. `write_event`'s real signature (`evaluated`, `acted`, `forward`, `extra`, `ts`) has no generic payload slot; authority events are encoded via `extra` with a `kind` tag.
  5. `read_events(limit=...)` returns entries in descending timestamp order with no content filter, making it unreliable for retrieving "every event for this decision version" once a tenant has more events than the limit. `client.search(query, tiers=("journal",))` was verified to reliably content-filter the journal tier via FTS5 instead, and was used for R3. The `AE-<zero-padded-sequence>` fallback `PREREQ-003` had proposed was not needed.
  6. `get_reference`'s return shape differs from `get_entity`'s: a dict body passed to `set_reference` comes back JSON-stringified under a `"body"` key, not re-parsed into a nested dict. Found via a failing round-trip test during implementation, not anticipated in advance.
- These findings materially corrected several already-approved documents (`HACKATHON_RULES.md`, `PREREQ-003_ARCHITECTURE.md`, `SPEC-001`, `ARCHITECTURE.md`, `TASKS.md`). Claude treated this as the same category of fact-correction as the earlier `DECISION-023` status-propagation fixes — updating stale claims to match verified reality — not as a new architecture decision requiring a fresh approval cycle, since the underlying design (immutability enforced above the store, authority state derived by folding, R1-R5/W1-W5 boundary) was unchanged; only the exact mechanism for R3 and the credential claim were corrected.
- Claude also made `finne/models.py`'s validation helpers (`require_finite_decimal`, `require_positive_or_zero`, `require_nonempty`) public (dropped the leading underscore) so `finne/memory/schema.py` could reuse them for the same Decimal-only discipline Codex required in seam (a), rather than duplicating the logic. This is a mechanical, non-behavioral rename; seam (a)'s full test suite was re-run and confirmed unaffected.
- Claude noticed, while committing, that no feature branch had been created for this seam's work — it had been done directly against a checked-out `master`. Corrected before anything was committed by creating `feature/seam-b-memory-adapter` and carrying the uncommitted work onto it, per the standing one-bounded-change-one-branch practice.
