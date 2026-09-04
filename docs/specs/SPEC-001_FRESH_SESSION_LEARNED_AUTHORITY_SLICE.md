# SPEC-001: Fresh-Session Learned-Authority Vertical Slice

## 1. Spec ID And Approval Status

- Spec ID: `SPEC-001`
- Status: **APPROVED BY ARKO 2026-09-03 — NOT YET IMPLEMENTED**
- Governing decisions: `DECISION-022` (product, approved and committed), `DECISION-023` (architecture, approved and committed 2026-09-03), `DECISION-025` (two-tool operating model — Claude implements, Codex independently reviews with a two-pass cap, Arko approves/commits/pushes/merges — governs how this spec gets implemented)
- Governing contracts: `PRD.md`, `docs/product/ACTIVE_DEMO_DESIGN.md`, `docs/architecture/PREREQ-003_ARCHITECTURE.md`, retained `PREREQ-002` object model
- Authorization gate: SATISFIED. `DECISION-022`, `DECISION-023`, and this specification are all approved and committed. `TASK-001` may now be created per the gate in `TASKS.md`.

## 2. Goal And Actors

**Goal.** Prove that remembered operating history changes what an autonomous agent is permitted to do in a genuinely fresh session, and that the change is deterministic, bounded by owner authority, and auditable.

One sentence of observable outcome: *a fresh process proposes 25,000 USDC and is bound to 10,000 USDC by a precedent it retrieved from Sibyl Memory, and cannot do so when that memory is removed.*

| Actor | Capability in this slice |
| --- | --- |
| Owner | Defines the permission ceiling and derivation policy; approves constrained authority in Session 1; confirms a case to `active` |
| Autonomous treasury agent | Proposes an action; executes only within the authorized bound |
| Finné Memory | Retrieves precedent, derives learned constraint, emits the binding `AuthorizationDecision` |
| Sibyl Memory | Persists and recalls the case corpus across processes |
| Base | Records the authorization onchain and returns outcome evidence |
| Model | Optional prose explanation only; absent by default |

## 3. Inputs And Outputs

**Inputs**

- `config/owner_policy.toml` — owner ceiling `OP-001` and derivation policy `LCP-001`
- An action proposal with the eight material facts in `docs/product/ACTIVE_DEMO_DESIGN.md` section 2
- The Sibyl Memory tenant for the demo run
- `.env` — `FINNE_BASE_PRIVATE_KEY`, `BASE_RPC_URL`
- `config/base_deployment.json` — contract address, ABI, chain ID

**Outputs**

- An `AuthorizationDecision` — `result` in `allow` / `constrain` / `block` / `escalate`, plus `authorized_amount`, `binding_constraint`, `cited_precedents`, `material_differences`, and `explanation`
- A Base transaction reference, or a recorded failure
- New immutable records in Sibyl Memory: case version, outcome, authority events, owner-policy snapshot
- Terminal output making the recall moment legible on video

## 4. Behavior And State Changes

### Session 1 — establish experience

1. Load `OP-001`. Ceiling is 25,000 USDC on Base.
2. Agent proposes `CASE-001` at 25,000 USDC.
3. Retrieval finds no comparable `active` precedent. `learned_max_amount` falls back to `cold_start_autonomous_amount` = 0.
4. Intersection yields zero autonomous authority → `escalate`. **Not** a silent 25,000 allow.
5. Owner approves constrained authority of 10,000 USDC.
6. Base adapter calls `recordAuthorization` with the 10,000 policy value and the facts hash. Zero value moves.
7. Write W1 (case version), W2 (policy snapshot), W4 (outcome and transaction reference). This write is performed as the Owner, acting as Decision Reviewer, confirming creation of immutable draft `DV-001-V1` — per the retained `PREREQ-002` transitions, this confirmation **is** the initial `No prior state → draft` authority event, not a separate step.
8. The Owner, acting separately as Authority Steward, appends a second, distinct authority event W3: `draft` → `active`.
9. **Process exits.**

### Session 2 — memory changes behaviour

1. Fresh process. Load `OP-001`. No in-process state carried over.
2. Agent proposes `CASE-002` at 25,000 USDC.
3. R1 generates candidates; R2 reads each exactly; R3 folds authority state; R4 reads outcomes.
4. `CASE-001` is comparable, `active`, `success` → eligible. `CASE-003` (withdrawn), `CASE-006` (superseded), `CASE-007` (questioned), `CASE-008` (draft) are retrieved and displayed but excluded.
5. `learned_max_amount` = 10,000.
6. Intersection binds on the learned constraint → `constrain` to 10,000. `AuthorizationDecision.cited_precedents` names `DV-001-V1` — an explanation-level citation, not yet a persisted `PrecedentRelationship`, since `CASE-002` has no decision version until write-back.
7. Base action executes within the bound; outcome written back. The Owner, acting as Decision Reviewer, confirms creation of draft `DV-002-V1` (the initial authority event for `CASE-002`). The Owner then, acting separately as Authority Steward — a distinct timestamped confirmation from the step above — confirms the `follows` (`DV-002-V1` → `DV-001-V1`) and `distinguishes` (`DV-002-V1` → `DV-005-V1`) `PrecedentRelationship` records, each carrying required `fact_ids` and `citation_ids`. This persists the relationships without activating `DV-002-V1`, which remains `draft`; promoting it to `active` is out of scope for this slice.

### Control

`scripts/session2.py --no-memory` → nothing retrieved → `learned_max_amount` = 0 → `escalate`.

## 5. Business And Deterministic Rules

- Effective authority is the strict intersection of owner ceiling, hard policy, active precedent constraints, learned constraint, and current action scope. The fold can only narrow.
- Only `active` precedents enter derivation. `draft`, `questioned`, `superseded`, and `withdrawn` are retrievable and displayable but never authorizing.
- Comparability requires exact match on `network`, `asset`, `action_class`, `target_class`, `function`, plus a current `counterparty_risk_tier` no worse than the precedent's. Amount never affects comparability.
- `learned_max_amount` = max authorized amount over eligible cases, else `cold_start_autonomous_amount`.
- Immutable records are write-once. Correction creates a new version identifier.
- Current authority state is derived by folding the append-only journal, never stored mutably.

## 6. Permissions And Trust Boundaries

- Owner policy is read-only to the application. No code path writes it.
- The agent cannot rewrite its own authority policy or change an authority state.
- Only the owner confirmation path may promote a case to `active`.
- Only `finne/base/adapter.py` holds key material or reaches the network.
- Only `finne/explain.py` may call a model, and it has no import path to `finne/base/`.
- Model output is untrusted until schema-validated, and can never affect an authorization result.
- Records are validated on read; a malformed record is absent, not permission.

## 7. Interfaces Consumed And Exposed

**Consumed:** `sibyl_memory_client.MemoryClient` (entities, journal, reference, state, `search_entities`); `web3.py`; `AuthorizationReceipt` ABI; optional `anthropic`.

**Exposed:**

```
finne.policy.load_owner_policy(path) -> OwnerPolicy
finne.retrieval.find_candidates(proposal, memory) -> list[Candidate]
finne.authority.comparability.compare(proposal, case) -> Comparability
finne.authority.derivation.derive_learned_constraint(candidates, policy) -> LearnedConstraint
finne.authority.engine.derive_effective_authority(proposal, owner_policy, hard_policy, candidates) -> AuthorizationDecision
finne.memory.client.MemoryStore.{write_case_version, write_outcome, append_authority_event,
                                 read_case_version, fold_authority_state, search_cases}
finne.base.adapter.BaseAdapter.{record_authorization, get_receipt}
finne.explain.explain(decision) -> str
```

`VERIFY-AT-BUILD`: **RESOLVED 2026-09-04, seam (b).** `sibyl-memory-client` 0.8.0's real signatures were confirmed empirically (installed and exercised against a real local database, not just read from source) and differ from the published README in several ways — full detail in `finne/memory/client.py`'s module docstring. All required operations (R1 candidate search via `search_entities(category=...)`, R3 authority-event retrieval via `client.search(tiers=("journal",))`, tenant selection via `tenant_id=`) work as needed. No fallback was required. `MemoryClient.local()` needs no `sibyl init` credentials for local operations, resolving `HACKATHON_RULES.md`'s `ORG-Q3`.

## 8. Failure Paths And Degraded Behavior

`NEG-01` through `NEG-08` in `docs/product/ACTIVE_DEMO_DESIGN.md` section 8 are all in scope. Every failure resolves to constrain, block, or escalate. None widens authority. The full table is `PREREQ-003` section 19.

## 9. Deterministic Versus Model-Driven Behavior

| Owned deterministically | May be model-assisted |
| --- | --- |
| Owner ceiling, effective authority, intersection, amount limits | Extracting proposed facts from natural language |
| Approved network, asset, contract, protocol, function scope | Suggesting comparable precedents |
| Authority states, transitions, terminal-state enforcement | Explaining similarities and material differences |
| Valid citations, precedent eligibility, policy versions | Drafting the readable explanation |
| Exact identifier resolution, outcome recording | Proposing follow or distinguish treatment |
| Safe fallback, and the final allow / constrain / block / escalate | — |

The model may not expand authority, authorize an action, change an authority state, create a valid citation, confirm a precedent, sign a transaction, hold a key, submit a Base transaction, or bypass a deterministic rule.

## 10. Invariants

1. `authorized_amount <= owner_policy.max_amount` — always, including on malformed and adversarial input.
2. The engine never introduces a network, asset, contract, protocol, function, or action class absent from the owner ceiling.
3. Intersection can only narrow.
4. A non-`active` precedent can never raise authority.
5. A retrieval miss can only narrow authority, never widen it.
6. Removing the load-bearing memory reads makes autonomous execution impossible.
7. Authorization results are identical with and without a model API key.
8. An immutable record is never overwritten.
9. No key material reaches Sibyl Memory, logs, or the repository.
10. Every demonstration transaction carries zero value.

## 11. Observable Acceptance Criteria

| # | Criterion |
| --- | --- |
| A1 | Session 1 escalates rather than silently authorizing 25,000 at cold start |
| A2 | Session 1 persists the complete case and exits fully |
| A3 | Session 2 is a fresh process with no carried-over in-process state |
| A4 | Session 2 changes 25,000 proposed to 10,000 authorized |
| A5 | The change names `DV-001-V1` as the binding precedent on screen |
| A6 | With the tenant emptied, Session 2 escalates and cannot execute |
| A7 | `CASE-003` (withdrawn) is displayed but never raises authority to 20,000 |
| A8 | A materially different proposal is not silently followed |
| A9 | A 40,000 request is blocked regardless of precedent |
| A10 | Results are identical with no model API key present |
| A11 | A Base transaction executes within the bound and its hash is persisted |
| A12 | Base failure produces no false success and no fabricated reference |
| A13 | Duplicate execution is rejected at both application and contract level |
| A14 | The demo resets to a known state and rehearses repeatably |

## 12. Automated Tests Mapped To Acceptance Criteria

| Test file | Criteria |
| --- | --- |
| `test_authority_invariants.py` | A9, invariants 1–3, 5 |
| `test_authority_states.py` | A7, invariant 4 |
| `test_comparability.py` | A8 |
| `test_memory_roundtrip.py` | A2, invariant 8 |
| `test_fresh_session.py` | A1, A3, A4, A5, A6, A14, invariant 6 — A14 is proven by the test's own setup phase, which invokes `reset_demo.py` and asserts the pre-seeded (`CASE-003`..`008`) and not-seeded (`CASE-001`) state before each session run, then re-runs the full flow from that known state |
| `test_negative_cases.py` | A9, A10, A12, A13, invariant 7 |
| `test_base_adapter.py` | A11, A12, A13, invariant 10 |
| `test_import_boundaries.py` | Module constraints, invariant 9 |

## 13. Allowed Files And Ownership Area

Application files: exactly the layout in `PREREQ-003` section 18, plus `README.md` for the required memory read/write table. No application file outside that layout may be created or modified under this spec.

This restriction governs application code only. It does not, and cannot, override the standing obligations in `AGENT_BUILD_INSTRUCTIONS.md` to save material prompts under `prompts/` and to maintain `AI_USAGE.md`, `HUMAN_DECISIONS.md`, `BUILD_LOG.md`, and `REUSED_COMPONENTS.md` as work occurs. Those five locations are always in scope for every task under this spec, regardless of the application-file boundary above.

## 14. Dependencies And Rollback

- **Blocking:** None. Arko approved this specification 2026-09-03. `TASK-001` may now be created.
- **Resolved:** `ORG-Q2`. The repository is MIT-licensed (`DECISION-024`). `pyproject.toml` must declare `license = "MIT"`.
- **Non-blocking:** `ORG-Q1`. The build targets Base Sepolia; the network is one configuration value.
- **Rollback:** current `HEAD`. The slice adds new files only; no existing behavior can regress because none exists.
- **Build order, if Arko prefers smaller commits, split at these seams:** (a) models, policy, and the pure authority engine with its invariant tests; (b) the Sibyl Memory adapter and round-trip tests; (c) retrieval and the two session scripts; (d) the Base contract and adapter; (e) the terminal interface and explanation.

## 15. Explicit Exclusions

Web application or hosted service; Virtuals Protocol; real fund transfer; custody or portfolio logic; payments, escrow, x402, settlement, refunds, disputes, or service-delivery verification; multi-domain precedent support; authentication or multi-tenant production concerns; retrieval ranking quality work beyond deterministic candidate generation; any capability not required by the fourteen acceptance criteria.

## 16. Stop And Escalation Conditions

Stop and return to Arko when: the installed `sibyl-memory-client` cannot support the read/write boundary in `PREREQ-003` section 3 even with the documented fallback; Sibyl Memory cannot be made load-bearing; a genuine Base action cannot be demonstrated; any invariant in section 10 cannot be enforced deterministically; a model would need to make a deterministic or final decision; key material would need to leave `finne/base/`; `ORG-Q1` resolves in a way that requires mainnet funds; or the slice cannot satisfy an acceptance criterion within the allowed file set.
