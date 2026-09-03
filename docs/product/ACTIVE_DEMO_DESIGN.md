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
| `CASE-002` | `MV-002-V1` / — | Identical fact profile to `CASE-001`, proposed `25000.00` | — | — | — | Session 2 current proposal; expects constrain to `10000.00` |
| `CASE-003` | `MV-003-V1` / `DV-003-V1` | Identical fact profile, authorized `20000.00` | `20000.00` | `success` | `withdrawn` | Highly similar but **withdrawn**; must not raise authority to 20,000 |
| `CASE-004` | `MV-004-V1` / `DV-004-V1` | base, USDC, capital_deployment, `demo_receipt`, `recordAuthorization`, risk `low` | `5000.00` | `success` | `active` | Less similar but active; proves similarity and authority are separate |
| `CASE-005` | `MV-005-V1` / `DV-005-V1` | Same as `CASE-001` except `counterparty_risk_tier` = `high` | `10000.00` | `success` | `active` | Material-difference fixture; cannot be silently followed by a `low`-tier proposal's inverse |
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
| `distinguishes` | `MV-002-V1` | `DV-005-V1` | Records why the `high`-tier case is not followed |
| `follows` | `MV-002-V1` | `DV-001-V1` | The authorizing citation for Session 2 |

- CONFIRMED: A model may propose any of these. Only deterministic validation plus an authorized confirmation path may persist or apply them.

## 7. The Two-Session Demonstration

### Session 1 — establish experience

1. Owner ceiling `OP-001` is loaded: 25,000 USDC on Base.
2. The agent proposes `CASE-001` at `25000.00` USDC.
3. Finné Memory finds no comparable active precedent. `learned_max_amount` falls back to `cold_start_autonomous_amount` = `0.00`.
4. The intersection yields zero autonomous authority. The decision is `escalate` — **not** a silent 25,000 USDC allow.
5. The owner approves a constrained authority of `10000.00` USDC under the `CASE-001` conditions.
6. The agent executes the safe Base demonstration action within the bound. The authorization receipt records `10000.00` USDC as a policy value; the transaction carries zero value.
7. Finné Memory writes the complete case to Sibyl Memory: owner ceiling, proposal, circumstances, material facts, constrained authority, decision, action, Base transaction reference, observed outcome, supporting evidence, and precedent status.
8. Owner confirmation promotes `DV-001-V1` from `draft` to `active` as a separate timestamped authority event.
9. **The process terminates completely.**

### Session 2 — memory changes behaviour

1. A genuinely fresh process starts. No in-process state is carried over.
2. The same owner ceiling `OP-001` is loaded: 25,000 USDC.
3. The agent proposes `CASE-002` at `25000.00` USDC — the broader action.
4. Finné Memory retrieves prior cases from Sibyl Memory.
5. Deterministic checks: `CASE-001` is materially comparable; its authority state is `active`; the current facts satisfy its conditions. `CASE-003`, `CASE-006`, `CASE-007`, and `CASE-008` are retrieved and displayed but excluded from derivation by authority state or outcome.
6. `learned_max_amount` = `10000.00`.
7. The intersection binds on the learned constraint. The decision is `constrain` to `10000.00` USDC, citing `DV-001-V1` under a `follows` relationship.
8. The action changes: **25,000 USDC proposed → 10,000 USDC authorized**.
9. The agent executes the safe Base action within the bound. The receipt represents `10000.00` USDC; zero value moves.
10. The new outcome is written back to Sibyl Memory.

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
| `NEG-07` | Base transaction reverts, times out, or fails | No false success; outcome recorded as `failure`; no fabricated transaction reference |
| `NEG-08` | The same authorized action is executed twice | Idempotency key prevents a second execution and prevents an inconsistent outcome record |

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
| 11 | `NEG-07` |
| 12 | Reset procedure |
| 13 | No fixture references payment, escrow, x402, settlement, or dispute behaviour |
