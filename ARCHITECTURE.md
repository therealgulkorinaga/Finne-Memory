# Architecture

## Architecture Status

DECIDED — PENDING ARKO'S APPROVAL

The full architecture is `docs/architecture/PREREQ-003_ARCHITECTURE.md`, recorded as `DECISION-023`. This file is the summary and the standing constraint register. `PREREQ-003` is complete as a proposal; approval unblocks `SPEC-001`.

## System Overview

Three layers, one process.

```
   Owner policy (TOML, read-only)
              |
              v
   +---------------------------+
   |  Finné Memory             |   authority layer
   |  comparability            |
   |  learned-constraint       |
   |  deterministic engine     |
   +---------------------------+
      |  reads              ^  writes
      v                     |
   +---------------------------+
   |  Sibyl Memory             |   mandatory persistent substrate
   |  local SQLite + FTS5      |
   +---------------------------+
              ^
              |  outcome evidence
   +---------------------------+
   |  Base                     |   execution and evidence layer
   |  AuthorizationReceipt     |
   +---------------------------+
```

Finné derives the permitted action → the agent executes it on Base → the transaction result becomes outcome evidence → the outcome is written into Sibyl Memory → a future fresh session recalls and uses it.

## Technical Constraints

- CONFIRMED: Python 3.11. One installable package, `finne`. `venv` and `pip`.
- CONFIRMED: `sibyl-memory-client` is the sole store of remembered agent experiences. No Supabase, PostgreSQL, pgvector, Pinecone, or other database may hold that state, and no second cache of case content exists.
- CONFIRMED: No LangChain, no microservices, no agent-orchestration framework, no cloud infrastructure, no hosted service.
- CONFIRMED: The authority engine is pure. No I/O, no clock, no network, and no imports from the memory or Base modules.
- CONFIRMED: The deterministic path runs with no model API key present, and the test suite and recorded demo both run that way.
- CONFIRMED: Decimal amounts use `decimal.Decimal`. Float arithmetic is prohibited in the authority path.

## Application Boundaries

| Module | Hard constraint |
| --- | --- |
| `finne/memory/` | Only module importing `sibyl_memory_client` |
| `finne/authority/` | Pure; may not import `finne.memory` or `finne.base` |
| `finne/base/` | Only module holding key material or reaching the network |
| `finne/explain.py` | Only module permitted to call a model; no import path to `finne.base` |
| `finne/cli.py` | Presentation only; no authority logic |

Enforced by `tests/test_import_boundaries.py`, not by convention alone. Full layout is section 18 of `PREREQ-003`.

## Data Model

The `PREREQ-002` object model is retained: immutable matter and decision versions, facts, evidence, sources, canonical fact-evidence links, policy versions, validated citations, precedent relationships, append-only authority events, owner confirmation, provenance, and rejected citation-attempt audit events. Authority states are `draft`, `active`, `questioned`, `superseded`, and `withdrawn`.

Two encoding decisions make that model work on an overwritable key-value store:

- Immutability is enforced in `finne/memory/client.py`, which refuses to overwrite an existing immutable record. Correction creates a new version identifier.
- Current authority state is **derived** by folding the append-only authority journal, never stored as a mutable field.

`archive_entity` is deliberately unused: withdrawn and superseded cases must stay retrievable while being ineligible to authorize.

## Integrations

| Integration | Role | Genuine work |
| --- | --- | --- |
| Sibyl Memory | Mandatory persistent substrate | Load-bearing reads R1–R4 and writes W1, W3, W4 (`PREREQ-003` section 3). Remove them and the agent cannot derive learned authority. |
| Base | Execution and evidence layer | `AuthorizationReceipt` contract records the authorized policy amount and a facts hash; the transaction result is the outcome evidence that feeds derivation eligibility. |
| Anthropic model | Optional explanation only | Absent by default. Cannot affect any authorization result. |

UNRESOLVED: `ORG-Q1` in `HACKATHON_RULES.md` — Base mainnet versus Base Sepolia. The build targets Sepolia and the network is a single configuration value.

## Security And Privacy

- CONFIRMED: The signing key is read from `FINNE_BASE_PRIVATE_KEY` inside `finne/base/adapter.py` and nowhere else. It is never passed to the engine, never written to Sibyl Memory, never logged, and never committed.
- CONFIRMED: The demo wallet is a throwaway holding only testnet gas.
- CONFIRMED: A model may never sign, submit, or construct a transaction.
- CONFIRMED: Owner policy is read-only to the application. No code path writes it, so the agent cannot rewrite its own authority policy.
- CONFIRMED: Records are validated on read. A malformed record is treated as absent, never as permission.
- CONFIRMED: Every demonstration transaction carries zero value. Authorized amounts are policy values, not transfers.

## Testing Strategy

`pytest`, plus `hypothesis` for the ceiling invariant. Eight test files map to the acceptance criteria; the table is section 14 of `PREREQ-003`.

Two are load-bearing for the project's central claims:

- `test_fresh_session.py` runs both sessions as **subprocesses**. Anything less would not prove cross-session behaviour.
- The memory-deleted control is an automated test, so the organiser's deletion gate runs in CI rather than only on camera.

## Deployment Strategy

Nothing is hosted. The deliverable is a repository plus a recorded demo. The only deployed artifact is the `AuthorizationReceipt` contract on Base. The interface is a `rich` terminal application; two side-by-side terminals make process separation self-evident on video.

## Architectural Decision Process

Architectural changes must be recorded in `DECISIONS.md`. Codex must not silently change architecture because another implementation is easier. Material assumptions must be explicit before implementation proceeds.

## Open Questions

- `VERIFY-AT-BUILD`: `sibyl-memory-client` 0.8.0 exact signatures for `write_event`, `read_events`, `search_entities`, and tenant selection. The published README documents the v0.4.x surface. One documented fallback exists for the authority-event storage call; see `PREREQ-003` section 3.
- `ORG-Q1`: Base mainnet versus Base Sepolia for the partner multiplier.
- RESOLVED `ORG-Q2`: the repository is licensed MIT (`DECISION-024`).
