# Finné Memory

**Finné Memory catches inconsistent institutional decisions before customers do.**

> Policy defines the rule. Precedent captures how the institution has actually interpreted it. Finné checks both before a decision leaves the building.

Jump to: [memory read/write locations](#where-sibyl-memory-is-load-bearing) · [setup and run](#setup-and-run) · [prior work](#prior-work) · [builders](#builders-and-ai-tools)

## What It Does

Disputes rarely start with a bad decision. They start with an **inconsistent** one — two similar cases treated differently, a decision resting on superseded policy, an exception applied unevenly, or an institution that cannot reconstruct why it decided what it did.

Finné Memory sits in front of an externally consequential decision and asks one question: *is this consistent with current policy and with this institution's own valid precedent?*

The demonstration domain is insurance claims. A handler has delegated authority to settle up to £25,000. An assessing agent (`finne/agent.py`, a model) is shown a claim and the loss adjuster's figure — never its own limits — and proposes a settlement. Finné then retrieves how the institution has actually decided materially similar claims, and derives what it has *earned* the authority to do:

```
eligible = prior decisions that are materially comparable
           AND authority_state == "active"     (still stands as precedent)
           AND outcome == "success"            (settled and not reversed)

learned_max = max(settled amount of eligible)  if any
            = cold_start (0.00)                if none
```

"Materially comparable" is a strict, deterministic rule — same channel, currency, assessment type, peril and decision, and the current claim can't be *riskier* than the precedent. **No model participates in that judgement anywhere.** The authorized figure is the strict intersection of five constraints and can only ever narrow.

The point is not to force consistency blindly. It is to force **explainable** consistency: when a decision departs from precedent, the departure is surfaced, attributed, and recorded before the letter goes out.

## Status

Implemented and merged. The two-session demonstration runs end to end against Base Sepolia.

| | |
| --- | --- |
| Build | All five `SPEC-001` seams merged (PRs #7–#11), plus the assessing agent (`SPEC-002`) |
| Tests | **229 passed, 4 skipped** — the 4 are live-Base tests, opt-in via `FINNE_LIVE_BASE_TEST=1` |
| Contract | [`0x27ccbF8DFD42c27bD501f513E7470171CAF1b9d4`](https://sepolia.basescan.org/address/0x27ccbF8DFD42c27bD501f513E7470171CAF1b9d4) on Base Sepolia (chain `84532`). Carries the real `DV-001-V1` and `DV-002-V1` receipts from the recorded run — verifiable on BaseScan, both `10,000.00`, both zero value. Because `recorded[decisionId]` is permanent, re-running the demonstration needs `deploy_contract.py --force` first — see [Run the full demonstration](#run-the-full-demonstration) |
| Deletion gate | Automated — `tests/test_fresh_session.py::test_no_memory_control_escalates_and_cannot_execute` |
| Domain | Insurance claims (`DECISION-028`). The engine is domain-agnostic and has now carried two instantiations |
| Open | `ORG-Q1` (Sepolia vs mainnet for the partner multiplier); four test-catalogue questions in `docs/testing/TEST-CATALOGUE.md` |

## The Demonstration

Two genuinely separate OS processes.

**Session 1 — a first-of-its-kind claim.** Delegated authority is £25,000. A burst pipe claim comes in; the adjuster values the reinstatement at £25,000 and the agent proposes settling in full. Finné finds no comparable, active, upheld precedent, so `learned_max_amount` falls back to `cold_start_autonomous_amount` of `0.00` and the decision **escalates to a human** rather than settling at the delegated ceiling. A senior handler approves £10,000. That decision — facts, evidence, policy version in force, the approval, the outcome — is written into Sibyl Memory and anchored on Base. **The process exits.**

**Session 2 — a materially similar claim.** A fresh process, no carried-over state. Same authority, same claim profile, adjuster again at £25,000, agent again proposes £25,000. This time Finné retrieves the institution's own history and derives **£10,000**, naming `DV-001-V1` as the decision it is consistent with.

**25,000 GBP proposed → 10,000 GBP authorized**, attributable on screen to the precedent recalled. The handler may settle up to £10,000 on their own authority; going beyond it isn't forbidden, it requires sign-off — and the precedent being departed from is named.

**Control.** Empty the memory and Session 2 retrieves nothing, derives zero, and escalates. It cannot proceed.

### Why the corpus is the real test

Six other prior decisions are retrieved and displayed. Every one is excluded, and each for a different reason:

| Prior decision | Settled | Why it cannot authorise |
| --- | --- | --- |
| `DV-003-V1` | £20,000 | **Overturned by the ombudsman** on appeal |
| `DV-006-V1` | £15,000 | Decided under **policy wording v2**, since replaced by v4 |
| `DV-007-V1` | £12,000 | Settlement **reversed**, now under complaint |
| `DV-008-V1` | £18,000 | Recorded but **never signed off** |
| `DV-004-V1` | £5,000 | Storm damage — a **different peril** |
| `DV-005-V1` | £10,000 | **Gradual** leakage, not sudden — excluded by the wording |

Four carry amounts **above** £10,000. If authority filtering broke, the derived figure would rise and the demo would fail loudly instead of passing quietly.

`DV-005-V1` is the one worth pausing on. The wording covers *sudden and accidental* escape of water and excludes gradual leakage. That decision is active, upheld, and superficially identical — and still cannot be followed. A handler classifying on surface similarity is exactly what produces a complaint, an ombudsman referral, and a remediation bill.

## Where Sibyl Memory Is Load-Bearing

Every critical-path read and write, with the exact call and the module that makes it. All memory access is confined to [`finne/memory/client.py`](finne/memory/client.py) — no other module imports `sibyl_memory_client`, enforced by `tests/test_import_boundaries.py`.

| # | Operation | Call | Mode | When |
| --- | --- | --- | --- | --- |
| W1 | Immutable decision record | `set_entity("finne_case_version", "<id>", {...})` | Write-once | Session 1, after the senior handler approves |
| W2 | Delegated-authority policy in force | `set_reference("owner_policy_snapshot/<id>", {...})` | Write-once | Session 1, with W1 |
| W3 | Authority event (`draft` → `active` → …) | `write_event(extra={...})` | Append-only | On owner confirmation and every later treatment |
| W4 | Outcome and the onchain anchor reference | `set_entity("finne_outcome", "<id>", {...})` | Write-once | After the Base transaction settles |
| W5 | In-flight assessment working state | `set_state("current_proposal", {...})` | Overwritable | During a session; **never** read across sessions |
| **R1** | **Candidate prior-decision generation** | `search_entities(<query>, category="finne_case_version")` | Read | Session 2, before any decision |
| **R2** | **Exact decision-record retrieval** | `get_entity("finne_case_version", "<id>")` | Read | Session 2, for every candidate |
| **R3** | **Authority-state fold** | `search(<id>, tiers=("journal",))` over authority events | Read | Session 2, to derive current authority state |
| **R4** | **Outcome lookup for derivation eligibility** | `get_entity("finne_outcome", "<id>")` | Read | Session 2, during derivation |
| R5 | Audit display of the policy version in force | `get_reference("owner_policy_snapshot/<id>")` | Read | Session 2, for the explanation |

**R1–R4 are the load-bearing reads.** Remove any one of them and Session 2 assembles no usable prior decision, derives `learned_max_amount = 0`, and must escalate. It cannot decide autonomously.

**W1, W3, and W4 are the load-bearing writes.** Remove them and Session 1 leaves no institutional record for Session 2 to be consistent with.

This is not a stored preference or a cache. The institution's earned position does not exist anywhere else and cannot be recomputed without these reads.

## Memory Implementation Note

**What the institution persists.** An immutable decision record per claim (the material facts, the amount settled), the delegated-authority policy in force at the time, an append-only journal of what happened to that decision afterwards, and the outcome with its onchain anchor.

**What it recalls.** In a fresh process with no carried-over state: candidate prior decisions matching channel, currency and assessment type; each one's exact record; each one's current authority state, folded from its journal; and whether the settlement was upheld or reversed.

**What it uses to decide.** A prior decision becomes usable only if it is materially comparable (same channel, currency, assessment type, peril and decision, and the current claim is no riskier), its folded state is `active`, and its outcome is `success`. The learned ceiling is the largest amount across those. That enters a five-way intersection that can only narrow, and the resulting decision names what it relied on.

**The authority lifecycle is the institution's, not an abstraction:**

| State | Means |
| --- | --- |
| `active` | Stands as precedent |
| `questioned` | Under complaint or appeal |
| `superseded` | Decided under policy wording since replaced |
| `withdrawn` | Overturned |

Two encoding decisions make this work on an overwritable key-value store:

- **Immutability is enforced above the store.** `set_entity` silently overwrites by default; `finne/memory/client.py` refuses to overwrite an existing decision record or outcome and raises instead. A correction creates a new version, never a mutation. That is the property a dispute turns on — you cannot quietly rewrite what you decided once a complaint arrives.
- **Current authority state is derived, never stored.** It is folded from the append-only journal on every read, enforcing both the transition matrix and cross-event consistency. A contradictory chain yields no authority at all rather than its last good value.

Overturned and superseded decisions stay retrievable while being ineligible to authorise, so `archive_entity` is deliberately never called. An insurer needs to see the decision that was overturned; it just must not lean on it.

## The Agent, And What It Is Not Allowed To Do

`finne/agent.py` is the only module that calls a model. It is shown a claim and the loss adjuster's assessed value, and decides two things: the settlement figure to propose, and how it rates the claim's risk. It returns a proposal and nothing else.

**It is never shown the delegated ceiling, any prior decision, or any authority value — and it cannot go looking.** The module has no import path to `finne/authority/`, `finne/memory/`, `finne/policy.py`, or `finne/base/`, enforced over the transitive closure by `tests/test_import_boundaries.py`. That boundary is what makes the demonstration honest: the bound comes from the institution's own record, not from the agent's restraint.

| Concern | Decided by |
| --- | --- |
| What settlement is proposed | **The model** |
| Whether it is comparable to precedent | Deterministic |
| What authority has been earned | Deterministic |
| What is authorised | Deterministic |
| What is anchored onchain | Deterministic |
| What is explained | Deterministic |

Model output is untrusted input. It is parsed into a `Proposal`, whose validation rejects anything malformed, and the engine bounds whatever survives. If the agent proposes £40,000 against a £25,000 delegated ceiling it is blocked — that is the product working, and `tests/test_agent.py` asserts it. There is deliberately no fallback to a fixed proposal on model failure: a silent fallback would make the demo appear to work while proving nothing.

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
.venv/bin/python scripts/reset_demo.py --db-path $DB    # seeds the six prior decisions; CASE-001 is created live

.venv/bin/python scripts/session1.py --db-path $DB              # escalates; senior handler approves 10,000
.venv/bin/python scripts/session2.py --db-path $DB              # constrains 25,000 -> 10,000, citing DV-001-V1
.venv/bin/python scripts/session2.py --db-path $DB --no-memory  # the control: escalates, cannot act
```

Add `--agent=model` to either session to have the settlement proposed by a real assessing agent rather than a fixed value. It needs `OPENROUTER_API_KEY`; the default `--agent=fixed`, the test suite, and the deletion gate all run without one.

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
| **Base** (Sepolia, chain `84532`) | Tamper-evident attestation. `AuthorizationReceipt` deployed and called with a real onchain transaction per confirmed decision, anchoring the authorised amount and a hash of the facts and precedents relied on | `finne/base/adapter.py`, `finne/base/contracts/AuthorizationReceipt.sol`, contract [`0x27cc…b9d4`](https://sepolia.basescan.org/address/0x27ccbF8DFD42c27bD501f513E7470171CAF1b9d4) |

Virtuals Protocol is not used.

`ORG-Q1` is unresolved with the organiser: the published rules require deployment plus an executed onchain action but do not name a network. The build targets Base Sepolia and the network is a single configuration value.

## How Base Performs Genuine Work

Base is a **tamper-evident attestation layer**, not a payment rail. No confidential claim file goes onchain and no money moves.

When a decision is confirmed, the `AuthorizationReceipt` contract records the authorised amount as a policy value and a keccak hash of the material facts and the precedents relied upon, keyed by `keccak256(decision_version_id)`. Every transaction carries **zero value** and the function is non-payable, so the contract enforces that itself.

The question this answers is the ugly one that surfaces six months later, after a complaint:

> *Was this really the policy and the reasoning at the time, or was the record reconstructed after the fact?*

**Sibyl Memory remembers the decision. Base proves the record wasn't rewritten.**

The outcome closes the loop: `finne/authority/derivation.py` requires `outcome == "success"`, so a decision with no recorded, anchored result cannot be leaned on in a later session. Duplicate anchoring is rejected at both the application level and by the contract's own `require(!recorded[decisionId])`, and an `authorizedSigner` restriction prevents a third party recording a competing entry for a predictable decision id.

## Boundaries

Finné Memory is a pre-decision consistency check. It is **not** a claims management system, a policy administration system, a dispute-resolution or adjudication engine, a payments or settlement rail, or generic agent memory. It does not decide claims; it tells an institution when it is about to decide one inconsistently with its own record.

The insurance corpus in this repository is **entirely synthetic** and authored for this demonstration. No real claim, policyholder, insurer, or claims data is represented, and none is claimed.

## Prior Work

**No external code was reused.** Every line under `finne/`, `scripts/`, and `tests/` was written for this project during the event window, in a public repository with genuine commit history from 2026-09-02.

| Category | Declaration |
| --- | --- |
| External code, templates, assets | None |
| Datasets | None. The insurance corpus in `docs/product/ACTIVE_DEMO_DESIGN.md` is entirely synthetic and authored for this project. No real claim, policyholder, insurer, or claims dataset is used or represented |
| Dependencies | `sibyl-memory-client` (MIT), `web3` (MIT), `py-solc-x` (MIT), `rich` (MIT); dev-only `pytest` (MIT) and `hypothesis` (MPL-2.0, not distributed). All used as published, unmodified |
| Prior work by this builder | The `PREREQ-002` decision-record and precedent object model — matter and decision versions, authority states and transitions, citation rules, and invariants — was designed earlier in this repository and is carried forward unchanged. It has now carried three domain instantiations: supplier onboarding, agent authority (`DECISION-022`), and insurance claims (`DECISION-028`). The earlier instantiations are retained as historical under `docs/product/PREREQ-001_*` and `PREREQ-002_*` |
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
