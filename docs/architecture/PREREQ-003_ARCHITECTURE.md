# PREREQ-003: Architecture

## Status

- CONFIRMED: This document closes `PREREQ-003` and is recorded as `DECISION-023`. Arko approved it on 2026-09-03; it is committed in `d82f224`. `SPEC-001` remains a separate approval gate.
- CONFIRMED: It decides every item required of `PREREQ-003`. Where a fact could not be verified without installing software, the verification step is named rather than guessed.
- CONFIRMED: Scope is the minimum credible architecture for the two-session learned-authority slice in `docs/product/ACTIVE_DEMO_DESIGN.md`. Nothing is designed for scale that the demo does not need.

## 0. Verified External Facts

Verified 2026-09-03 from `https://pypi.org/pypi/sibyl-memory-client/json` and `https://docs.sibyllabs.org/memory`.

| Fact | Value |
| --- | --- |
| Package | `sibyl-memory-client` |
| Version | `0.8.0` |
| Licence | MIT |
| Python | `>=3.10` |
| Import | `from sibyl_memory_client import MemoryClient` |
| Construction | `MemoryClient.local("~/.sibyl-memory/memory.db")` |
| Storage | SQLite under `~/.sibyl-memory/`, FTS5 full-text search, no embeddings, no vector index |
| Tiers | state, entities, journal, reference, archive |
| Published API | `set_state`/`get_state`, `set_entity(kind, name, body)`/`get_entity`, `write_event(...)`/`read_events(...)`, `set_reference(key, body)`/`get_reference`, `archive_entity(kind, name)`, `delete_entity(kind, name)`, `search_entities(query)` |
| Uniqueness | `UNIQUE (tenant_id, category, name)` |
| Tenancy | Every read and write scoped by `tenant_id` |
| Credentials | `sibyl init` browser sign-in writes `~/.sibyl-memory/credentials.json` for the CLI's cloud-tier features. **Not required** for this project: `MemoryClient.local()`'s core operations work with no credentials — confirmed empirically, see below. Free tier has a 5 MB local cap regardless. |

- **VERIFY-AT-BUILD — RESOLVED 2026-09-04 (seam (b)):** The published README documents the v0.4.x surface while the current release is v0.8.0. The exact signatures of `write_event`, `read_events`, `search_entities`, `get_reference`, and tenant selection were confirmed against the installed package by construction and exercise, not just `inspect.signature`. Full findings in `finne/memory/client.py`'s module docstring and section 3 below.

## 1. Agent Runtime

- **Decision:** Python 3.11, standard library plus a short dependency list, `venv` and `pip`, one installable package `finne`.
- **Why:** Sibyl Memory is a local-first Python SQLite library. A web stack would put a network hop between the agent and its own memory for no benefit and would make "genuinely fresh process" harder to demonstrate.
- **Rejected:** Node/TypeScript web stack (wrong language for the mandatory substrate); LangChain (no orchestration need that plain functions do not meet); microservices; any cloud runtime.

| Dependency | Purpose | Justification |
| --- | --- | --- |
| `sibyl-memory-client` | Mandatory memory substrate | Required by the event |
| `web3` | Base adapter | Signing and contract interaction |
| `py-solc-x` | One-time contract compile | Avoids adding a second toolchain (Foundry/Hardhat) |
| `rich` | Terminal interface | Makes the recall moment legible on video |
| `pytest`, `hypothesis` | Tests | `hypothesis` proves the ceiling invariant over generated inputs rather than a handful of examples |
| `anthropic` | Optional explanation only | Never imported on the deterministic path |

## 2. Sibyl Memory Integration Method

- **Decision:** Direct in-process use of `sibyl-memory-client` via `MemoryClient.local(...)`, wrapped by exactly one module, `finne/memory/client.py`.
- **Decision:** A dedicated `tenant_id` per demo run isolates fixtures from any other Sibyl Memory content on the machine.
- **Decision:** No MCP server, no Hermes plugin, no CLI shelling. The application is the memory caller.
- **Prohibited:** Supabase, PostgreSQL, pgvector, Pinecone, or any other database as the store of remembered agent experiences. There is no second store and no cache of case content outside Sibyl Memory.

## 3. Memory Read/Write Boundary

This table is the critical path. It is reproduced in the README to satisfy the organiser's two-minute findability requirement.

| # | Operation | Tier / call | Written or read | When |
| --- | --- | --- | --- | --- |
| W1 | Immutable case version | `set_entity("finne_case_version", "DV-001-V1", {...})` | Write-once | Session 1, after the owner constrains authority |
| W2 | Owner-policy snapshot in force at decision time | `set_reference("owner_policy_snapshot/DV-001-V1", {...})` | Write-once | Session 1, same transaction boundary as W1 |
| W3 | Authority event (`draft` → `active`, `questioned`, `superseded`, `withdrawn`) | `write_event(...)` | Append-only | On owner confirmation and every later treatment |
| W4 | Execution outcome, Base transaction reference, observed result | `write_event(...)` + `set_entity("finne_outcome", "<decision_version_id>", {...})` | Write-once | After the Base transaction settles |
| W5 | In-flight proposal working state | `set_state("current_proposal", {...})` | Overwritable | During a session; **never** read across sessions |
| R1 | **Candidate precedent generation** | `search_entities(<deterministic query>)` | Read | Session 2, before any authorization |
| R2 | **Exact case retrieval** | `get_entity("finne_case_version", "<id>")` | Read | Session 2, for every candidate |
| R3 | **Authority-state fold** | `client.search(decision_version_id, tiers=("journal",))` over `finne_authority_event` records | Read | Session 2, to derive current authority state |
| R4 | Outcome lookup for derivation eligibility | `get_entity("finne_outcome", "<id>")` | Read | Session 2, during derivation |
| R5 | Audit display of the policy in force | `get_reference("owner_policy_snapshot/<id>")` | Read | Session 2, for the explanation |

- **R1, R2, R3, and R4 are the load-bearing reads.** Remove them and Session 2 has no precedent, derives `learned_max_amount = 0`, and must escalate. It cannot execute autonomously.
- **W1, W3, and W4 are the load-bearing writes.** Remove them and Session 1 produces nothing for Session 2 to find.
- **Decision:** Immutability is enforced above an overwritable key-value store. `finne/memory/client.py` refuses to overwrite an existing `finne_case_version` or `finne_outcome` name; an attempted overwrite raises and is recorded as an integrity failure. Correction creates a new version identifier, never a mutation.
- **Decision:** Current authority state is **derived** by folding the append-only authority journal, never stored as a mutable field. This preserves `PREREQ-002` append-only semantics on a store that permits overwrite.
- **Decision:** `archive_entity` is **not** used for withdrawn or superseded cases. They must stay retrievable and displayable while being ineligible to authorize. Archiving them would break that requirement.
- **VERIFY-AT-BUILD result (confirmed 2026-09-04, seam (b); corrected 2026-09-04 after a second Codex review found the first version of this note overclaimed):** The `AE-<zero-padded-sequence>` fallback below was not needed — `client.search(query, tiers=("journal",))` does content-filter the journal tier via FTS5, unlike `read_events(limit=...)`, which is descending-order and unfilterable. However, `client.search()` is **not unbounded**: it was found to silently cap real results at `limit // 4` regardless of how many actually match (verified across limit=20/100/400/1000/100000 — the ratio held consistently), with no pagination parameter to retrieve more. `finne/memory/client.py`'s `_authority_events_for` requests a high limit (8000, giving an effective cap of 2000 real events per decision version — far beyond any realistic corpus for this project) and treats hitting that cap as a truncation signal, failing `fold_authority_state` safe to `None` rather than trusting a possibly-incomplete history. See `finne/memory/client.py`'s module docstring for the complete list of verified signature differences from the published README.

## 4. Structured Memory Format

- **Decision:** Every entity body is a JSON object with a `schema_version` field, serialised from a frozen Python dataclass in `finne/models.py` and validated on both write and read.
- **Decision:** Validation on read is mandatory. A record that fails validation is treated as **absent**, never as permission. This is what makes `NEG-06` safe.
- **Decision:** Identifiers follow `PREREQ-002`: stable `CASE-nnn`, immutable `MV-nnn-Vk` and `DV-nnn-Vk`. Exact references always use the immutable version identifier.
- **Decision:** Decimal amounts are stored as strings and handled as `decimal.Decimal`. Float arithmetic is prohibited anywhere in the authority path.

## 5. Owner-Policy Representation

- **Decision:** `config/owner_policy.toml`, version-controlled, human-readable, loaded read-only by `finne/policy.py`.
- **Decision:** The application has **no code path that writes this file.** The agent cannot rewrite its own authority policy; the filesystem permission model and the absence of a writer are both relied upon.
- **Decision:** The learned-constraint derivation policy (`LCP-001`) lives in the same file. Derivation rules are owner-controlled, not agent-controlled.
- **Decision:** A snapshot of the policy in force is written to the reference tier at decision time (W2), so an audit can reconstruct which ceiling applied without trusting the current file.

## 6. Deterministic Authority Engine

- **Decision:** `finne/authority/engine.py` is pure. No I/O, no clock reads, no network, no imports from `finne.memory` or `finne.base`. Inputs in, `AuthorizationDecision` out.

```
derive_effective_authority(
    proposal:      Proposal,
    owner_policy:  OwnerPolicy,
    hard_policy:   HardPolicy,
    candidates:    list[EvaluatedCandidate],
) -> AuthorizationDecision
```

- **Decision:** The result is the strict intersection of the five inputs — owner permission ceiling, current hard policy, active precedent constraints, learned constraint, and current action scope. Intersection is implemented as a fold that can only narrow.
- **Decision:** `AuthorizationDecision.result` is one of `allow`, `constrain`, `block`, `escalate`. It always carries `authorized_amount`, `binding_constraint` naming which of the five inputs bound the result, and `cited_precedents` listing the exact decision version identifiers relied upon.
- **Invariant, enforced by an assertion in code and by a property test:** `authorized_amount <= owner_policy.max_amount` for all inputs, including adversarial and malformed ones.
- **Invariant:** The engine cannot widen scope. It may never introduce a network, asset, contract, protocol, function, or action class absent from the owner ceiling.

## 7. Precedent Retrieval

- **Decision:** `finne/retrieval.py` builds a deterministic FTS5 query from the proposal's comparability facts and calls `search_entities`. No model participates in retrieval.
- **Decision:** Retrieval is a **candidate generator only.** Every candidate is then re-read exactly (R2), authority-folded (R3), and deterministically filtered. Rank order carries no weight in the result.
- **Safety property, stated because it is the reason ranking quality is not a correctness risk:** derivation takes the maximum authorized amount over *eligible* cases. A retrieval miss can therefore only lower the derived maximum. Retrieval error narrows authority; it can never widen it.
- **Decision:** Similarity is never conflated with authority. A candidate carries `is_comparable`, `authority_state`, and `outcome` as three independent fields, and all three are displayed.

## 8. Material-Difference Handling

- **Decision:** `finne/authority/comparability.py` implements the rule in `docs/product/ACTIVE_DEMO_DESIGN.md` section 3 as pure deterministic code: exact match on `network`, `asset`, `action_class`, `target_class`, and `function`, plus a directional check that the current `counterparty_risk_tier` is not worse than the precedent's.
- **Decision:** Any mismatch yields a structured `MaterialDifference` record naming the dimension, the precedent value, and the current value. The case is excluded from derivation and shown with its difference stated.
- **Decision:** A model may *explain* a material difference and may *propose* a `follows` or `distinguishes` treatment. Only deterministic validation plus an authorized confirmation path may persist or apply it. A model-proposed relationship that is not confirmed has no effect on authority.

## 9. Base Adapter

- **Decision:** `finne/base/adapter.py` using `web3.py`. It is the only module performing network I/O to Base and the only module aware of key material.
- **Decision:** Network, RPC URL, contract address, and chain ID come from configuration (`config/base_deployment.json` and `.env`). Switching Base Sepolia to Base mainnet is a configuration change, not a code change. This keeps `ORG-Q1` cheap to resolve either way.
- **Decision:** The adapter exposes two operations: `record_authorization(decision)` and `get_receipt(decision_id)`. It accepts an `AuthorizationDecision` and refuses to submit anything the decision did not authorize.
- **Decision:** Failure is explicit. Revert, timeout, and insufficient gas all produce a recorded `failure` outcome with no transaction reference fabricated and no success path taken (`NEG-07`).

## 10. Key And Signing Boundary

- **Decision:** The demo signing key is read from the environment variable `FINNE_BASE_PRIVATE_KEY` inside `finne/base/adapter.py` and nowhere else.
- **Decision:** The key is never passed to the authority engine, never written to Sibyl Memory, never written to any log or terminal output, and never committed. `.env` is already gitignored; `.env.example` carries the variable name and no value.
- **Decision:** The demo wallet holds only testnet gas. It is a purpose-made throwaway account with no other funds and no other role.
- **Decision:** Transactions are signed locally with `web3.eth.account.sign_transaction`. No custody service, no remote signer, no key derivation from anything stored in memory.
- **Decision:** A model may never sign, submit, or construct a transaction. `finne/explain.py` has no import path to `finne/base/`.

## 11. Safe Demo Contract And Action

- **Decision:** A purpose-built demonstration contract, `AuthorizationReceipt.sol`, records an authorization onchain. It moves no funds and holds no balance.

```solidity
function recordAuthorization(
    bytes32 decisionId,
    uint256 authorizedAmount,   // policy value, 6-decimal USDC units; NOT a transfer
    bytes32 factsHash           // hash of the material facts and cited precedents
) external;                     // non-payable; emits AuthorizationRecorded
```

- **Decision:** The authorized amount is carried as a **policy value**, not a transfer. Representing a 10,000 USDC authorization does not require moving 10,000 USDC. Every demonstration transaction carries zero value.
- **Decision:** `decisionId = keccak256(decision_version_id)`. The contract enforces `require(!recorded[decisionId])`, giving onchain duplicate-execution protection for `NEG-08` in addition to the application-level idempotency check.
- **Decision:** `factsHash` binds the receipt to the exact facts and precedents relied upon, so the onchain record is verifiable evidence rather than a bare log line.
- **Decision:** Compiled and deployed once by `scripts/deploy_contract.py` with `py-solc-x` and `web3.py`. The ABI and deployed address are checked into `config/base_deployment.json`. No Foundry or Hardhat toolchain is added.
- **Why this is genuine work:** the contract is the evidence layer. Session 1's transaction hash is written into Sibyl Memory as outcome evidence, and Session 2 reads that outcome as an eligibility input to derivation. Remove Base and the outcome evidence disappears from the derivation policy.

## 12. Fresh-Session Reset Procedure

- **Decision:** Sessions are separate OS processes. `scripts/session1.py` and `scripts/session2.py` are distinct entry points, and Session 1 exits fully before Session 2 starts. Termination is process exit, not a flag.
- **Decision:** `scripts/reset_demo.py` deletes the demo tenant's records via `delete_entity` and re-seeds `CASE-003` through `CASE-008` as pre-existing history.
- **Decision:** `CASE-001` is never seeded. Session 1 must create it live, so the Session 2 recall is genuine rather than staged.
- **Decision:** `scripts/session2.py --no-memory` points the client at an empty tenant to run the organiser's deletion test on camera.
- **Decision:** No module holds process-global mutable state that could survive within a session and mask a cross-session dependency. The fresh-session test enforces this by running both sessions as subprocesses and asserting only memory carries state.

## 13. Model-Optional Behaviour

- **Decision:** `finne/explain.py` is the only module permitted to call a model. Nothing else may import an AI SDK.
- **Decision:** If `ANTHROPIC_API_KEY` is absent, or the call fails, or the response fails schema validation, explanation falls back to a deterministic template. The authorization result is byte-identical either way.
- **Decision:** The model receives already-validated structured records and returns prose only. It cannot return a decision, an amount, an authority state, a citation, or a relationship that takes effect.
- **Decision:** The full test suite runs with no API key present in CI and locally. This is how "the deterministic system must work without a model API key" is proven rather than asserted.
- **Decision:** The recorded demo runs with no API key present.

## 14. Testing Approach

- **Decision:** `pytest`, with `hypothesis` for the ceiling invariant.

| Test file | Proves |
| --- | --- |
| `test_authority_invariants.py` | `authorized_amount <= owner ceiling` over generated inputs, including malformed and adversarial ones; intersection can only narrow |
| `test_authority_states.py` | Only `active` precedents support learned authority; `draft`, `questioned`, `superseded`, `withdrawn` are retrievable but never authorizing |
| `test_comparability.py` | Material-difference rules, including the directional risk-tier check |
| `test_memory_roundtrip.py` | Structured write and read against a real temporary Sibyl Memory database; overwrite of an immutable record raises |
| `test_fresh_session.py` | Session 1 and Session 2 run as **subprocesses**; Session 2 constrains 25,000 to 10,000; with the tenant emptied it escalates |
| `test_negative_cases.py` | `NEG-01` through `NEG-08` |
| `test_base_adapter.py` | Mocked revert, timeout, and duplicate submission produce no false success; one opt-in live test gated by `FINNE_LIVE_BASE_TEST=1` |

- **Decision:** `test_fresh_session.py` uses subprocesses rather than function calls. Anything less does not prove cross-session behaviour, and this is the project's central claim.
- **Decision:** The memory-deleted control is an automated test, not only a demo step. The organiser's gate test runs in CI.

## 15. Local Run Procedure

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
sibyl init                              # one-time browser sign-in; free tier
cp .env.example .env                    # add FINNE_BASE_PRIVATE_KEY and BASE_RPC_URL
python scripts/deploy_contract.py       # one-time; writes config/base_deployment.json
python scripts/reset_demo.py            # seed CASE-003..008
python scripts/session1.py              # establish 10,000 authority, execute, persist, exit
python scripts/session2.py              # fresh process: 25,000 proposed -> 10,000 authorized
python scripts/session2.py --no-memory  # deletion-test control
pytest                                  # run with no model API key set
```

## 16. Deployment And Demonstration Approach

- **Decision:** Nothing is hosted. The deliverable is a repository plus a recorded demo. The only deployed artifact is the Base contract.
- **Decision:** The interface is a `rich` terminal application, not a web app. Two side-by-side terminals make process separation self-evident on video, which a browser tab does not; and it removes a server, a frontend, and a build step from a ten-day window.
- **Decision:** The demo shows the Session 2 recall as one continuous unedited segment, as the rules require, with the Basescan transaction link visible.

## 17. Module Boundaries

| Module | Responsibility | Hard constraint |
| --- | --- | --- |
| `finne/models.py` | Frozen dataclasses, schema versions, validation | No I/O |
| `finne/policy.py` | Load owner policy and derivation policy | Read-only; no writer exists |
| `finne/memory/` | Sibyl Memory adapter, serialisation, immutability guard | **Only** module importing `sibyl_memory_client` |
| `finne/authority/` | Comparability, derivation, intersection engine | Pure; may not import `finne.memory` or `finne.base` |
| `finne/retrieval.py` | Deterministic candidate generation | May not rank by model output |
| `finne/base/` | Contract interaction and signing | **Only** module holding key material or reaching the network |
| `finne/explain.py` | Readable explanation | **Only** module permitted to call a model; no import path to `finne.base` |
| `finne/cli.py` | Terminal interface | Presentation only; no authority logic |

- **Decision:** These constraints are enforced by an import-boundary test, not only by convention.

## 18. Repository Layout

```
finne/
  __init__.py
  models.py
  policy.py
  retrieval.py
  explain.py
  cli.py
  memory/
    __init__.py
    client.py
    schema.py
  authority/
    __init__.py
    engine.py
    comparability.py
    derivation.py
  base/
    __init__.py
    adapter.py
    contracts/AuthorizationReceipt.sol
scripts/
  deploy_contract.py
  seed_demo.py
  reset_demo.py
  session1.py
  session2.py
tests/
  test_authority_invariants.py
  test_authority_states.py
  test_comparability.py
  test_memory_roundtrip.py
  test_fresh_session.py
  test_negative_cases.py
  test_base_adapter.py
  test_import_boundaries.py
config/
  owner_policy.toml
  base_deployment.json
.env.example
pyproject.toml
```

This layout replaces the `UNRESOLVED` logical ownership areas in `AGENT_BUILD_INSTRUCTIONS.md` section 3 with concrete, non-overlapping paths.

## 19. Failure Behaviour

Every failure resolves to a narrower authority. None widens.

| Failure | Behaviour |
| --- | --- |
| Sibyl Memory unavailable, uninitialised, or unauthenticated | `escalate`; stated on screen as a memory failure, never as an allow |
| Empty memory / cold start | `learned_max_amount = cold_start_autonomous_amount` = 0 → `escalate` |
| Record fails schema validation on read | Treated as **absent**, not as permission; logged as an integrity event |
| Contradictory authority events | Most restrictive interpretation wins; the conflict is surfaced |
| Only non-`active` precedents match | Displayed, excluded from derivation, result `escalate` |
| Material difference on every candidate | Cannot follow; result `escalate` with the difference named |
| Requested amount above owner ceiling | `block`, regardless of precedent |
| Model unavailable or malformed | Deterministic template; identical authorization result |
| Base revert, timeout, or gas failure | Outcome recorded as `failure`; no transaction reference fabricated; no success path |
| Duplicate execution | Application idempotency key plus contract-level `require` both reject it |
| Immutable-record overwrite attempted | Raises; recorded as an integrity failure; never silently accepted |

## 20. Open Items Carried Into SPEC-001

- RESOLVED `VERIFY-AT-BUILD`: `sibyl-memory-client` 0.8.0 signatures and tenant selection confirmed empirically during seam (b), 2026-09-04 — see section 3 above and `finne/memory/client.py`.
- `ORG-Q1`: Base mainnet versus Base Sepolia. Build targets Sepolia; the switch is one configuration value.
- RESOLVED `ORG-Q2`: the repository is licensed MIT (`DECISION-024`), matching `sibyl-memory-client`. `pyproject.toml` must declare `license = "MIT"` and every specified dependency is MIT except `hypothesis`, which is MPL-2.0 and dev-only, so it is not distributed.
