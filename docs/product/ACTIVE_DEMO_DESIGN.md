# Active Demo Design: Base Agent-Permission Precedent

## Status

- CONFIRMED: This is the **active** V1 demonstration design under `DECISION-022`. It replaces supplier onboarding as the active demo domain.
- CONFIRMED: It instantiates the `PREREQ-002` object model, authority states, and invariants in the Base agent-permission domain. The model is unchanged; only the domain instance is new.
- HISTORICAL: `docs/product/PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md` remains the validated supplier-domain corpus and is preserved as historical design work.
- CONFIRMED: Every record here is synthetic. No real counterparty, protocol, or fund is represented.
- CONFIRMED: No fixture places real capital at risk. Authorized amounts are represented as policy values in authorization records; executed Base transactions carry zero value.

## 1. Owner Permission Ceiling

The owner ceiling is owner-controlled configuration. Finné Memory reads it and can never write it.

| Dimension | Owner ceiling `OP-001` |
| --- | --- |
| `max_amount` | `25000.00 USDC` |
| `network` | `base` |
| `asset` | `USDC` |
| `action_class` | `capital_deployment` |
| `approved_target_classes` | `demo_receipt`, `yield_vault_conservative` |
| `approved_functions` | `recordAuthorization`, `deposit` |
| `unknown_situation_behaviour` | `escalate_to_owner` |
| `cold_start_autonomous_amount` | `0.00 USDC` |

- CONFIRMED: `cold_start_autonomous_amount` of zero is what forces the safe cold-start path in Session 1. With no precedent, the intersection yields zero autonomous authority, so the outcome is `escalate`, never a silent 25,000 USDC allow.

## 2. Material Fact Dimensions

Every proposal and every recorded case carries these structured facts.

| Fact | Type | Role |
| --- | --- | --- |
| `network` | Enum | Comparability dimension |
| `asset` | Enum | Comparability dimension |
| `action_class` | Enum | Comparability dimension |
| `target_class` | Enum | Comparability dimension |
| `function` | Enum | Comparability dimension |
| `counterparty_risk_tier` | `low` / `medium` / `high` | Comparability dimension, directional |
| `amount` | Decimal | Constrained output, **not** a comparability dimension |
| `proposed_at` | Timestamp | Provenance |

## 3. Deterministic Comparability Rule

A prior case is **materially comparable** to a current proposal if and only if:

1. `network`, `asset`, `action_class`, `target_class`, and `function` match exactly; and
2. the current `counterparty_risk_tier` is not worse than the precedent's tier.

Any mismatch is a **material difference**. A materially different case may be retrieved and displayed, and a model may explain the difference, but it cannot be followed. Amount never affects comparability; it is the value being constrained.

- CONFIRMED: The directional risk-tier check specifically stops a current proposal that is *riskier* than its precedent from inheriting that precedent's authority — e.g. a `high`-risk current proposal could not follow a `low`-risk precedent even if every other dimension matched exactly. A precedent that is riskier than the current proposal remains comparable (a successful high-risk case is at least as strong grounds for a lower-risk one). Every proposal in this corpus is fixed at `low` risk, so this exclusion direction is never exercised by a corpus fixture; it is proven by `test_comparability.py` against a synthetic higher-risk-current-vs-lower-risk-precedent input instead.

## 4. Learned-Constraint Derivation Policy

Owner-defined and owner-controlled. V1 policy `LCP-001`:

```
eligible = cases that are materially comparable
           AND authority_state == "active"
           AND outcome == "success"

learned_max_amount = max(authorized_amount of eligible)  if eligible is non-empty
                   = cold_start_autonomous_amount        if eligible is empty
```

- CONFIRMED: Only `active` precedents enter `eligible`. `draft`, `questioned`, `superseded`, and `withdrawn` cases are excluded from derivation while remaining retrievable and displayable.
- CONFIRMED: The learned value is one input to the intersection, never an override. `effective_authority` is the strictest of owner ceiling, hard policy, active precedent constraints, learned constraint, and current action scope.
- CONFIRMED: A `questions` relationship targeting a case removes it from `eligible` until an authorized confirmation restores it.

## 5. Corpus Fixtures

Identifiers follow the `PREREQ-002` convention: stable `CASE-nnn` identity, immutable `MV-nnn-Vk` matter versions and `DV-nnn-Vk` decision versions.

| Case | Matter / Decision version | Facts | Authorized | Outcome | Authority state | Role in demo |
| --- | --- | --- | --- | --- | --- | --- |
| `CASE-001` | `MV-001-V1` / `DV-001-V1` | base, USDC, capital_deployment, yield_vault_conservative, deposit, risk `low` | `10000.00` | `success` | `active` | Session 1 baseline; the precedent Session 2 must find |
| `CASE-002` | `MV-002-V1` / `DV-002-V1` (created at write-back) | Identical fact profile to `CASE-001`, proposed `25000.00` | `10000.00` | `success` | `draft` | Session 2 current proposal; expects constrain to `10000.00`; its own resulting decision version stays `draft` — promoting it to `active` is out of this slice's scope |
| `CASE-003` | `MV-003-V1` / `DV-003-V1` | Identical fact profile, authorized `20000.00` | `20000.00` | `success` | `withdrawn` | Highly similar but **withdrawn**; must not raise authority to 20,000 |
| `CASE-004` | `MV-004-V1` / `DV-004-V1` | base, USDC, capital_deployment, `demo_receipt`, `recordAuthorization`, risk `low` | `5000.00` | `success` | `active` | Less similar but active; proves similarity and authority are separate |
| `CASE-005` | `MV-005-V1` / `DV-005-V1` | Same as `CASE-001` except `target_class` = `yield_vault_aggressive` | `10000.00` | `success` | `active` | Material-difference fixture: `target_class` mismatch excludes it from derivation even though authority state and outcome match `CASE-001` exactly |
| `CASE-006` | `MV-006-V1` / `DV-006-V1` | Identical fact profile, authorized `15000.00` | `15000.00` | `success` | `superseded` | Superseded by `DV-001-V1`; retrievable, not authorizing |
| `CASE-007` | `MV-007-V1` / `DV-007-V1` | Identical fact profile, authorized `12000.00` | `12000.00` | `failure` | `questioned` | Failed outcome later questioned; excluded from derivation |
| `CASE-008` | `MV-008-V1` / `DV-008-V1` | Identical fact profile, authorized `18000.00` | `18000.00` | `success` | `draft` | Recorded but never owner-confirmed; cannot authorize |

- CONFIRMED: `CASE-003`, `CASE-006`, `CASE-007`, and `CASE-008` all carry authorized amounts **above** 10,000 USDC. This is deliberate. If authority-state filtering is broken, the derived learned maximum rises above 10,000 and the demo assertion fails loudly.
- CONFIRMED: `CASE-001` is the only `active`, comparable, successful case at the 10,000 level, so `learned_max_amount` for Session 2 is exactly `10000.00`.

## 6. Precedent Relationships

| Relationship | From | To | Effect |
| --- | --- | --- | --- |
| `supersedes` | `DV-001-V1` | `DV-006-V1` | `CASE-006` moves to `superseded` |
| `questions` | `DV-007-V1` | `DV-007-V1` (outcome-driven) | `CASE-007` moves to `questioned` |
| `distinguishes` | `DV-002-V1` | `DV-005-V1` | Records why the `target_class`-mismatched case is not followed |
| `follows` | `DV-002-V1` | `DV-001-V1` | The authorizing citation for Session 2 |

- CONFIRMED: Every `PrecedentRelationship` is canonically between two exact `decision_version_id`s, per the retained `PREREQ-002` contract. The `distinguishes` and `follows` rows above are therefore not pre-existing at proposal time — they can only be persisted once `DV-002-V1` exists, which happens at Session 2's write-back (section 7 below), not when `CASE-002` is merely proposed.
- CONFIRMED: A model may propose any of these. Only deterministic validation plus an authorized confirmation path may persist or apply them.
- DEFERRED 2026-09-04 (two independent Codex passes on seam (c): round 1 found `PrecedentRelationship` persistence missing, round 2 found the round-1 implementation's `fact_ids`/`citation_ids` didn't meet the retained contract): **persisting `PrecedentRelationship` records themselves is out of scope for this slice.** `PREREQ-002`'s own contract requires `fact_ids`/`citation_ids` to reference real, human-validated `CitationEdge`/`Fact` entities with a rejection-audit path (`CitationAttemptAuditEvent`) — a genuine validated-reference subsystem, not a shape a few tuples of strings can satisfy. Building that is excluded by `SPEC-001` section 15 ("multi-domain precedent support"), is required by none of `SPEC-001`'s fourteen acceptance criteria, and is not part of `PREREQ-003` section 3's load-bearing W1-W5/R1-R5 set — `DV-002-V1`'s own authority state and cited-precedent explanation (in `AuthorizationDecision.cited_precedents`, shown live in Session 2) already carry the demo's authorizing claim; only the separate, canonical `PrecedentRelationship` audit objects in this table are deferred.

## 7. The Two-Session Demonstration

### Session 1 — establish experience

1. Owner ceiling `OP-001` is loaded: 25,000 USDC on Base.
2. The agent proposes `CASE-001` at `25000.00` USDC.
3. Finné Memory finds no comparable active precedent. `learned_max_amount` falls back to `cold_start_autonomous_amount` = `0.00`.
4. The intersection yields zero autonomous authority. The decision is `escalate` — **not** a silent 25,000 USDC allow.
5. The owner approves a constrained authority of `10000.00` USDC under the `CASE-001` conditions.
6. Finné Memory writes the immutable case version and owner-policy snapshot to Sibyl Memory. The Owner, acting as **Decision Reviewer**, confirms creation of the immutable draft decision version `DV-001-V1`. Per the retained `PREREQ-002` authority transitions, this confirmation is itself the initial `No prior state → draft` `AuthorityEvent` — not merely a data write. **CORRECTED 2026-09-05** (ordering only, fact-correction — independent review found this document, `PREREQ-003`, and `SPEC-001` all described these writes happening after Base execution rather than before it; the case version, snapshot, and authority events do not wait on Base, per `PREREQ-003` section 3's own W-table — only the outcome, W4, does).
7. The Owner, acting separately as **Authority Steward** — a distinct timestamped action, even though it is the same person — confirms activation: a second `AuthorityEvent` records `draft → active`, promoting `DV-001-V1` to `active`.
8. The agent executes the safe Base demonstration action within the bound. The authorization receipt records `10000.00` USDC as a policy value; the transaction carries zero value. If the transaction settles (confirmed success or confirmed revert), the outcome and Base transaction reference (W4) are written now. If the receipt wait times out or errors, the transaction may still be pending — W4 is deliberately left unwritten rather than recording a possibly-wrong immutable failure, and is completed later once the original transaction's own receipt can be checked directly.
9. **The process terminates completely**, regardless of whether W4 completed or is left pending reconciliation.

### Session 2 — memory changes behaviour

1. A genuinely fresh process starts. No in-process state is carried over.
2. The same owner ceiling `OP-001` is loaded: 25,000 USDC.
3. The agent proposes `CASE-002` at `25000.00` USDC — the broader action.
4. Finné Memory retrieves prior cases from Sibyl Memory.
5. Deterministic checks: `CASE-001` is materially comparable; its authority state is `active`; the current facts satisfy its conditions. `CASE-003`, `CASE-006`, `CASE-007`, and `CASE-008` are retrieved and displayed but excluded from derivation by authority state or outcome.
6. `learned_max_amount` = `10000.00`.
7. The intersection binds on the learned constraint. The decision is `constrain` to `10000.00` USDC. The `AuthorizationDecision.cited_precedents` names `DV-001-V1` as the supporting precedent — this is the decision's own explanation citing a prior decision version, not yet a persisted `PrecedentRelationship`, since `CASE-002` has no decision version of its own until write-back.
8. The action changes: **25,000 USDC proposed → 10,000 USDC authorized**.
9. Finné Memory writes the immutable case version and owner-policy snapshot. The Owner, acting as **Decision Reviewer**, confirms creation of the immutable draft decision version `DV-002-V1` for `CASE-002` — the initial `No prior state → draft` `AuthorityEvent`, exactly as in Session 1 step 6. **CORRECTED 2026-09-05** (ordering only, matching Session 1's correction above — these writes do not wait on Base).
10. The agent executes the safe Base action within the bound. The receipt represents `10000.00` USDC; zero value moves. If the transaction settles, the new outcome (W4) is written back to Sibyl Memory now; a receipt-wait timeout leaves W4 pending, completed later once the original transaction's own receipt can be checked directly.
11. Section 6 names the `follows` (`DV-002-V1` → `DV-001-V1`) and `distinguishes` (`DV-002-V1` → `DV-005-V1`) treatments; per section 6's 2026-09-04 deferral note, persisting these as canonical `PrecedentRelationship` records is out of scope for this slice — `DV-002-V1` already carries its citation live, in `AuthorizationDecision.cited_precedents`, shown on screen in step 8. `DV-002-V1` remains `draft` — promoting it to `active` is also out of scope for this slice.

- CONFIRMED: The changed action must be visible on screen and attributable to the recalled memory, naming `DV-001-V1` as the binding precedent.

### Control — memory removed

With the Sibyl Memory database removed or emptied, Session 2 retrieves nothing, `learned_max_amount` falls back to `0.00`, and the decision is `escalate`. The agent cannot proceed autonomously. This is the organiser's deletion test and it is also an automated test.

## 8. Negative Cases

| ID | Scenario | Required behaviour |
| --- | --- | --- |
| `NEG-01` | Sibyl Memory absent, empty, or unauthenticated | Safe fallback: `escalate`. Never a silent allow. |
| `NEG-02` | Only `CASE-003` (withdrawn) matches | Retrieved and displayed; excluded from derivation; result `escalate`, never `20000.00` |
| `NEG-03` | Proposal is materially different from every active case | Cannot silently follow; result `escalate` with the difference stated |
| `NEG-04` | Proposal of `40000.00` USDC, above the owner ceiling | `block`, regardless of any precedent |
| `NEG-05` | No model API key, or model returns malformed output | Deterministic path produces the identical authorization; explanation degrades to a deterministic template |
| `NEG-06` | Malformed or contradictory memory record | Treated as absent, not as permission; result constrains or escalates |
| `NEG-07` | Base transaction reverts or is rejected outright before broadcast | No false success; outcome recorded as `failure`; no fabricated transaction reference |
| `NEG-08` | The same authorized action is executed twice | Idempotency key prevents a second execution and prevents an inconsistent outcome record; the deployed contract's own `authorizedSigner` restriction additionally prevents a third party from ever recording a competing entry for the same `decisionId` |
| `NEG-09` | Base transaction is broadcast but the receipt wait times out or errors | **ADDED 2026-09-05** (independent review, seam (d)): distinct from `NEG-07` — the transaction may still be mined and may still succeed, and `Outcome` is write-once, so treating this identically to a confirmed revert (the original `NEG-07` wording, since corrected) could permanently misrepresent a still-pending, possibly-successful case. No outcome is written; `finne.base.adapter.reconcile_pending()` / `scripts/reconcile_outcome.py` resolve it later against the original transaction's own receipt. |

## 9. Reset Procedure

The demo must be resettable to a known starting state: clear the demo tenant's records from Sibyl Memory, then re-seed `CASE-003` through `CASE-008` as pre-existing history while leaving `CASE-001` to be created live in Session 1.

- CONFIRMED: `CASE-001` is never seeded. It must be produced by Session 1 so the fresh-session recall in Session 2 is genuine rather than staged.

## 10. Traceability To Acceptance Criteria

| PRD acceptance criterion | Demonstrated by |
| --- | --- |
| 1, 2 | Session 1 steps 1–9 |
| 3, 4 | Session 2 steps 1–8 |
| 5 | Control — memory removed |
| 6 | `CASE-003`, `NEG-02` |
| 7 | `CASE-005`, `NEG-03` |
| 8 | `NEG-04` |
| 9 | `NEG-05` |
| 10 | Session 1 step 6, Session 2 step 9 |
| 11 | `NEG-07`, `NEG-09` |
| 12 | Reset procedure |
| 13 | No fixture references payment, escrow, x402, settlement, or dispute behaviour |
