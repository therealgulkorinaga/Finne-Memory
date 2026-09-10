# Finné Memory

**Finné Memory converts an autonomous agent's remembered operating history into bounded authority for its next action.**

> Sibyl lets agents remember. Finné determines what that memory authorizes them to do next.

Jump to: [memory read/write locations](#where-sibyl-memory-is-load-bearing) · [setup and run](#setup-and-run) · [prior work](#prior-work) · [builders](#builders-and-ai-tools)

## What It Does

An agent with a 25,000 USDC ceiling and no memory of its own history will propose 25,000 USDC on its first day and on its hundredth. Mechanical permissions — spending limits, approved assets, approved contracts, permitted time windows — say what an agent is *technically allowed* to do. They say nothing about what it has *earned*: what happened last time, under what circumstances it was approved, what scope was considered safe, whether the outcome held up, and what is materially different now.

An autonomous agent (`finne/agent.py`, a model) is shown an opportunity and the capital it has available — never its ceiling, never any precedent — and proposes what it wants to do. Finné Memory sits between that agent and its ceiling. It turns persisted experiences into structured precedents and derives a narrower, explainable authority from them:

```
eligible = cases that are materially comparable
           AND authority_state == "active"
           AND outcome == "success"

learned_max_amount = max(authorized_amount of eligible)  if eligible is non-empty
                   = cold_start_autonomous_amount        if eligible is empty
```

The authorized amount is the strict intersection of five constraints — owner ceiling, current hard policy, active precedent constraints, learned constraint, and current action scope. It can only narrow. No model participates at runtime; every value is deterministic.

Finné Memory is **not** generic agent memory. Sibyl Memory provides the persistent memory. Finné Memory operates above it and converts remembered operating history into bounded, auditable authority.

## Status

Implemented and merged. The two-session demonstration runs end to end against Base Sepolia.

| | |
| --- | --- |
| Build | All five `SPEC-001` seams merged (PRs #7–#11) |
| Tests | **229 passed, 4 skipped** — the 4 are live-Base tests, opt-in via `FINNE_LIVE_BASE_TEST=1` |
| Contract | [`0xcC012ce78162bDA47B630C205B5f4Fa675Be9f46`](https://sepolia.basescan.org/address/0xcC012ce78162bDA47B630C205B5f4Fa675Be9f46) on Base Sepolia (chain `84532`). Its `DV-001-V1` and `DV-002-V1` receipts are already recorded from earlier rehearsals, so a fresh run needs `deploy_contract.py --force` — see [Run the full demonstration](#run-the-full-demonstration) |
| Deletion gate | Automated — `tests/test_fresh_session.py::test_no_memory_control_escalates_and_cannot_execute` |
| Open | `ORG-Q1` (Sepolia vs mainnet for the partner multiplier); four test-catalogue questions in `docs/testing/TEST-CATALOGUE.md` |

## The Demonstration

Two genuinely separate OS processes.

**Session 1.** Owner ceiling is 25,000 USDC on Base. The agent proposes 25,000. No comparable precedent exists, so `learned_max_amount` falls back to `cold_start_autonomous_amount` of `0.00` and Finné Memory escalates rather than silently authorizing the full amount. The owner approves a constrained authority of 10,000 USDC. The agent executes a zero-value Base action recording that authorization. The complete case — proposal, facts, ceiling, constrained authority, decision, action, transaction reference, outcome, precedent status — is written into Sibyl Memory. **The process exits.**

**Session 2.** A fresh process. Same 25,000 ceiling, a materially similar opportunity, no carried-over state. The agent proposes the broader action. Finné Memory retrieves the earlier case from Sibyl Memory, confirms it is materially comparable and still `active`, and derives learned authority of 10,000 USDC.

**25,000 USDC proposed → 10,000 USDC authorized**, attributable on screen to the precedent it recalled.

**Control.** Empty the memory and Session 2 retrieves nothing, derives zero autonomous authority, and escalates. It cannot proceed.

The corpus deliberately contains four comparable cases authorized **above** 10,000 — withdrawn at 20,000, superseded at 15,000, questioned-with-failed-outcome at 12,000, and never-activated draft at 18,000. If authority-state filtering breaks, the derived maximum rises above 10,000 and the demo fails loudly instead of passing quietly.

## Where Sibyl Memory Is Load-Bearing

Every critical-path read and write, with the exact call and the module that makes it. All memory access is confined to [`finne/memory/client.py`](finne/memory/client.py) — no other module imports `sibyl_memory_client`, enforced by `tests/test_import_boundaries.py`.

| # | Operation | Call | Mode | When |
| --- | --- | --- | --- | --- |
| W1 | Immutable case version | `set_entity("finne_case_version", "<id>", {...})` | Write-once | Session 1, after the owner constrains authority |
| W2 | Owner-policy snapshot in force | `set_reference("owner_policy_snapshot/<id>", {...})` | Write-once | Session 1, with W1 |
| W3 | Authority event (`draft` → `active` → …) | `write_event(extra={...})` | Append-only | On owner confirmation and every later treatment |
| W4 | Execution outcome and Base transaction reference | `set_entity("finne_outcome", "<id>", {...})` | Write-once | After the Base transaction settles |
| W5 | In-flight proposal working state | `set_state("current_proposal", {...})` | Overwritable | During a session; **never** read across sessions |
| **R1** | **Candidate precedent generation** | `search_entities(<query>, category="finne_case_version")` | Read | Session 2, before any authorization |
| **R2** | **Exact case retrieval** | `get_entity("finne_case_version", "<id>")` | Read | Session 2, for every candidate |
| **R3** | **Authority-state fold** | `search(<id>, tiers=("journal",))` over authority events | Read | Session 2, to derive current authority state |
| **R4** | **Outcome lookup for derivation eligibility** | `get_entity("finne_outcome", "<id>")` | Read | Session 2, during derivation |
| R5 | Audit display of the policy in force | `get_reference("owner_policy_snapshot/<id>")` | Read | Session 2, for the explanation |

**R1–R4 are the load-bearing reads.** Remove any one of them and Session 2 assembles no usable candidate, derives `learned_max_amount = 0`, and must escalate. It cannot execute autonomously.

**W1, W3, and W4 are the load-bearing writes.** Remove them and Session 1 produces nothing for Session 2 to find.

This is not a stored preference or a cache. The learned number does not exist anywhere else and cannot be recomputed without these reads.

## Memory Implementation Note

**What the agent persists.** An immutable case version per decision (facts, authorized amount), the owner-policy snapshot in force at decision time, an append-only journal of authority transitions, and the execution outcome with its Base transaction hash.

**What it recalls.** In a fresh process with no carried-over state: candidate prior cases matching network, asset and action class; each candidate's exact record; each candidate's current authority state, folded from its journal; and each candidate's recorded outcome.

**What it uses to decide.** A candidate becomes eligible only if it is materially comparable (same network, asset, action class, target class and function, and the current proposal is no riskier than the precedent), its folded authority state is `active`, and its recorded outcome is `success`. The learned ceiling is the maximum authorized amount across eligible candidates. That ceiling enters a five-way intersection that can only narrow, and the resulting decision names the precedent it relied on.

Two encoding decisions make the `PREREQ-002` object model work on an overwritable key-value store:

- **Immutability is enforced above the store.** `set_entity` silently overwrites by default; `finne/memory/client.py` refuses to overwrite an existing case version or outcome and raises instead. Correction creates a new version identifier, never a mutation.
- **Current authority state is derived, never stored.** It is folded from the append-only journal on every read, enforcing both the transition matrix and cross-event chain consistency. A contradictory chain yields no authority at all rather than its last good value.

Withdrawn and superseded cases stay retrievable and displayable while being ineligible to authorize, so `archive_entity` is deliberately never called.

## The Agent, And What It Is Not Allowed To Do

`finne/agent.py` is the only module that calls a model. It is given an opportunity and its available capital, and it decides two things: how much to commit, and how it rates the counterparty. It returns a `Proposal` and nothing else.

It is never given the owner ceiling, any precedent, or any authority value — and it cannot go looking. The module has no import path to `finne/authority/`, `finne/memory/`, `finne/policy.py`, or `finne/base/`, enforced over the transitive closure by `tests/test_import_boundaries.py`. That boundary is what makes the demonstration honest: the bound comes from Finné Memory, not from the agent's restraint.

| Concern | Decided by |
| --- | --- |
| What is proposed | **The model** |
| Whether it is comparable to precedent | Deterministic |
| What authority has been earned | Deterministic |
| What is authorized | Deterministic |
| What is signed and submitted | Deterministic |
| What is explained | Deterministic |

Model output is untrusted input. It is parsed into a `Proposal`, whose validation rejects anything malformed, and the engine then bounds whatever survives. If the agent proposes 40,000 against a 25,000 ceiling it is blocked — that is the product working, not an error path, and `tests/test_agent.py` asserts it. There is deliberately no fallback to a fixed proposal on model failure: a silent fallback would make the demo appear to work while proving nothing.

Specified by `docs/specs/SPEC-002_MODEL_PROPOSING_AGENT.md`, recorded as `DECISION-027`.

## Setup And Run

Requires Python 3.11+ and a Base Sepolia wallet holding testnet gas only.

```bash
git clone https://github.com/therealgulkorinaga/Finne-Memory.git
cd Finne-Memory
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Configure the Base credentials:

```bash
cp .env.example .env
# Set FINNE_BASE_PRIVATE_KEY (throwaway Sepolia wallet, testnet gas only).
# BASE_RPC_URL defaults to https://sepolia.base.org and needs no signup.
```

### Verify without a wallet

The test suite needs no key and touches no network. It includes the memory-deletion gate and the cross-session behaviour, both run as real subprocesses:

```bash
.venv/bin/python -m pytest
# 229 passed, 4 skipped
```

### Run the full demonstration

This needs a funded Sepolia wallet, because **the headline result depends on a real Base transaction**. `finne/authority/derivation.py` requires `outcome == "success"` for a precedent to be eligible, and the outcome only exists once a transaction settles. Both prerequisites below are mandatory, not optional:

1. **Deploy a fresh contract.** `recorded[decisionId]` is permanent and global, and the committed deployment has already consumed `DV-001-V1` and `DV-002-V1` from earlier rehearsals. Reusing it makes Session 1 correctly refuse a duplicate, write no outcome, and leave Session 2 with nothing to find.
2. **Use a new database file.** Sibyl Memory exposes no delete for the reference or journal tiers — both write-once and append-only by design — so a decision version that already exists cannot be reset in place. `scripts/reset_demo.py` detects this and refuses with an actionable message rather than failing later.

```bash
DB=~/.sibyl-memory/demo-$(date +%H%M%S).db

.venv/bin/python scripts/deploy_contract.py --force     # required: frees DV-001-V1 / DV-002-V1
.venv/bin/python scripts/reset_demo.py --db-path $DB    # seeds CASE-003..008; CASE-001 is not seeded

.venv/bin/python scripts/session1.py --db-path $DB              # escalates; owner approves 10,000
.venv/bin/python scripts/session2.py --db-path $DB              # constrains 25,000 -> 10,000
.venv/bin/python scripts/session2.py --db-path $DB --no-memory  # the control: escalates, cannot act
```

Add `--agent=model` to either session to have the proposal produced by a real agent rather than a fixed value. It needs `OPENROUTER_API_KEY`; the default `--agent=fixed`, the test suite, and the deletion gate all run without one.

`--no-memory` points at a fresh, never-seeded tenant, so it reproduces the deletion test without destroying Session 1's case.

### Environment flags

| Flag | Effect |
| --- | --- |
| `FINNE_BASE_DRY_RUN=1` | Skips every network call. **Session 2 will escalate rather than constrain** — with no Base attempt there is no recorded outcome, so `DV-001-V1` is correctly ineligible as precedent. This is the specified behaviour, not a failure; `tests/test_fresh_session.py::test_session2_honestly_escalates_when_precedent_has_no_recorded_outcome` asserts it. Use it to exercise orchestration, not to see the headline result |
| `FINNE_PLAIN_OUTPUT=1` | Unstyled text, fixed width, for piping or capture |
| `FINNE_LIVE_BASE_TEST=1` | Enables the 4 opt-in live-Base tests, which deploy a fresh contract and spend testnet gas |
| `OPENROUTER_API_KEY` | Required only for `--agent=model`. Read solely inside `finne/agent.py`; never logged, never persisted, never written to Sibyl Memory |
| `FINNE_AGENT_MODEL` | Optional OpenRouter model slug for the agent. Defaults to `anthropic/claude-opus-5` |

## Partner Stacks Used

| Stack | Use | Evidence |
| --- | --- | --- |
| **Sibyl Memory** (`sibyl-memory-client` 0.8.0) | Mandatory persistent substrate. Entity, reference, journal and state tiers. Local SQLite with FTS5 under `~/.sibyl-memory/` | `finne/memory/client.py`, `finne/memory/schema.py` |
| **Base** (Sepolia, chain `84532`) | Execution and outcome evidence. `AuthorizationReceipt` contract deployed and called with a real onchain transaction per authorization | `finne/base/adapter.py`, `finne/base/contracts/AuthorizationReceipt.sol`, contract [`0xcC01…9f46`](https://sepolia.basescan.org/address/0xcC012ce78162bDA47B630C205B5f4Fa675Be9f46) |

Virtuals Protocol is not used.

`ORG-Q1` is unresolved with the organiser: the published rules require deployment plus an executed onchain action but do not name a network. The build targets Base Sepolia and the network is a single configuration value.

## How Base Performs Genuine Work

Finné derives the permitted action → the agent executes it on Base → the transaction result becomes outcome evidence → the outcome is written into Sibyl Memory → a future fresh session recalls and uses it.

The `AuthorizationReceipt` contract records the authorized policy amount and a keccak hash of the material facts and cited precedents, keyed by `keccak256(decision_version_id)`. Every demonstration transaction carries **zero value** — representing a 10,000 USDC authorization does not require moving 10,000 USDC — and the function is non-payable, so the contract enforces that itself.

The outcome is what closes the loop: `finne/authority/derivation.py` requires `outcome == "success"` for eligibility, so a case with no recorded Base result cannot authorize anything in a later session. Duplicate execution is rejected at both the application level and by the contract's own `require(!recorded[decisionId])`, and an `authorizedSigner` restriction prevents a third party recording a competing entry for a predictable decision id.

## Boundaries

Finné Memory is not a payment, escrow, x402, refund, settlement, transaction-dispute, or service-delivery verification product. Base is used here for authorized execution and outcome evidence only.

## Prior Work

**No external code was reused.** Every line under `finne/`, `scripts/`, and `tests/` was written for this project during the event window, in a public repository with genuine commit history from 2026-09-02.

| Category | Declaration |
| --- | --- |
| External code, templates, assets | None |
| Datasets | None. The demo corpus in `docs/product/ACTIVE_DEMO_DESIGN.md` is entirely synthetic and authored for this project |
| Dependencies | `sibyl-memory-client` (MIT), `web3` (MIT), `py-solc-x` (MIT), `rich` (MIT); dev-only `pytest` (MIT) and `hypothesis` (MPL-2.0, not distributed). All used as published, unmodified |
| Prior work by this builder | The `PREREQ-002` decision-record and precedent object model — matter and decision versions, authority states and transitions, citation rules, and invariants — was designed earlier in this repository for a supplier-onboarding domain and is carried forward unchanged. Its supplier instantiation is retained as historical under `docs/product/PREREQ-001_*` and `PREREQ-002_*` |
| Third-party content | Short factual requirements and API names from `hack.sibyllabs.org`, `docs.sibyllabs.org`, and the PyPI JSON API, cited with verification dates in `HACKATHON_RULES.md` |

Full record, including licences and per-change provenance: [`REUSED_COMPONENTS.md`](REUSED_COMPONENTS.md).

## Builders And AI Tools

Built by **Arko Ganguli** ([@therealgulkorinaga](https://github.com/therealgulkorinaga)), solo.

Two AI tools were used and are disclosed here voluntarily; no event rule requires it.

- **Claude Code (Anthropic)** — implementation, drafting, and planning.
- **Codex (OpenAI)** — independent second-pass review of every bounded change, per `AGENT_BUILD_INSTRUCTIONS.md` section 11. Review prompts and outcomes are preserved under [`prompts/`](prompts/).

Every substantive decision, approval, and merge was made by Arko. The complete record of what each tool did is in [`AI_USAGE.md`](AI_USAGE.md), with human decisions in [`HUMAN_DECISIONS.md`](HUMAN_DECISIONS.md) and per-change history in [`BUILD_LOG.md`](BUILD_LOG.md). Individual commits carry `Co-Authored-By` trailers naming the tools that worked on them.

## Naming

| Name | Meaning |
| --- | --- |
| Sibyl Labs | Hackathon organiser |
| Sibyl Memory | The organiser's mandatory persistent-memory infrastructure |
| Finné | Umbrella venture |
| Finné Memory | This product |
| `Finne-Memory` | GitHub repository |
| `finne-memory` | Technical slug |

The product was renamed from Sybill to Finné Memory under `DECISION-021`. Historical references retain the former name and the former event spelling; they are preserved unrewritten as truthful contemporaneous record.

## Documentation

**Current-facing**

- `PRD.md` — product requirements
- `ARCHITECTURE.md` — architecture summary and constraint register
- `docs/architecture/PREREQ-003_ARCHITECTURE.md` — the full architecture decision
- `docs/product/ACTIVE_DEMO_DESIGN.md` — active demo corpus, fixtures, and negative cases
- `docs/specs/SPEC-001_FRESH_SESSION_LEARNED_AUTHORITY_SLICE.md` — approved first specification
- `docs/testing/TEST-CATALOGUE.md` — test-case specification, findings, and open questions
- `HACKATHON_RULES.md` — verified official event rules and open organiser questions
- `TASKS.md` — task registry and build sequence
- `DECISIONS.md` — chronological product, architecture, and process decisions

**Governance**

- `AGENTS.md` — standing operating manual for agents
- `AGENT_BUILD_INSTRUCTIONS.md` — roles, ownership, handoffs, reviews, escalation
- `AI_BUILD_GOVERNANCE.md` — mandatory AI-build lifecycle and control gates
- `CONTRIBUTING.md` — collaboration workflow

**Audit**

- `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, `REUSED_COMPONENTS.md`, `prompts/`

**Historical**

- `docs/product/PREREQ-001_*` and `docs/product/PREREQ-002_*` — the supplier-onboarding design, superseded as a domain by `DECISION-022`. The `PREREQ-002` object model, authority semantics, and invariants carry forward unchanged and remain authoritative.

## Licence

MIT. See [`LICENSE`](LICENSE). Chosen under `DECISION-024` and consistent with `sibyl-memory-client`, which is also MIT.
