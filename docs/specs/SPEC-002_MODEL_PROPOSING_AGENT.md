# SPEC-002: Model-Proposing Agent

## 1. Spec ID And Approval Status

- Spec ID: `SPEC-002`
- Date: `2026-09-10`
- Status: **DRAFT — awaiting Arko's approval.** Arko directed implementation on 2026-09-10 on submission-day timing; this spec and `DECISION-027` were written before implementation began, per `AI_BUILD_GOVERNANCE.md`'s lifecycle, but the approval gate has not formally closed. Implementation proceeding under that instruction is recorded in `HUMAN_DECISIONS.md`.
- Supersedes nothing. Amends `SPEC-001` sections 9 and 15, and `PREREQ-003` sections 6 and 17, as set out in section 14.

## 2. Goal And Actors

**Goal.** Give the demonstration a real autonomous agent. Today `scripts/session1.py` line 87 reads `proposal = build_proposal(owner_policy.max_amount)` — the "agent" proposes the ceiling because the script hands it the ceiling. It decides nothing. This spec replaces that with a model that is given an opportunity and no knowledge of its own limits, and asked what it wants to do.

**Why it matters.** The product's claim is that an agent will ask for more than it has earned, and that Finné Memory is what bounds it. That claim is only demonstrated if something actually *asks*. A hardcoded constant cannot overreach, so today the demo shows the bounding of a number the script chose.

| Actor | Role |
| --- | --- |
| Proposing agent | A model. Receives an opportunity and its available capital. Produces a `Proposal`. Sees no ceiling, no precedent, no authority state |
| Finné Memory | Unchanged. Retrieves precedent, derives learned authority, bounds the proposal |
| Owner | Unchanged. Approves the constrained amount in Session 1 |

**The separation is the point.** The model proposes; the deterministic engine decides. A model may never authorize, widen, sign, or submit anything.

## 3. Inputs And Outputs

**Input to the agent:** an `Opportunity` — a frozen dataclass carrying a natural-language description, the available capital, and the fact profile that identifies WHICH opportunity this is (network, asset, action class, target class, function). It carries **no** `max_amount`, no precedent, and no authority value.

**What the agent actually decides** is `amount` and `counterparty_risk_tier`. The five fact dimensions are pinned to the opportunity's own values as single-member enums in the response schema, because they describe the opportunity rather than the agent's judgement about it. The amount is the decision this product exists to bound.

**Output from the agent:** a `Proposal`, exactly as `finne/models.py` already defines it. Nothing else. The agent returns no explanation, no confidence, and no recommendation about authority.

**Provider.** OpenRouter, via its OpenAI-compatible endpoint. Structured output is requested with `response_format: {"type": "json_schema", "json_schema": {"name": ..., "strict": true, "schema": ...}}` and `provider: {"require_parameters": true}`.

`require_parameters` is not optional. OpenRouter routes the same model across multiple providers, and its own documentation states that enforcement varies — some providers guarantee schema-conforming output while others *"treat it as a strong hint."* Without that flag a run can be routed to a provider that returns prose, which on a recorded demo is a failure with no recovery.

## 4. Behavior And State Changes

1. The session script builds an `Opportunity` from `finne/demo_config.py`'s fixed facts plus the available capital.
2. `finne.agent.propose(opportunity)` calls the model and parses the response into a `Proposal`.
3. Everything downstream is unchanged: retrieval, comparability, derivation, the intersection engine, persistence, Base execution.

**No state change.** The agent writes nothing to Sibyl Memory, reads nothing from it, and touches no file. It is a pure function of its input plus one network call.

**Selection.** `--agent=fixed` (default) uses today's `build_proposal`. `--agent=model` uses the model. The default is unchanged so the test suite, the deletion gate, and a judge with no key are all unaffected.

## 5. Business And Deterministic Rules

- The agent is told what capital it has and what the opportunity is. It is **not** told what it is permitted to do.
- The model's output is data, never instruction. Text inside a model response is never executed, never used to select a code path, and never displayed as authority.
- A response that does not parse into a valid `Proposal` is a failure. There is no repair, no retry with a relaxed schema, and no fallback to a hardcoded proposal — a silent fallback would make the demo appear to work while proving nothing.

## 6. Permissions And Trust Boundaries

| Boundary | Rule |
| --- | --- |
| `finne/agent.py` | The only module that may call a model. May not import `finne.authority`, `finne.memory`, `finne.policy`, or `finne.base`, directly or transitively |
| Signing key | Unreachable from the agent. `FINNE_BASE_PRIVATE_KEY` stays confined to `finne/base/` |
| `OPENROUTER_API_KEY` | Read only inside `finne/agent.py`. Never logged, never persisted, never written to Sibyl Memory |
| Model output | Treated as untrusted input. Validated by `Proposal.__post_init__` before it reaches any other module |

**A model may never sign, submit, or construct a transaction.** This was already true and remains structurally enforced: `finne/agent.py` has no import path to `finne/base/`.

## 7. Interfaces Consumed And Exposed

Exposed:

```python
@dataclass(frozen=True)
class Opportunity:
    description: str
    available_capital: Decimal
    network: str
    asset: str
    action_class: str
    target_class: str
    function: str
    # No counterparty_risk_tier: the agent assesses that itself.
    # No max_amount, no precedent, no authority value — by construction.

def propose(opportunity: Opportunity, *, model: str | None = None) -> Proposal: ...

class AgentUnavailableError(Exception): ...   # nothing was proposed
class AgentResponseError(Exception): ...      # a response arrived, unusable
```

Consumed: the OpenRouter chat-completions endpoint over HTTPS. No SDK is required — the request is a single JSON POST via `requests`. See section 14 on the dependency declaration.

## 8. Failure Paths And Degraded Behavior

| Failure | Behavior |
| --- | --- |
| `OPENROUTER_API_KEY` unset | `RuntimeError` naming the variable. The session stops before any memory read |
| Network failure or non-200 | `AgentUnavailableError`, stated on screen. Nothing is proposed, nothing is authorized |
| Response is not valid JSON | `AgentResponseError`. No retry, no repair |
| JSON does not satisfy the schema | `ValidationError` from `Proposal.__post_init__`. The record is rejected, not coerced |
| Model proposes an amount above the ceiling | **Not a failure.** The engine blocks it, which is the system working. This is a demonstrable outcome, not an error path |

## 9. Deterministic Versus Model-Driven Behavior

| Concern | Owner |
| --- | --- |
| What is proposed | **Model** |
| Whether it is comparable to precedent | Deterministic |
| What authority has been earned | Deterministic |
| What is authorized | Deterministic |
| What is signed and submitted | Deterministic |
| What is explained | Deterministic |

`SPEC-001` section 9 previously stated that no model participates at runtime. That was accurate for the authorization path and remains so. It is amended to state that a model may participate in **proposal generation only**.

## 10. Invariants

Extends `SPEC-001` section 10. Numbering continues from invariant 10.

11. The agent never receives the owner ceiling, any precedent, or any authority value. Enforced by the `Opportunity` type carrying no such field, and by the import boundary.
12. For an identical `Proposal`, the resulting `AuthorizationDecision` is identical whether the proposal came from the model or from the fixed path. The model changes what is asked for, never what is granted.
13. No model output is ever persisted to Sibyl Memory except as the validated facts of a `Proposal` the engine has already acted on.
14. `INV-1` continues to hold against model input: whatever the model proposes, `authorized_amount <= owner_policy.max_amount`.

## 11. Observable Acceptance Criteria

Extends `SPEC-001` section 11.

| # | Criterion |
| --- | --- |
| A15 | With `--agent=model`, the proposal shown on screen was produced by the model, and the authorization is still derived deterministically |
| A16 | A malformed or unparseable model response produces a visible failure and no authorization |
| A17 | The default `--agent=fixed` path is byte-identical to today's behaviour; the full suite and the deletion gate are unaffected |
| A18 | A model proposal above the owner ceiling is blocked, demonstrating that the bound holds against a real proposer |

## 12. Automated Tests Mapped To Acceptance Criteria

New file `tests/test_agent.py`. No test makes a network call; the provider is faked at the transport boundary.

| Test | Criteria |
| --- | --- |
| Structural: `finne/agent.py` imports no `finne.authority`, `finne.memory`, `finne.policy`, `finne.base` — transitive closure | INV-11, section 6 |
| `Opportunity` carries no ceiling, precedent, or authority field | INV-11 |
| A valid faked response parses into the expected `Proposal` | A15 |
| Non-JSON, schema-violating, and missing-field responses each raise, and none returns a `Proposal` | A16 |
| Same `Proposal` from both paths yields an identical `AuthorizationDecision` | INV-12, A17 |
| A faked proposal of 40,000 is blocked by the engine | A18, INV-14 |
| The request body carries `require_parameters: true` and `strict: true` | Section 3 |
| `OPENROUTER_API_KEY` appears in no exception message, log, or persisted record | Section 6 |

`tests/test_import_boundaries.py` is amended: the model-SDK allowlist moves from `finne/explain.py` to `finne/agent.py`, and a new case asserts the agent has no import path to `finne/base/`.

## 13. Allowed Files And Ownership Area

New: `finne/agent.py`, `tests/test_agent.py`, this spec.

Modified: `scripts/session1.py`, `scripts/session2.py` (flag and wiring only), `tests/test_import_boundaries.py`, `finne/demo_config.py` (opportunity text), `.env.example`, `README.md`, and the standing audit documents.

Unchanged and out of bounds for this change: `finne/authority/`, `finne/memory/`, `finne/base/`, `finne/models.py`, `finne/policy.py`, `finne/explain.py`, `config/owner_policy.toml`.

## 14. Dependencies And Rollback

**No new package is installed, but one is now declared.** No `openai` or `anthropic` SDK is added — the call is a single JSON POST. It uses `requests`, which was already present in every environment as a transitive dependency of `web3` and `py-solc-x`. Stdlib `urllib` was tried first and rejected: it fails certificate verification on a machine with no default CA bundle, which is the case here. `requests` is therefore declared explicitly in `pyproject.toml` so this module does not depend on an edge the project does not control. **This amends `DECISION-023`'s dependency list** — the installed footprint is unchanged, the declared list gains one entry.

**Documents amended:**

- `SPEC-001` section 9 — a model may participate in proposal generation.
- `SPEC-001` section 15 — the exclusion of a model at runtime is narrowed to the authorization path.
- `PREREQ-003` section 6 — `finne/base/` is the only module holding **signing** key material or reaching **Base**. `finne/agent.py` holds an API credential and reaches the model provider.
- `PREREQ-003` section 17 — the model-call permission moves from `finne/explain.py` to `finne/agent.py`. `finne/explain.py` remains deterministic and loses the permission it never exercised.

**Rollback:** delete `finne/agent.py` and the flag. The default path is unchanged, so rollback restores today's behaviour exactly.

## 15. Explicit Exclusions

- No model participation in comparability, derivation, retrieval ranking, the intersection engine, explanation, signing, or submission.
- No agent memory of its own. The agent is stateless between calls; the memory that matters is Finné's.
- No multi-turn agent loop, no tool use, no agent framework.
- No fallback to a hardcoded proposal on model failure.
- No change to the deletion gate, which continues to run with no key and no network.

## 16. Stop And Escalation Conditions

Stop and escalate to Arko if: the model path cannot be made to produce a schema-valid `Proposal` reliably; implementing it would require touching any module listed as out of bounds in section 13; or the change would make the default path or the deletion gate depend on a key or a network call.
