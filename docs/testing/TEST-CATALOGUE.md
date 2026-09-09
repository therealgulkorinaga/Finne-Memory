# Test Catalogue

## Status

- DRAFT, COMMITTED 2026-09-09 on Arko's authorization. Committing it does not approve it: **four questions remain open and nine cases are blocked on them.** The catalogue must not be implemented until Q1-Q4 are answered, because two of the answers change what the expected result ought to be. See "Open Questions" below.
- Round 2 independent review is prepared at `prompts/2026-09-08-test-catalogue-codex-review-round-2.md` and **has not been run.** Arko authorized the commit with that pass outstanding.
- This document is a **specification of test cases**, not test code. It does not change behaviour and does not add a dependency.
- Round 1 review verdict was NOT READY FOR COMMIT, with two blockers, and every one of its twelve findings was reproduced and accepted. Both blockers are addressed here: the false-invariant case is recorded as `F-9` and returned to Arko, and every row carries a **Class** separating what the system SHOULD do from what it currently DOES.
- **`F-9` reports that `SPEC-001` invariant 5 is false for a legal configuration.** An approved specification containing a false statement is a governance matter, not only a test-design one; it is recorded in `HUMAN_DECISIONS.md` as outstanding.
- Scope: the whole system — every module under `finne/`, every script under `scripts/`, the Solidity contract, the demo corpus, and the cross-session behaviour the organiser's gate turns on.

## What This Document Is, And What It Is Not

Round 1 review found the original draft conflated two incompatible things: requirements a test should lock in, and observations about how the code currently happens to behave. Written the same way, both read as "expected" — so implementing the catalogue as written would have frozen several defects into passing tests while the recommendations section simultaneously proposed fixing them.

Every row therefore carries a **Class**:

| Class | Meaning | May a test assert it? |
| --- | --- | --- |
| `REQ` | A requirement. The expected result is what the system SHOULD do, and a test asserting it locks in correct behaviour. | Yes |
| `CHAR` | Characterization. Records current behaviour that is neither clearly right nor wrong, so that a future change to it is deliberate rather than accidental. | Yes, but the test must say in its docstring that it pins current behaviour, not a requirement |
| `DEFECT` | Current behaviour is wrong. The row states what happens now AND what should happen. | **No** — not until the defect is fixed or formally accepted. Asserting the observed behaviour would make the defect permanent |
| `UNRES` | Behaviour is undefined and the correct answer is a decision Arko has not made. | **No** — the row is a question, not a case |

The document is also split into two parts, for the reason round 1 gave: a 1,000-line normative specification turns every implementation quirk into permanent product law.

- **Part I is normative.** Acceptance-level scenarios, the high-risk matrices, key-material cases, and the property sweeps. These are the cases worth implementing and maintaining.
- **Part II is an appendix and is explicitly NOT authoritative.** It is a field-by-field inventory of current behaviour, useful for finding holes and for onboarding, and it should be treated as a worklist rather than a contract. Where an appendix row still carries a real invariant it is marked `REQ`, and those rows alone remain binding.

## How Coverage Was Determined — Corrected After Round 1

The `Coverage` column names an existing test only when that test actually asserts the case.

**These marks are inspection-based, not instrumented.** `coverage` is not installed and is not in `pyproject.toml`; `DECISION-023` fixes the dependency list, so adding one to produce this document would be an architecture change requiring a decision record. That remains a recommendation, not an action.

Round 1 found the first draft's column unreliable in both directions, and it was right. Five cited tests did not reach the case they were cited for, and eighteen rows claimed coverage with no named test at all, using phrases like "Widely used" and "via seeding" that let a setup fixture masquerade as an assertion. The column has been re-audited with a stricter vocabulary:

| Mark | Meaning |
| --- | --- |
| `` `test_name` `` | That test asserts this case. Verified by reading the test body, not its name |
| `PARTIAL` | The named test reaches the case but does not assert all of it; what it misses is stated |
| `INDIRECT` | The case is exercised as setup for another assertion, never asserted itself. **Counted as uncovered** |
| `GAP` | No test found. A claim about a search, not a proof of absence |

Baseline: 181 test functions, 4,069 lines, **229 passed, 4 skipped** in 23.46s. The 4 skips are live Base tests gated behind `FINNE_LIVE_BASE_TEST=1`.

## Conventions

- **TC IDs** are stable and flat. Ranges are allocated per area with gaps so cases can be inserted without renumbering.
- Amounts are USDC. `OP-001` is the ceiling in `config/owner_policy.toml`: `max_amount` 25000.00, `cold_start_autonomous_amount` 0.00, network `base`, asset `USDC`, action class `capital_deployment`, approved target classes `demo_receipt` / `yield_vault_conservative`, approved functions `recordAuthorization` / `deposit`.
- "Baseline facts" means the `CASE-001` profile: base / USDC / capital_deployment / yield_vault_conservative / deposit / risk `low`.
- Exact values are written with their decimal scale, because `Decimal("10000.00")` and `Decimal("10000")` compare equal but are not the same object, and exact decimal handling is this system's discipline.
- Where a case needs a Sibyl exception instance, note that all of them require a `message` argument and `TierGateError` additionally requires keyword-only `feature` — its signature is `(message, *, feature, current_tier="free", upgrade_url=...)`. Round 1 found the first draft's examples uninstantiable.

---

# Findings

Ten findings. Each was **reproduced against the running code**, and the reproduction is stated so a reviewer can repeat it. Round 1 confirmed F-1, F-3, F-5, F-7 and F-8 as written; found F-2 and F-6 materially understated, now corrected; found F-4's reproduction underspecified, now corrected; and found two the first draft missed entirely, recorded here as F-9 and F-10.

**F-9 — `INV-5` is false for a legal configuration. (BLOCKER, raised by round 1.)**

`SPEC-001` invariant 5 states unconditionally that "a retrieval miss can only narrow authority, never widen it." That is false whenever `cold_start_autonomous_amount` exceeds an eligible precedent's authorized amount.

Reproduced with cold start `500.00` and one eligible precedent authorized `100.00`, proposal 25000.00:

```
with precedent    -> constrain 100.00  bound by learned_constraint
precedent MISSED  -> constrain 500.00  bound by learned_constraint
```

Losing the precedent RAISED authority five-fold. The mechanism is in `derivation.py`: an empty eligible set falls back to the cold-start allowance, and nothing constrains that fallback to be lower than what a real precedent would have produced.

The live configuration sets `cold_start_autonomous_amount = "0.00"`, so the invariant holds for the demo and for every current test. It is the INVARIANT that is wrong, not the code — or else the code is missing a clamp. Which of those is true is a product decision, not something this catalogue may settle. **Returned to Arko as Q1.**

**F-10 — a sixth `BaseExecutionResult` shape is constructible. (Raised by round 1.)**

The first draft asserted five coherent shapes. Exhaustive construction over `attempted x success x outcome_confirmed x {None, "0xabc", ""}` yields six:

```
(True,  True,  True,  '0xabc')     confirmed success
(True,  False, True,  None)        pre-broadcast rejection, no hash
(True,  False, True,  '0xabc')     confirmed revert
(True,  False, True,  '')          <-- the sixth
(True,  False, False, '0xabc')     unknown outcome
(False, False, True,  None)        unattempted
```

`__post_init__` rejects an empty `tx_hash` only on the success path, so an attempted, confirmed FAILURE may carry `tx_hash=""`. Whether that is coherent — an empty string is not a reference, but a confirmed failure is permitted to have no reference at all — or whether it should be normalised to `None`, is a decision. **Returned to Arko as Q3.**

**F-2 — a zero-authorized eligible precedent produces a FALSE explanation. (Understated in the first draft; corrected after round 1.)**

The first draft called this attribution "odd." It is worse than that. Reproduced with one comparable, active, successful precedent authorized `0.00`:

```
learned:     0.00, basis 'precedent', supporting ('DV-001-V1',)
result:      escalate, binding learned_constraint, cited ('DV-001-V1',)
explanation: "... No active, comparable, successful precedent supports it,
              and the owner's cold-start autonomous amount is zero. ..."
```

The decision cites `DV-001-V1` and simultaneously states that no active, comparable, successful precedent supports it. Both cannot be true. This is a false statement rendered beside a correct decision — precisely the class of defect that four rounds of seam (e) review were spent eliminating from the explanation layer, reappearing in the ENGINE's own explanation string, which was never suspected because it was assumed to be derived purely from facts. The escalation itself is correct and safe. Unreachable from the current corpus. Cases: TC-098, TC-187, TC-229b.

**F-6 — the fold's behaviour on identical timestamps is genuinely undefined. (Understated in the first draft; corrected after round 1.)**

The first draft called this a theoretical risk. Round 1 asked for a probe, and the probe settles it. With two events sharing a timestamp, `fold_authority_state` returns a DIFFERENT answer depending on the order the journal search returned them:

```
search order [draft, active] -> ACTIVE
search order [active, draft] -> None
```

Python's stable sort preserves search order on a tie, and that order is FTS5 relevance, not write order. So the same stored history folds to `active` or to nothing depending on an ordering nobody controls. Millisecond resolution makes a tie unlikely — two consecutive appends were observed 10ms apart — but "unlikely" is not "defined," and one of the two outcomes grants authority. A tie-break rule is needed. **Returned to Arko as Q2.** Cases: TC-362.

**F-5 — a negative `authorized_amount` in storage crashes retrieval instead of reading as absent.**

`CaseVersionRecord` validates with `require_finite_decimal`, which permits negatives; `EvaluatedCandidate` uses `require_positive_or_zero`, which does not. Reproduced end to end: `-5000.00` is accepted on write, survives `from_body`, passes `search_cases`, then raises `ValidationError` inside `find_candidates`, where nothing catches it. `is_memory_unavailable()` returns `False` for it — correctly, since it is not a store outage — so both session scripts re-raise and the run dies in a traceback.

The direction of failure is safe: nothing is authorized. But `NEG-06` requires a malformed record to be "treated as absent," and both session scripts promise the screen shows a clean escalation while tracebacks go to stderr. Here the run dies instead. Cases: TC-275 and TC-300; TC-315 records the same asymmetry in `OwnerPolicySnapshot`, which is audit-only and not part of this failure chain.

**F-1 — `Proposal` does not validate `counterparty_risk_tier`.** Every other field is checked; this one is not. Reproduced: `Proposal(counterparty_risk_tier="low", ...)` constructs, and `compare()` then raises `AttributeError: 'str' object has no attribute 'not_worse_than'`. Fails loudly and in the safe direction — a robustness gap, not an authority defect. Cases: TC-076.

**F-3 — one malformed-config path does not surface as `ValidationError`.** Reproduced: `max_amount = "not-a-number"` raises `decimal.InvalidOperation` (`ConversionSyntax`) out of `load_owner_policy`, not the `ValidationError` every other malformed value produces. Config-time, fails closed, inconsistent with the module's stated contract. Cases: TC-129.

**F-4 — approved scope is checked per dimension, not per pairing. By design.**

Reproduction corrected after round 1, which rightly found the first draft's version misleading. `_in_approved_scope` admits `target_class="demo_receipt"` with `function="deposit"` — a pairing no corpus fixture uses — because each field is tested against its own allowlist. What happens next depends on the numeric path, and the first draft's `ALLOW` came from proposing `0.00`, not from the pairing:

```
amount 0.00,    no candidates -> allow    0.00 bound by current_action_scope
amount 1000.00, no candidates -> escalate 0    bound by learned_constraint
```

So the correct statement is narrow: the mismatched pairing PASSES THE SCOPE GATE. With an eligible precedent it would then be authorized on the numeric path like any in-scope proposal.

This is consistent with `ACTIVE_DEMO_DESIGN` section 1, which defines the ceiling as independent per-dimension lists, so it is **by design, not a defect**. It is recorded because `INV-2` — "the engine never introduces a contract or function absent from the ceiling" — holds per dimension, and a reader could reasonably expect it to hold per combination. If pairing ever needs to matter, that is a policy-model change with a decision record, not a code fix. Cases: TC-217.

**F-7 — `.env` values are not quote-stripped.** `KEY="value"` yields a value including the quotes. Harmless while `.env.example` shows them unquoted. Cases: TC-499.

**F-8 — the session scripts use different exit-code conventions for a refusal.** `session1.py` returns 1 when the engine blocks; `session2.py` returns 0 when nothing is authorized, treating a correct refusal as success. Both are defensible — Session 2's refusal IS the demonstration — but CI or a demo script treating non-zero as failure reads them inconsistently. **Returned to Arko as Q4.** Cases: TC-603.

---

# Open Questions

These four are decisions, not defects, and the catalogue cannot answer them. Each blocks the rows listed beside it, which are marked `UNRES` and must not be implemented until answered.

| Q | Question | Blocks | Recommendation |
| --- | --- | --- | --- |
| Q1 | Is `INV-5` meant to hold unconditionally, or only when `cold_start_autonomous_amount` is zero? If unconditionally, `derivation.py` needs `max(eligible)` clamped so a fallback can never exceed what a real precedent would have yielded. If conditionally, `SPEC-001` invariant 5 needs the condition written into it. | TC-183, TC-189, TC-190, TC-685 | State the condition in `SPEC-001`. The current wording is a stronger claim than the code makes, and the demo relies on the zero configuration anyway |
| Q2 | What is the tie-break when two authority events share a timestamp? | TC-362, TC-690 | Break ties by the transition matrix — prefer the ordering that forms a legal chain — or fail closed to `None` on any tie. Failing closed is more consistent with the rest of the fold |
| Q3 | Is `attempted=True, success=False, outcome_confirmed=True, tx_hash=""` coherent, or should an empty hash normalise to `None`? | TC-424, TC-425 | Reject empty on every path. "No reference" is `None`; an empty string is a value that looks like a reference and is not one |
| Q4 | Should the two session scripts share an exit-code convention? | TC-603 | Yes, and document it. A correct refusal is the demo working; both should exit 0, with non-zero reserved for a genuine failure |

Additionally, F-2, F-3 and F-5 are defects with an obvious fix rather than a decision, but each narrows or changes described behaviour, so they need a line in the audit trail either way — fixed, or accepted with a reason.

---

# Part I — Normative Cases

These carry acceptance-criterion or invariant weight. They are the cases worth implementing and maintaining.

## I.1 Acceptance-level scenarios — the demo and the organiser's gate

Every case in I.1.3 must run the sessions as **real subprocesses**. An import shares interpreter state and would prove nothing about a fresh process.

### I.1.1 `session1.py`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-580 | REQ | Seeded tenant without `CASE-001`, dry run | `session1.py` | Engine escalates at cold start; exit 0; the screen never shows a 25,000 allow | A1 | `test_session1_escalates_and_persists_authorization_without_a_premature_outcome` |
| TC-581 | REQ | Same | `session1.py` | `DV-001-V1` persisted with `authorized_amount == 10000.00`, an owner-policy snapshot, and a `draft -> active` chain — all written BEFORE any Base call | A2, INV-8 | `test_session1_escalates_and_persists_authorization_without_a_premature_outcome` |
| TC-582 | REQ | Same, dry run so nothing is attempted | `session1.py` | NO outcome record written — recording success with no transaction is the fabrication NEG-07 forbids | NEG-07 | `test_session1_escalates_and_persists_authorization_without_a_premature_outcome` |
| TC-583 | REQ | Same | `--owner-approved-amount 0` | Refuses, exit 1, nothing persisted — a zero approval authorizes nothing | A2 | GAP |
| TC-584 | REQ | Same | `--owner-approved-amount -100` | Refuses, exit 1 | A2 | GAP |
| TC-585 | REQ | Same | `--owner-approved-amount 30000` | Refuses, exit 1 — the owner cannot approve above their own ceiling | INV-1 | GAP |
| TC-586 | REQ | Same | `--owner-approved-amount 25000.00` (exactly the ceiling) | Accepted | INV-1 | GAP |
| TC-587 | REQ | Policy whose ceiling makes the proposal over-ceiling | `session1.py` | BLOCK path: warns, exit 1, nothing submitted or persisted | A9, NEG-04 | GAP |
| TC-588 | REQ | Store rigged so the engine returns ALLOW at cold start | `session1.py` | Refuses with "UNEXPECTED: cold start did not escalate", exit 1 | A1 | GAP |
| TC-589 | REQ | Memory raising a genuine outage | `session1.py` | Memory-failure frame on stdout, traceback on STDERR, exit 1, nothing persisted | NEG-01 | `test_neg_01_unavailable_memory_escalates_visibly_and_never_crashes` |
| TC-590 | REQ | Memory raising a caller defect | `session1.py` | Re-raised and visible as a crash — never displayed as a clean escalation | NEG-01 | `test_neg_01_classifier_separates_outages_from_defects_through_the_cause_chain` |
| TC-591 | REQ | Base confirming a revert | `session1.py` | Outcome FAILURE written with the real tx hash; exit 1; no false success | A12, NEG-07 | GAP |
| TC-592 | REQ | Base returning `outcome_confirmed=False` | `session1.py` | NO outcome written; the exact `reconcile_outcome.py` command printed to stderr with the decision id and tx hash; exit 1 | NEG-09 | GAP |
| TC-593 | REQ | Base confirming success | `session1.py` | Outcome SUCCESS written with the tx hash; exit 0 | A11 | `test_live_session1_then_session2_constrains_citing_precedent` (live, opt-in) |
| TC-594 | REQ | Any completed run | Process state | The process EXITS; no server, thread, or handle keeps it alive | A2, A3 | PARTIAL — `test_session1_escalates_and_persists_authorization_without_a_premature_outcome` runs it as a subprocess and reads its return code, but asserts nothing about lingering handles |
| TC-595 | REQ | Owner approval accepted | Inspect the submitted decision | `binding_constraint == "owner_manual_approval"`, distinct from anything the engine produces | A2 | GAP |
| TC-596 | REQ | Owner approval accepted | Inspect the engine's own decision afterwards | Unchanged and still escalating — `replace()` produced a new object rather than mutating | INV-1 | GAP |

### I.1.2 `session2.py`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-598 | REQ | Tenant where `DV-001-V1` is active with a recorded SUCCESS outcome | `session2.py` | CONSTRAIN to 10000.00 citing `DV-001-V1`; the canonical change line appears on screen | A4, A5 | `test_session2_constrains_and_cites_precedent_once_precedent_has_a_recorded_outcome` |
| TC-599 | REQ | Tenant where `DV-001-V1` is active but has NO recorded outcome | `session2.py` | Honestly escalates — derivation correctly requires a real outcome | NEG-06 | `test_session2_honestly_escalates_when_precedent_has_no_recorded_outcome` |
| TC-600 | REQ | `--no-memory` | `session2.py` | Points at a fresh `empty-<uuid4>` tenant, retrieves nothing, escalates, cannot execute | A6, INV-6 | `test_no_memory_control_escalates_and_cannot_execute` |
| TC-601 | REQ | `--no-memory` | Inspect the real demo tenant afterwards | Untouched — the control is non-destructive, which is what makes it repeatable on camera | A14 | GAP |
| TC-602 | REQ | Any escalating run | `session2.py` | NOTHING persisted for `CASE-002`, nothing submitted to Base | NEG-01 | `test_no_memory_control_escalates_and_cannot_execute` |
| TC-603 | UNRES | Any escalating run | Exit code | Currently 0, where `session1.py` returns 1 on BLOCK. **Blocked on Q4** — do not assert either convention until it is chosen | A6 | GAP |
| TC-604 | REQ | Constraining run | `session2.py` | `DV-002-V1` written with a SINGLE `None -> draft` event and no activation event | A4 | GAP |
| TC-605 | REQ | Constraining run | Inspect | An owner-policy snapshot is written for `DV-002-V1` | INV-8 | GAP |
| TC-606 | REQ | Over-ceiling proposal | `session2.py` | BLOCK displayed; nothing persisted | A9, NEG-04 | GAP |
| TC-607 | REQ | Memory outage | `session2.py` | Memory-failure frame, traceback to stderr, exit 1 | NEG-01 | `test_neg_01_unavailable_memory_escalates_visibly_and_never_crashes` |
| TC-608 | REQ | Any run | Source inspection | No owner-override path exists — Session 2 exists to prove autonomous behaviour | A4 | GAP |

### I.1.3 Cross-session — the load-bearing set

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-610 | REQ | Fresh database, reset run | `session1.py` then `session2.py` as SEPARATE subprocesses | Session 2 constrains 25,000 to 10,000 citing `DV-001-V1`, with no shared interpreter state | A3, A4, A5 | `test_session2_constrains_and_cites_precedent_once_precedent_has_a_recorded_outcome`; `test_live_session1_then_session2_constrains_citing_precedent` (live, opt-in) |
| TC-611 | REQ | Same | Inspect Session 2's environment | No environment variable, temp file, or in-process object carries the precedent — the only channel is Sibyl Memory | A3, INV-6 | GAP |
| TC-612 | REQ | After a successful pair | Empty the tenant, re-run `session2.py` | Escalates; derives zero; cannot execute. **The organiser's gate** | A6, INV-6 | `test_no_memory_control_escalates_and_cannot_execute` |
| TC-613 | REQ | After a successful pair | Delete ONLY the outcome record, re-run `session2.py` | Escalates — removing any single load-bearing read is enough. Proves the dependency is on the READS, not on the file existing | INV-6 | GAP |
| TC-614 | REQ | After a successful pair | Delete ONLY the authority events, re-run `session2.py` | Escalates — `fold_authority_state` returns `None`, so the candidate is not assembled at all | INV-6 | GAP |
| TC-615 | REQ | After a successful pair | Append a withdrawal event for `DV-001-V1`, re-run | Escalates; `DV-001-V1` still DISPLAYED as retrieved but not eligible | A7, NEG-02 | GAP |
| TC-616 | REQ | Reset state | `reset -> session1 -> session2` twice against two fresh database files | Byte-identical observable stdout both times | A14 | PARTIAL — `test_demo_resets_and_rehearses_repeatably` runs the sequence twice and asserts two substrings per run; it never compares the two runs' complete output, so drift outside those substrings would pass |
| TC-617 | REQ | Any run | Captured stdout | The screen never contains a traceback; tracebacks go to stderr only | NEG-01 | `test_neg_01_unavailable_memory_escalates_visibly_and_never_crashes` |
| TC-618 | REQ | Any run, with and without `ANTHROPIC_API_KEY` | Compare full stdout | Byte-identical | A10, NEG-05, INV-7 | `test_neg_05_authorization_is_identical_with_and_without_a_model` |

## I.2 The authority core

### I.2.1 Comparability

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-140 | REQ | None | Identical facts and risk tier | `is_comparable=True`, no differences | A4 | `test_identical_facts_are_comparable` |
| TC-141 | REQ | None | `network` differs | Not comparable; one difference on `network`, with `precedent_value` the CASE's and `current_value` the PROPOSAL's — asserted in that direction | NEG-03 | `test_network_mismatch_excludes` |
| TC-142 | REQ | None | `asset` differs | Not comparable; one difference on `asset` | NEG-03 | GAP |
| TC-143 | REQ | None | `action_class` differs | Not comparable; one difference on `action_class` | NEG-03 | GAP |
| TC-144 | REQ | None | `target_class` differs (the `CASE-005` shape) | Not comparable; one difference on `target_class` | A8, NEG-03 | `test_target_class_mismatch_excludes_case005_style` |
| TC-145 | REQ | None | `function` differs | Not comparable; one difference on `function` | NEG-03 | `test_function_mismatch_excludes` |
| TC-146 | REQ | None | All five dimensions differ | Exactly five differences, in declared order | NEG-03 | `test_multiple_material_differences_all_reported` |
| TC-147 | REQ | None | Current `high` vs precedent `low` | Not comparable; difference on `counterparty_risk_tier` | A8 | `test_riskier_current_proposal_excludes_safer_precedent` |
| TC-148 | REQ | None | Current `low` vs precedent `high` | **Comparable** — a successful high-risk case is at least as strong grounds for a lower-risk one. Directional by design | A8 | `test_safer_current_proposal_remains_comparable_to_riskier_precedent` |
| TC-149 | REQ | None | Current `medium` vs precedent `low` | Not comparable | A8 | GAP |
| TC-150 | REQ | None | Current `low` vs precedent `medium` | Comparable | A8 | GAP |
| TC-151 | REQ | None | Current `medium` vs precedent `high` | Comparable | A8 | GAP |
| TC-152 | REQ | None | Current `high` vs precedent `medium` | Not comparable | A8 | GAP |
| TC-153 | REQ | None | All 9 risk-tier ordered pairs, parametrised | Comparable exactly when `current.rank <= precedent.rank`; the four failing pairs each produce exactly one difference on `counterparty_risk_tier` | A8 | PARTIAL — `test_equal_risk_tier_is_comparable`, `test_riskier_current_proposal_excludes_safer_precedent` and `test_safer_current_proposal_remains_comparable_to_riskier_precedent` cover 3 of 9 |
| TC-154 | REQ | None | Identical facts, amounts differing by 15,000 | Comparable — amount is the value being constrained, never a dimension | A4 | GAP |
| TC-156 | REQ | None | `"base"` vs `"Base"` | Not comparable — matching is exact and case-sensitive, so casing drift fails closed | NEG-03 | GAP |
| TC-157 | REQ | None | `"deposit"` vs `"deposit "` | Not comparable — no normalisation | NEG-03 | GAP |
| TC-158 | REQ | None | One exact mismatch AND a risk-tier violation | Exactly two differences, exact dimension first | NEG-03 | GAP |
| TC-160 | REQ | None | `compare(p, c)` vs `compare(c, p)` with a risk-tier difference | NOT symmetric — asserts directionality is real, not an accident of argument order | A8 | GAP |

### I.2.2 Derivation

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-170 | REQ | `OP-001`, cold start 0.00 | No candidates | `0.00`, basis `cold_start`, no supporting ids | A1, A6, INV-6 | `test_empty_candidates_falls_back_to_cold_start` |
| TC-171 | REQ | Cold start 0.00 | One eligible at 10000.00 | `10000.00`, basis `precedent`, supporting `("DV-001-V1",)` | A4, A5 | `test_session2_constrains_and_cites_precedent_once_precedent_has_a_recorded_outcome` |
| TC-172 | REQ | Cold start 0.00 | Two eligible at 10000.00 and 5000.00 | `10000.00`; supporting names ONLY the 10000.00 case | A4 | GAP |
| TC-173 | REQ | Cold start 0.00 | Two eligible BOTH at 10000.00 | `10000.00`; supporting names BOTH ids | A5 | GAP |
| TC-174 | REQ | Cold start 0.00 | Eligible 10000.00 plus WITHDRAWN 20000.00 | `10000.00` — the `CASE-003` trap | A7, NEG-02, INV-4 | `test_withdrawn_precedent_never_raises_authority` |
| TC-175 | REQ | Cold start 0.00 | Eligible 10000.00 plus SUPERSEDED 15000.00 | `10000.00` | INV-4 | `test_full_active_demo_corpus_yields_documented_outcome` |
| TC-176 | REQ | Cold start 0.00 | Eligible 10000.00 plus QUESTIONED 12000.00 with FAILURE | `10000.00` | INV-4, NEG-06 | `test_full_active_demo_corpus_yields_documented_outcome` |
| TC-177 | REQ | Cold start 0.00 | Eligible 10000.00 plus DRAFT 18000.00 | `10000.00` | INV-4 | `test_full_active_demo_corpus_yields_documented_outcome` |
| TC-178 | REQ | Cold start 0.00 | Eligible 10000.00 plus non-comparable ACTIVE SUCCESS 10000.00 | `10000.00`, supporting names only the comparable case | A8, NEG-03 | `test_full_active_demo_corpus_yields_documented_outcome` |
| TC-179 | REQ | Cold start 0.00 | ACTIVE + SUCCESS but NOT comparable, only candidate | `0.00`, basis `cold_start` | A8, NEG-03 | GAP |
| TC-180 | REQ | Cold start 0.00 | Comparable + ACTIVE but FAILURE, only candidate | `0.00`, basis `cold_start` | NEG-06 | `test_neg_06_failed_outcome_never_authorizes` |
| TC-181 | REQ | Cold start 0.00 | Comparable + SUCCESS but each of DRAFT / QUESTIONED / SUPERSEDED / WITHDRAWN in turn | `0.00`, basis `cold_start`, for all four | A7, INV-4 | PARTIAL — `test_only_withdrawn_match_falls_back_to_cold_start` covers withdrawn only |
| TC-182 | REQ | Cold start `500.00` | No eligible candidates | `500.00` — the fallback reads the policy, it is not hardcoded zero | A1 | GAP |
| TC-183 | UNRES | Cold start `500.00` | One eligible at 100.00 | Currently `100.00` — a real precedent replaces the allowance even when LOWER. Whether that is correct depends on Q1; **blocked** | INV-5 | GAP |
| TC-184 | CHAR | Cold start 0.00 | Eligible candidate authorized `40000.00`, above the owner ceiling | Returns `40000.00` UNCLAMPED — derivation does not clamp, the engine's intersection does. Pins the division of responsibility | INV-1, INV-3 | GAP |
| TC-185 | REQ | Cold start 0.00 | Same candidate set in 5 orders | Identical `learned_max_amount`; supporting ids identical as a set | A10 | GAP |
| TC-186 | CHAR | Cold start 0.00 | Two eligible sharing one `decision_version_id` | Both ids appear if both are at the max — no deduplication | | GAP |
| TC-187 | DEFECT | Cold start 0.00 | One eligible authorized `0.00` | **Observed:** basis `precedent` with a non-empty supporting tuple and a ceiling of zero, which the engine then explains as "no active, comparable, successful precedent supports it" while citing one — see F-2. **Desired:** the explanation must not contradict the citation | | GAP |
| TC-189 | UNRES | Cold start 0.00 | Removing any candidate from an eligible set | Result never increases. **Holds only because cold start is zero; blocked on Q1** for the general statement | INV-5 | `test_fewer_candidates_never_widen_authority` (asserts the zero-cold-start case only) |
| TC-190 | UNRES | Cold start `500.00` | Removing an eligible candidate authorized `100.00` | Currently RAISES authority from 100.00 to 500.00, contradicting INV-5 as written — see F-9. **Blocked on Q1** | INV-5 | GAP |

### I.2.3 The engine

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-200 | REQ | `OP-001`, no candidates | Proposal 40000.00, in scope | BLOCK, amount `0`, binding `owner_permission_ceiling`, no citations | A9, NEG-04, INV-1 | `test_neg_04_above_ceiling_is_blocked_regardless_of_precedent` |
| TC-201 | REQ | One eligible precedent at 25000.00 | Proposal 40000.00 | BLOCK — precedent cannot lift the ceiling | A9, INV-1 | `test_neg_04_block_holds_even_with_many_supporting_precedents` |
| TC-202 | REQ | Twenty eligible precedents at 25000.00 | Proposal 40000.00 | BLOCK | A9, INV-1 | `test_neg_04_block_holds_even_with_many_supporting_precedents` |
| TC-203 | REQ | `OP-001` | Proposal exactly 25000.00 | NOT blocked — the ceiling is inclusive | INV-1 | PARTIAL — `test_above_ceiling_is_always_blocked` asserts the above-ceiling side; the at-ceiling boundary is asserted only via the demo path |
| TC-204 | REQ | `OP-001` | Proposal `25000.01` | BLOCK — the smallest representable step above the ceiling | INV-1 | GAP |
| TC-205 | REQ | `OP-001` | Proposal `25000.000001` | BLOCK — sub-cent excess is still excess | INV-1 | GAP |
| TC-206 | REQ | `OP-001`, no candidates | Proposal 40000.00 AND out of scope | BLOCK, not ESCALATE — the absolute result wins over the owner-resolvable one | A9, INV-1 | `test_out_of_scope_and_over_ceiling_blocks_not_escalates` |
| TC-207 | REQ | Candidates include two non-comparable cases | Proposal 40000.00 | BLOCK, and `material_differences` still carries both — a block still explains what else was wrong | NEG-03 | GAP |
| TC-208 | REQ | Ceiling `0.00` | Proposal 1.00 | BLOCK | INV-1 | GAP |
| TC-209 | CHAR | Ceiling `0.00` | Proposal 0.00, in scope | ALLOW at `0` — zero is within a zero ceiling. Degenerate corner, documented rather than left undefined | | GAP |
| TC-211 | REQ | `OP-001`, no candidates | In-ceiling proposal, `network="ethereum"` | ESCALATE, amount `0`, binding `current_action_scope`, no citations | NEG-03, INV-2 | `test_out_of_scope_network_is_never_authorized` |
| TC-212 | REQ | `OP-001` | `asset="DAI"` | ESCALATE, binding `current_action_scope` | INV-2 | GAP |
| TC-213 | REQ | `OP-001` | `action_class="treasury_rebalance"` | ESCALATE, binding `current_action_scope` | INV-2 | GAP |
| TC-214 | REQ | `OP-001` | `target_class="yield_vault_aggressive"` | ESCALATE, binding `current_action_scope` | INV-2 | GAP |
| TC-215 | REQ | `OP-001` | `function="withdraw"` | ESCALATE, binding `current_action_scope` | INV-2 | GAP |
| TC-216 | REQ | ONE eligible precedent at 10000.00 with identical facts | Proposal 10000.00 but `network="ethereum"` | ESCALATE with NO citation — out-of-scope never reaches derivation, so precedent cannot rescue it | INV-2 | GAP |
| TC-217 | CHAR | `OP-001`, one eligible precedent at 10000.00 | `target_class="demo_receipt"` with `function="deposit"`, amount 1000.00 | Passes the scope gate and is authorized on the numeric path — each field is checked against its own allowlist and the pairing is not validated. By design per `ACTIVE_DEMO_DESIGN` section 1; see F-4 | INV-2 | GAP |
| TC-218 | REQ | `OP-001` | All five scope fields wrong at once | ESCALATE; the explanation names all five values | NEG-03 | GAP |
| TC-221 | REQ | No-op hard policy, one eligible precedent at 10000.00 | Proposal 25000.00 | CONSTRAIN to `10000.00`, binding `learned_constraint`, citing `DV-001-V1` — **the demo's central assertion** | A4, A5 | `test_session2_constrains_and_cites_precedent_once_precedent_has_a_recorded_outcome` |
| TC-222 | REQ | Hard override `5000.00`, eligible precedent 10000.00 | Proposal 25000.00 | CONSTRAIN to `5000.00`, binding `current_hard_policy` | INV-3 | GAP |
| TC-223 | REQ | Hard override `40000.00`, eligible precedent 10000.00 | Proposal 25000.00 | CONSTRAIN to `10000.00` — an override above the ceiling is clamped down, never honoured upward | INV-3 | `test_hard_policy_override_cannot_exceed_owner_ceiling` |
| TC-225 | REQ | Hard override `0.00`, eligible precedent 10000.00 | Proposal 25000.00 | ESCALATE at `0`, binding `current_hard_policy`, explanation says a tighter current restriction reduced authority to zero EVEN THOUGH eligible precedent exists | | `test_zero_ceiling_from_hard_policy_blames_hard_policy_not_precedent` |
| TC-226 | REQ | No override, no candidates | Proposal 25000.00 | ESCALATE, binding `learned_constraint` | A1, A6, NEG-01 | `test_zero_ceiling_from_true_cold_start_blames_learned_constraint` |
| TC-227 | CHAR | Hard override equal to the learned ceiling (both `10000.00`) | Proposal 25000.00 | CONSTRAIN to `10000.00` reported as `learned_constraint` — the tie is resolved by testing the learned ceiling FIRST. Known, deliberate, and the seam (e) round-4 finding; pinned so it is not rediscovered | | GAP |
| TC-228 | REQ | Learned ceiling equal to the owner ceiling | Proposal 25000.00 | ALLOW — nothing narrowed, so the attribution branch is never reached | | GAP |
| TC-229 | REQ | Hard override `20000.00`, no eligible precedent | Proposal 25000.00 | ESCALATE at `0` bound by `learned_constraint` — the strictest ceiling wins the attribution | | GAP |
| TC-229b | DEFECT | One eligible precedent authorized `0.00` | Proposal 25000.00 | **Observed:** ESCALATE citing `DV-001-V1` while the explanation states no active, comparable, successful precedent supports it — a false statement beside a correct decision (F-2). **Desired:** when `learned.basis == "precedent"`, the explanation must not deny that a precedent exists | A5 | GAP |
| TC-230 | REQ | Eligible precedent 10000.00 | Proposal `9999.99` | ALLOW in full, binding `current_action_scope` | | GAP |
| TC-231 | REQ | Eligible precedent 10000.00 | Proposal exactly `10000.00` | ALLOW — equality is allowance, not constraint | | GAP |
| TC-232 | REQ | Eligible precedent 10000.00 | Proposal `10000.01` | CONSTRAIN to `10000.00` — the smallest step turning an allow into a constraint | A4 | GAP |
| TC-233 | CHAR | Eligible precedent 10000.00 | Proposal `0.00` | ALLOW at `0` with `cited_precedents == ("DV-001-V1",)` — an ALLOW carries supporting ids even though precedent did not bind. A citation on an ALLOW is not a claim of causation | | GAP |
| TC-234 | CHAR | No candidates, cold start 0.00 | Proposal `0.00` | ALLOW at `0`, NOT ESCALATE — a zero proposal is trivially within any ceiling | | GAP |
| TC-235 | REQ | Eligible precedent authorized 40000.00 | Proposal 25000.00 | ALLOW at 25000.00 and never above — a precedent recorded above the current ceiling cannot lift it | INV-1, INV-3 | GAP |
| TC-236 | REQ | Cold start `500.00`, no candidates | Proposal 25000.00 | CONSTRAIN to `500.00` — cold start is an allowance, not automatically zero | A1 | GAP |
| TC-237 | CHAR | Cold start `500.00`, no candidates | Proposal `400.00` | ALLOW at 400.00 with no citation — reachable WITHOUT any precedent. The counterfactual the seam (e) round-4 review turned on | A10 | GAP |
| TC-239 | REQ | Any BLOCK path | Inspect | `authorized_amount == 0` always | A9, INV-1 | GAP |
| TC-240 | REQ | Any ESCALATE path | Inspect | `authorized_amount == 0` always | A1, NEG-01 | GAP |
| TC-241 | REQ | Any CONSTRAIN path | Inspect | `0 < authorized_amount < proposal.amount` | A4 | GAP |
| TC-242 | REQ | Any ALLOW path | Inspect | `authorized_amount == proposal.amount` exactly, scale included | | GAP |
| TC-243 | REQ | Two non-comparable and one comparable candidate | Any in-scope path | `material_differences` aggregates the two non-comparable only | A8, NEG-03 | GAP |
| TC-245 | REQ | Matrix of policies, hard policies, candidate sets and proposals | Enumerate every returned `binding_constraint` | Only `owner_permission_ceiling`, `current_action_scope`, `current_hard_policy`, `learned_constraint` are reachable — asserted by enumeration so a new branch cannot introduce an unlabelled one | | GAP |
| TC-246 | REQ | Same enumeration | Collect every reachable `(result, binding_constraint, cited-or-not)` triple | The reachable set is stable and enumerated in the test itself. This is the shape seam (e) review demanded after a hand-written enumeration missed three reachable combinations | A10 | PARTIAL — `test_every_result_kind_renders` covers result kinds only, not the triple |
| TC-247 | REQ | Any path | Call twice with identical inputs | Byte-identical decision, explanation included | A10, INV-7 | GAP |
| TC-248 | REQ | Any path | Permute candidate order across 5 permutations | Identical result, amount and binding | A10 | GAP |
| TC-250 | REQ | Any path | Inspect every numeric value | Every amount is `Decimal`; no `float` anywhere in the returned object | INV-1 | GAP |
| TC-251 | REQ | CONSTRAIN with citation | Inspect `explanation` | Contains the proposed amount, authorized amount, binding constraint and cited ids | A5 | GAP |
| TC-253 | REQ | Full corpus (`CASE-001`, `003`–`008`) | Proposal 25000.00 baseline facts | CONSTRAIN to exactly `10000.00` citing `DV-001-V1`, with all four above-10,000 fixtures present and none raising the ceiling | A4, A5, A7, INV-4 | `test_full_active_demo_corpus_yields_documented_outcome` |

### I.2.4 Eligibility and retrieval

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-090 | REQ | Comparable, ACTIVE, SUCCESS | `is_eligible()` | True — the ONLY eligible combination | A4, INV-4 | `test_finds_a_fully_confirmed_active_case` |
| TC-091 | REQ | Comparable, DRAFT, SUCCESS | `is_eligible()` | False | A7, INV-4 | PARTIAL — `test_draft_case_is_still_retrieved_and_displayable` asserts retrieval and state, not the eligibility call |
| TC-092 | REQ | Comparable, QUESTIONED, SUCCESS | `is_eligible()` | False | INV-4 | GAP |
| TC-093 | REQ | Comparable, SUPERSEDED, SUCCESS | `is_eligible()` | False | INV-4 | GAP |
| TC-094 | REQ | Comparable, WITHDRAWN, SUCCESS | `is_eligible()` | False | A7, NEG-02, INV-4 | `test_withdrawn_precedent_never_raises_authority` |
| TC-095 | REQ | Comparable, ACTIVE, FAILURE | `is_eligible()` | False | NEG-06 | `test_neg_06_failed_outcome_never_authorizes` |
| TC-096 | REQ | NOT comparable, ACTIVE, SUCCESS | `is_eligible()` | False | A8, NEG-03 | `test_neg_03_material_difference_is_never_silently_followed` |
| TC-097 | REQ | All 20 combinations of (comparable) x (5 states) x (2 outcomes), parametrised | `is_eligible()` | True for exactly ONE and False for nineteen — asserted by enumeration, so a new `AuthorityState` member fails this test instead of silently becoming eligible | INV-4 | GAP |
| TC-260 | REQ | Case with a folded state and a recorded outcome | `find_candidates` | One `EvaluatedCandidate` with the record's amount, folded state, recorded outcome, and comparability computed against the CASE's facts | A4 | `test_finds_a_fully_confirmed_active_case` |
| TC-261 | REQ | Case with events but NO outcome | `find_candidates` | Excluded entirely — absent, not ineligible | NEG-06 | `test_excludes_case_with_no_recorded_outcome` |
| TC-262 | REQ | Case with an outcome but NO events | `find_candidates` | Excluded entirely | NEG-06 | `test_excludes_case_with_no_confirmed_authority_state` |
| TC-263 | REQ | WITHDRAWN case | `find_candidates` | Returned, with `authority_state == WITHDRAWN` — retrievable and displayable | A7, NEG-02 | `test_withdrawn_case_is_still_retrieved_and_displayable` |
| TC-264 | REQ | DRAFT case | `find_candidates` | Returned | INV-4 | `test_draft_case_is_still_retrieved_and_displayable` |
| TC-265 | REQ | SUPERSEDED case | `find_candidates` | Returned | INV-4 | GAP |
| TC-266 | REQ | QUESTIONED case | `find_candidates` | Returned | INV-4 | GAP |
| TC-267 | REQ | `target_class`-mismatched case | `find_candidates` | Returned with `is_comparable == False` and the difference stated | A8, NEG-03 | `test_material_difference_case_is_still_retrieved` |
| TC-268 | REQ | Empty tenant | `find_candidates` | `[]`, no exception | A6, NEG-01, INV-6 | `test_no_candidates_on_empty_memory` |
| TC-274 | REQ | Store raising a genuine outage | `find_candidates` | Exception PROPAGATES — retrieval must not swallow it, so a failed read is never mistaken for an empty corpus | NEG-01 | `test_neg_01_unreadable_memory_is_absence_not_permission` |
| TC-275 | DEFECT | Store holding a case whose `authorized_amount` is negative (admitted at write; see TC-300) | `find_candidates` | **Observed:** raises `ValidationError` out of `find_candidates`; `is_memory_unavailable` returns False; both sessions re-raise and die in a traceback. **Desired:** the record is treated as absent, per NEG-06, and the screen shows a clean escalation. See F-5 | NEG-06 | GAP |

## I.3 Memory integrity

### I.3.1 The authority transition matrix

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-319 | REQ | None | `(None -> draft)` | Constructs | A2, INV-4 | INDIRECT — constructed as setup in `reset_demo.py` and several tests; no test asserts its legality |
| TC-320 | REQ | None | `(draft -> active)` | Constructs | A2, INV-4 | INDIRECT — same |
| TC-321 | REQ | None | `(draft -> withdrawn)` | Constructs | INV-4 | GAP |
| TC-322 | REQ | None | `(active -> questioned)` | Constructs | INV-4 | INDIRECT — seeded for `CASE-007`; legality never asserted |
| TC-323 | REQ | None | `(active -> superseded)` | Constructs | INV-4 | INDIRECT — seeded for `CASE-006` |
| TC-324 | REQ | None | `(active -> withdrawn)` | Constructs | A7 | INDIRECT — seeded for `CASE-003` |
| TC-325 | REQ | None | `(questioned -> active)` | Constructs — the only path back to authorizing | INV-4 | GAP |
| TC-326 | REQ | None | `(questioned -> superseded)` | Constructs | INV-4 | GAP |
| TC-327 | REQ | None | `(questioned -> withdrawn)` | Constructs | INV-4 | GAP |
| TC-328 | REQ | None | `(None -> active)` | `ValidationError` — a case cannot be born active, so a single forged event can never mint authority | INV-4 | `test_no_prior_state_to_active_is_unconstructable` |
| TC-329 | REQ | None | `(withdrawn -> active)` | `ValidationError` — withdrawn is terminal | A7, INV-4 | `test_withdrawn_to_active_is_unconstructable` |
| TC-330 | REQ | None | `(superseded -> X)` for all five targets | `ValidationError` for all five | INV-4 | `test_superseded_has_no_legal_outgoing_transition` |
| TC-331 | REQ | None | All 30 `(previous, new)` pairs over `{None} + 5 states` x `5 states`, parametrised | Exactly the 9 legal pairs construct; the other 21 raise. Enumerated so a future matrix edit cannot quietly add a path | INV-4 | PARTIAL — `test_no_prior_state_to_active_is_unconstructable`, `test_withdrawn_to_active_is_unconstructable` and `test_superseded_has_no_legal_outgoing_transition` cover 7 of the 21 illegal pairs and none of the 9 legal ones |
| TC-337 | REQ | None | `from_extra` with an illegal transition pair in the stored payload | `ValidationError` — deserialisation cannot reconstruct an event live code could not create; direct storage tampering is caught here | NEG-06, INV-4 | GAP — round 1 found the previously cited test (`test_fold_discards_the_whole_chain_at_a_break_not_just_the_tail`) uses a LEGAL event pair with cross-event inconsistency, which is TC-370, not this case |

### I.3.2 Authority folding

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-357 | REQ | No events | Fold | `None` — never a default state | INV-4 | `test_fold_with_no_events_returns_none` |
| TC-358 | REQ | One `(None -> draft)` | Fold | `DRAFT` | INV-4 | `test_fold_after_single_event` |
| TC-359 | REQ | `(None -> draft)`, `(draft -> active)` | Fold | `ACTIVE` | A2, INV-4 | `test_fold_after_draft_then_active_returns_active` |
| TC-361 | REQ | Events written out of chronological order | Fold | Ordered by `ts`, not write order | INV-4 | `test_fold_orders_by_timestamp_not_write_order` |
| TC-362 | UNRES | Two events sharing the SAME `ts` | Fold | **Observed:** `ACTIVE` or `None` depending on the order the journal search returned — see F-6. **Blocked on Q2**; do not assert either outcome until a tie-break rule exists | INV-4 | GAP |
| TC-363 | REQ | Events for another decision version present | Fold | Only this decision's events are folded | INV-4 | `test_fold_excludes_events_for_a_different_decision_version` |
| TC-364 | REQ | Journal holds non-authority entries | Fold | Skipped as irrelevant | | `test_fold_excludes_non_authority_journal_entries` |
| TC-365 | REQ | Journal entry with a non-dict body | Fold | Skipped, no crash | NEG-06 | `test_non_dict_journal_body_does_not_crash_the_fold` |
| TC-366 | REQ | Journal entry with a dict body but a non-dict `extra` | Fold | Skipped | NEG-06 | GAP |
| TC-367 | REQ | Journal entry with `kind` absent or wrong | Fold | Skipped | | GAP |
| TC-368 | REQ | Entry whose `extra.decision_version_id` differs despite matching the FTS5 query | Fold | Skipped — the exact id is verified rather than trusting the search hit | INV-4 | `test_fold_excludes_events_for_a_different_decision_version` |
| TC-369 | REQ | An entry that IS for this decision but fails to deserialise | Fold | `None` for the WHOLE chain, plus a logged integrity warning — relevant-and-invalid is evidence the history cannot be trusted | NEG-06 | `test_fold_fails_closed_on_a_malformed_authority_event` |
| TC-370 | REQ | Valid `draft -> active` chain then an event claiming `previous_status=draft` | Fold | `None` — cross-event inconsistency discards the whole chain, not just the tail | NEG-06, INV-4 | `test_fold_discards_the_whole_chain_at_a_break_not_just_the_tail` |
| TC-371 | REQ | Inconsistency in the middle of a chain | Fold | `None`; the valid prefix is discarded too | NEG-06 | `test_fold_stops_at_first_chain_inconsistency` |
| TC-372 | REQ | An illegal transition reaching the fold despite the record-level guard | Fold | `None` — defence in depth against schema change or tampering | INV-4 | `test_neg_06_illegal_transition_event_fails_the_whole_chain_closed` |
| TC-373 | REQ | Corrupt chain for `DV-A`, valid chain for `DV-B` | Fold both | `DV-A` -> `None`; `DV-B` still folds correctly | NEG-06 | `test_neg_06_an_invalid_event_for_another_decision_is_still_just_absent` |
| TC-374 | REQ | A corrupt chain | Fold, capturing logs | A WARNING naming the decision version and the conflict | NEG-06 | `test_neg_06_contradictory_chain_is_surfaced_not_silent` |
| TC-375 | REQ | Journal search returning exactly 2000 results | Fold | `None` — at or above the cap the true count is unknown, so it fails safe | NEG-06 | `test_journal_search_truncation_is_detected_and_fails_safe` |
| TC-376 | REQ | Journal search returning 1999 results | Fold | Folds normally — the boundary is `>=` and one below must still work | | GAP |

### I.3.3 `is_memory_unavailable` — outage versus defect

Every case here needs a real instance. All Sibyl exceptions take a `message`; `TierGateError` also requires keyword-only `feature`.

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-379 | REQ | None | `StorageError("db down")` | True | NEG-01 | `test_neg_01_classifier_separates_outages_from_defects_through_the_cause_chain` |
| TC-380 | REQ | None | `TenantError("t")`, `TierGateError("t", feature="x")`, `TierVerificationError("t")`, `SchemaError("t")` | True for all four | NEG-01 | PARTIAL — the cited test covers `StorageError` only |
| TC-381 | REQ | None | `OSError()` | True | NEG-01 | GAP |
| TC-382 | REQ | None | `sqlite3.OperationalError()` | True | NEG-01 | GAP |
| TC-383 | REQ | None | `sqlite3.DatabaseError("file is not a database")` | True — a structurally corrupt file is an outage | NEG-01 | GAP |
| TC-384 | REQ | None | `MemoryTruncationError()`, `AuthorityChainCorruptionError()` | True for both | NEG-01 | GAP |
| TC-385 | REQ | None | `sqlite3.ProgrammingError()` | False — SQL misuse is a caller defect and must stay visible | NEG-01 | `test_neg_01_classifier_separates_outages_from_defects_through_the_cause_chain` |
| TC-386 | REQ | None | `sqlite3.IntegrityError()` | False — a write-once violation is INV-8 working. It is a SUBCLASS of `DatabaseError`, so this asserts the defect check runs first | INV-8 | GAP |
| TC-387 | REQ | None | `TypeError()`, `AttributeError()`, `NameError()`, Sibyl `ValidationError("m")`, `ConflictError("m")` | False for all five | NEG-01 | PARTIAL — the cited test covers `ProgrammingError` and one wrapped defect, not these five |
| TC-388 | REQ | None | `StorageError("m")` raised `from` a `ProgrammingError` | False — a defect anywhere in the chain disqualifies the whole exception | NEG-01 | `test_neg_01_classifier_separates_outages_from_defects_through_the_cause_chain` |
| TC-389 | REQ | None | `StorageError` with an `OSError` CAUSE and a hidden `TypeError` CONTEXT | False — the exact case a `__cause__`-only walk misclassified | NEG-01 | `test_neg_01_classifier_separates_outages_from_defects_through_the_cause_chain` |
| TC-390 | REQ | None | `TypeError` with a `StorageError` cause (defect outermost) | False | NEG-01 | GAP |
| TC-391 | REQ | None | A five-link chain with the defect deepest | False | NEG-01 | GAP |
| TC-392 | REQ | None | An exception whose `__cause__` cycles back to itself | Terminates and returns a verdict | | GAP |
| TC-393 | REQ | None | Two exceptions referencing each other through `__context__` | Terminates | | GAP |
| TC-394 | REQ | None | `ValueError()` in neither list | False — unclassified means visible, not silently escalated | NEG-01 | GAP |
| TC-395 | REQ | None | `KeyboardInterrupt()` | False — never displayed as a memory outage | | GAP |

### I.3.4 Write-once enforcement

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-341 | REQ | Case already written | Same id, DIFFERENT content | `IntegrityError`; the stored record unchanged on re-read | INV-8 | `test_case_version_is_write_once` |
| TC-342 | REQ | Case already written | Same id, IDENTICAL content | `IntegrityError` — write-once is about the key, not the payload | INV-8 | GAP |
| TC-347 | REQ | Outcome already written | Second write, different outcome | `IntegrityError`; the first stands. This is why NEG-09 refuses to write a FAILURE on a timeout | NEG-09, INV-8 | `test_outcome_is_write_once` |
| TC-350 | REQ | Snapshot already written | Second write | `IntegrityError` | INV-8 | `test_owner_policy_snapshot_is_write_once` |
| TC-354 | REQ | Empty store | Two threads writing the same case id | Exactly one succeeds; the other raises `IntegrityError` | INV-8 | `test_concurrent_writers_in_one_process_do_not_double_write` |
| TC-377 | REQ | Two tenants on one database file | Write to one, read from the other | Isolated; nothing leaks | A6 | `test_tenants_are_isolated_on_a_shared_database_file` |

## I.4 Base evidence

### I.4.1 `BaseExecutionResult` shapes

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-410 | REQ | None | `attempted=False, success=False, outcome_confirmed=True, tx_hash=None` | Constructs — the unattempted shape | NEG-07 | `test_result_allows_every_coherent_shape` |
| TC-411 | REQ | None | `True, True, True, "0x..."` | Constructs — confirmed success | A11 | `test_result_allows_every_coherent_shape` |
| TC-412 | REQ | None | `True, False, True, None` | Constructs — pre-broadcast rejection with no hash | NEG-07 | `test_result_allows_every_coherent_shape` |
| TC-413 | REQ | None | `True, False, True, "0x..."` | Constructs — confirmed revert | NEG-07 | `test_result_allows_every_coherent_shape` |
| TC-414 | REQ | None | `True, False, False, "0x..."` | Constructs — unknown outcome | NEG-09 | `test_result_allows_every_coherent_shape` |
| TC-415 | REQ | None | `attempted=False, success=True` | `ValueError` | A12, NEG-07 | `test_result_rejects_unattempted_success` |
| TC-416 | REQ | None | `attempted=False` with a `tx_hash` | `ValueError` — the fabricated-reference guard | A12, NEG-07 | `test_result_rejects_unattempted_with_tx_hash` |
| TC-417 | REQ | None | `attempted=False, outcome_confirmed=False` | `ValueError` | NEG-09 | `test_result_rejects_unattempted_with_unconfirmed_outcome` |
| TC-418 | REQ | None | `outcome_confirmed=False, success=True` | `ValueError` | NEG-09 | `test_result_rejects_success_with_unconfirmed_outcome` |
| TC-419 | REQ | None | `attempted=True, outcome_confirmed=False, tx_hash=None` | `ValueError` | NEG-09 | `test_result_rejects_attempted_unconfirmed_without_tx_hash` |
| TC-420 | REQ | None | `success=True, tx_hash=None` | `ValueError` | A12, NEG-07 | `test_result_rejects_success_without_tx_hash` |
| TC-421 | REQ | None | `success=True, tx_hash=""` | `ValueError` — empty is not a reference | A12, NEG-07 | `test_result_rejects_success_with_empty_tx_hash` |
| TC-422 | REQ | None | `attempted="yes"` | `ValueError` naming the type — checks are `isinstance`, not truthiness | NEG-07 | `test_result_rejects_non_bool_attempted` |
| TC-423 | REQ | None | `success="yes"`, `outcome_confirmed=1`, `tx_hash=123` | `ValueError` for each | NEG-07 | `test_result_rejects_non_bool_success`, `..._outcome_confirmed`, `..._non_str_tx_hash` |
| TC-424 | UNRES | None | Exhaustive construction over `{T,F}^3 x {None, "0xabc", ""}` | **Observed:** SIX shapes construct, not five — `True, False, True, ""` also succeeds, because empty `tx_hash` is rejected only on the success path (F-10). **Blocked on Q3** before this is asserted either way | NEG-07, NEG-09 | PARTIAL — `test_result_allows_every_coherent_shape` enumerates five; the sixth is unasserted in either direction |
| TC-425 | UNRES | None | `attempted=True, success=False, outcome_confirmed=True, tx_hash=""` | **Blocked on Q3.** If empty normalises to `None`, this must raise; if it is coherent, it belongs in TC-424's enumeration | NEG-07 | GAP |

### I.4.2 `record_authorization`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-449 | REQ | `FINNE_BASE_DRY_RUN=1` | Any decision | `attempted=False`; no network call at all, asserted with a fake that raises if touched | A14 | `test_dry_run_skips_everything` |
| TC-450 | REQ | Decision authorizing `0` | `record_authorization` | `attempted=False`; no connection attempted | NEG-07 | `test_refuses_when_decision_authorizes_nothing` |
| TC-451 | REQ | Decision authorizing a 7dp amount | `record_authorization` | `attempted=False`, refused BEFORE connecting | INV-1 | `test_refuses_amount_not_exactly_representable_before_connecting` |
| TC-452 | REQ | RPC unreachable | `record_authorization` | `attempted=False, outcome_confirmed=True, tx_hash=None` | A12, NEG-07 | `test_connection_failure_is_unattempted_not_a_false_failure` |
| TC-453 | REQ | `recorded()` call raises | `record_authorization` | `attempted=False` | A12, NEG-07 | `test_read_failure_before_submitting_is_unattempted` |
| TC-454 | REQ | Contract reports `recorded=True` | `record_authorization` | `attempted=False`, detail cites NEG-08; nothing submitted | A13, NEG-08 | `test_refuses_duplicate_without_submitting` |
| TC-455 | REQ | Signing raises | `record_authorization` | `attempted=True, success=False, outcome_confirmed=True, tx_hash=None` — nothing pending, so a confirmed failure | A12, NEG-07 | `test_pre_broadcast_signing_failure_is_a_confirmed_failure` |
| TC-456 | REQ | `send_raw_transaction` raises | `record_authorization` | `attempted=True, outcome_confirmed=False`, hash present — the node may already have accepted it | NEG-09 | `test_ambiguous_broadcast_failure_is_unconfirmed_and_reconcilable` |
| TC-457 | REQ | Broadcast accepted, receipt wait fails | `record_authorization` | `attempted=True, outcome_confirmed=False`, hash present, detail names `reconcile_outcome.py` | NEG-09 | `test_timeout_is_unconfirmed_not_a_false_success_or_false_failure` |
| TC-458 | REQ | Receipt `status=0` | `record_authorization` | `attempted=True, success=False, outcome_confirmed=True`, hash present | A12, NEG-07 | `test_revert_produces_no_false_success` |
| TC-459 | REQ | Receipt `status=1` | `record_authorization` | `attempted=True, success=True, outcome_confirmed=True`, hash present | A11 | `test_successful_submission` |
| TC-460 | REQ | Any submission path | Inspect the built transaction | No `value` key, or `value == 0` | INV-10 | `test_transaction_never_carries_value` |
| TC-461 | REQ | Decision authorizing `10000.00` | Inspect the call args | `authorizedAmount == 10000000000`, `decisionId == keccak(id)`, `factsHash` as computed | A11 | `test_authorized_amount_submitted_in_six_decimal_units` |

### I.4.3 `reconcile_pending` and receipts

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-478 | REQ | Node does not know the hash | `reconcile_pending` | `outcome_confirmed=False` | NEG-09 | `test_reconcile_pending_unknown_transaction_is_unconfirmed` |
| TC-479 | REQ | Malformed hash | `reconcile_pending` | `ReconciliationMismatch` raised, NOT a result | NEG-09 | `test_reconcile_pending_malformed_hash_raises_mismatch` |
| TC-480 | REQ | Transaction to another contract | `reconcile_pending` | `ReconciliationMismatch` | NEG-07 | `test_reconcile_pending_raises_for_transaction_to_a_different_contract` |
| TC-481 | REQ | Transaction from another sender | `reconcile_pending` | `ReconciliationMismatch` | NEG-07 | `test_reconcile_pending_raises_for_transaction_from_a_different_sender` |
| TC-482 | REQ | Transaction calling a different function | `reconcile_pending` | `ReconciliationMismatch` | NEG-07 | `test_reconcile_pending_raises_for_a_different_function` |
| TC-483 | REQ | Transaction with a different `decisionId` | `reconcile_pending` | `ReconciliationMismatch` — binding verified from CALLDATA, because a reverted transaction emits no events | NEG-07 | `test_reconcile_pending_raises_for_a_different_decision` |
| TC-484 | REQ | Undecodable calldata | `reconcile_pending` | `ReconciliationMismatch` | NEG-07 | GAP |
| TC-485 | REQ | Bound transaction, unmined | `reconcile_pending` | `outcome_confirmed=False` | NEG-09 | `test_reconcile_pending_broadcast_but_unmined_is_unconfirmed` |
| TC-486 | REQ | Bound transaction, `status=0` | `reconcile_pending` | `success=False, outcome_confirmed=True`, and only after binding | A12, NEG-07 | `test_reconcile_pending_confirms_revert_only_after_binding` |
| TC-487 | REQ | Bound transaction, `status=1` | `reconcile_pending` | `success=True, outcome_confirmed=True` | A11 | `test_reconcile_pending_confirms_success` |
| TC-488 | REQ | Connection failure | `reconcile_pending` | `outcome_confirmed=False` result, not a mismatch — an outage is not an operator error | NEG-09 | GAP |
| TC-471 | REQ | Recorded by a DIFFERENT address | `get_receipt` | `None` — provenance verification, so a third party's receipt is never reported as this project's evidence | A13, NEG-08 | `test_get_receipt_rejects_provenance_mismatch` |
| TC-470 | REQ | Recorded, no log found within the scan bound | `get_receipt` | `None` — never a receipt without a reference | A12, NEG-07 | `test_get_receipt_returns_none_if_recorded_but_no_log_found` |
| TC-468 | REQ | Connection failure | `get_receipt` | `None` — a query failure is not evidence of absence | A12, NEG-07 | `test_get_receipt_returns_none_on_connection_failure` |
| TC-641 | REQ | Transaction that cannot be bound | `reconcile_outcome.py` | Refuses; exit 1; **writes nothing**. An earlier version wrote a fabricated `Outcome.FAILURE` here | A12, NEG-07, NEG-09 | GAP |
| TC-642 | REQ | Transaction still pending | `reconcile_outcome.py` | "Still unresolved", exit 1, nothing written | NEG-09 | GAP |
| TC-643 | REQ | Confirmed reverted and bound | `reconcile_outcome.py` | Writes FAILURE with the hash; exit 0 | NEG-07 | GAP |
| TC-644 | REQ | Confirmed successful and bound | `reconcile_outcome.py` | Writes SUCCESS with the hash; exit 0 | A11 | GAP |
| TC-645 | REQ | Reconciled once | Run again | Reports the existing outcome; no second write | INV-8 | `test_reconcile_outcome_is_idempotent_when_already_recorded` |

### I.4.4 The contract

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-500 | REQ | Fresh deployment | `recordAuthorization` from the deployer | Succeeds; `recorded[decisionId]` becomes true | A11 | `test_live_record_and_read_back_a_real_receipt` (live, opt-in) |
| TC-501 | REQ | Already recorded | Same call again | Reverts `already recorded` — the contract-level half of NEG-08 | A13, NEG-08 | `test_live_duplicate_rejected_at_contract_level_too` (live, opt-in) |
| TC-502 | REQ | Fresh deployment | Call from a non-deployer | Reverts `not the authorized signer` — without this, any third party could preempt a predictable `decisionId` | A13, NEG-08 | `test_live_contract_rejects_an_unauthorized_signer` (live, opt-in) |
| TC-503 | REQ | Recorded receipt | `getReceipt` | Returns the stored fields | A11 | `test_live_record_and_read_back_a_real_receipt` (live, opt-in) |
| TC-504 | REQ | Unknown decisionId | `getReceipt` | All-zero fields — the zero value must not be mistaken for a receipt | NEG-07 | GAP |
| TC-506 | REQ | Any call | Send with non-zero `msg.value` | Reverts — zero value enforced by the contract, not only the caller | INV-10 | GAP |
| TC-507 | REQ | Fresh deployment | Read `authorizedSigner` | Equals the deploying address; immutable | A13 | GAP |
| TC-509 | REQ | Contract source | Inspect | No `payable`, no balance-holding function, no token transfer | INV-10 | GAP |

## I.5 Explanation, key material, and module boundaries

### I.5.1 `explain()`

After the seam (e) round-4 removal, `explain()` is exactly `deterministic_explanation()`. A10 and NEG-05 are true by construction, so these cases are mostly STRUCTURAL — they assert the absence of a mechanism, which is the only kind of assertion that keeps it absent.

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-520 | REQ | Any decision | `deterministic_explanation` twice | Byte-identical | A10, INV-7 | `test_deterministic_explanation_is_pure_and_repeatable` |
| TC-521 | REQ | CONSTRAIN citing `DV-001-V1` | `deterministic_explanation` | Contains result, authorized amount, binding constraint, cited id | A5 | `test_deterministic_explanation_states_result_amount_and_citation` |
| TC-522 | REQ | Decision with no citations | `deterministic_explanation` | Says "none — no eligible precedent supported this proposal" explicitly | A1, NEG-01 | `test_deterministic_explanation_names_absence_of_precedent_explicitly` |
| TC-523 | REQ | Decision carrying material differences | `deterministic_explanation` | Each difference rendered with dimension, precedent value, current value | A8, NEG-03 | `test_deterministic_explanation_states_material_differences` |
| TC-524 | REQ | Decision citing `DV-001-V1` AND carrying differences from other candidates | `deterministic_explanation` | The differences are LABELLED as belonging to other candidates, and the label appears BEFORE them — unlabelled they read as if the cited precedent were mismatched, on the frame the demo exists to show | A5 | `test_material_differences_are_labelled_as_other_candidates` |
| TC-525 | REQ | One decision of each result kind | `deterministic_explanation` | All four render without `KeyError` | | `test_every_result_kind_renders` |
| TC-526 | REQ | Any decision | `explain(d) == deterministic_explanation(d)` | Equal for every decision in an enumerated set | A10, NEG-05 | `test_explain_is_exactly_the_deterministic_explanation` |
| TC-527 | REQ | `ANTHROPIC_API_KEY` set | `explain(d)` | Identical to the same call with no key | A10, NEG-05, INV-7 | `test_explain_without_api_key_is_exactly_the_deterministic_explanation`, `test_explain_ignores_the_environment_entirely` |
| TC-528 | REQ | A fake `anthropic` module in `sys.modules` | `explain(d)` | No client constructed; the fake records zero calls | A10, NEG-05 | `test_explain_never_constructs_a_model_client` |
| TC-529 | REQ | Module source | Static scan | Imports nothing outside `__future__` and `finne`; no SDK, no `os`, no network, no file I/O | A10, INV-7 | `test_no_model_sdk_is_reachable_from_this_module`, `test_the_module_does_not_read_or_write_anything` |
| TC-531 | REQ | A new `AuthorizationResult` member in a fixture | `deterministic_explanation` | Fails loudly rather than rendering an unlabelled result | | GAP |

### I.5.2 Key material (`INV-9`)

Round 1 found the first draft's key-material cases unimplementable and overclaiming. They are restated here with a mechanism.

**Method for this subsection.** Set `FINNE_BASE_PRIVATE_KEY` to a known sentinel value (a syntactically valid throwaway key never used elsewhere) and `BASE_RPC_URL` to `https://sentinel-host.example/v2/SENTINEL_RPC_TOKEN`. Run the flow. Then search each artifact for the sentinel substrings. The artifact boundary is explicit, because one artifact legitimately contains the key.

| Artifact | Must the sentinel key be absent? |
| --- | --- |
| Process stdout and stderr | Yes |
| The Sibyl Memory database file | Yes |
| `config/base_deployment.json` | Yes |
| Any file written under the repository except `.env` | Yes |
| Git-tracked files | Yes |
| `.env` | **No.** `.env` intentionally stores it. `finne/base/env.py` says so explicitly, and "never persisted anywhere" would overclaim. What is asserted about `.env` is that it is gitignored and mode `0600` |

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-619 | REQ | Sentinel key and sentinel RPC token set | Full `reset -> session1 -> session2` run | The sentinel key appears in no artifact in the table above marked Yes | INV-9 | GAP |
| TC-620 | REQ | Same | Inspect `.env` | Present in `.gitignore`; file mode is `0600` | INV-9 | GAP |
| TC-621 | REQ | Same | `git ls-files` and the tracked contents | The sentinel appears in no tracked file | INV-9 | GAP |
| TC-441 | REQ | None | `_redact_rpc_url("https://host/v2/SENTINEL_RPC_TOKEN")` | Path replaced by `/[redacted]`; the token appears nowhere in the output | INV-9 | GAP |
| TC-442 | REQ | None | `_redact_rpc_url("https://user:SENTINEL@host/path")` | User-info stripped — returning `netloc` alone would have preserved the credential, which an earlier version did | INV-9 | GAP |
| TC-443 | REQ | None | `_redact_rpc_url("https://host:8545/path")` | Port preserved, path redacted | | GAP |
| TC-444 | REQ | None | `_redact_rpc_url("not a url")` | `[unparseable-host]`, no exception | | GAP |
| TC-445 | REQ | RPC reporting chain id 1, deployment recording 84532 | `_connect()` | `RuntimeError` refusing to sign for the wrong network | INV-9 | GAP |
| TC-446 | REQ | RPC unreachable, sentinel token in the URL | `_connect()` | The raised `RuntimeError` message contains the REDACTED url and not the token | INV-9 | GAP |
| TC-464 | REQ | Each `except Exception as exc` path in `record_authorization`, with an injected exception whose message CONTAINS the sentinel RPC token | Inspect `BaseExecutionResult.detail` | **Enumerate the paths rather than assert a blanket property.** `_redact_rpc_url` is applied only in `_connect` and `deploy_contract`; every other path interpolates `{exc}` verbatim, so a library exception carrying the URL would pass through. This case exists to establish WHICH paths leak, not to claim none do. Any path that leaks is a finding to raise, not a test to make pass | INV-9 | GAP |

### I.5.3 Module boundaries

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-660 | REQ | Repository source | AST scan | Only `finne/memory/client.py` imports `sibyl_memory_client` | | `test_only_memory_client_imports_sibyl_memory_client` |
| TC-661 | REQ | Repository source | AST scan | Only modules under `finne/base/` import `web3`, `eth_account`, or `solcx` | INV-9 | `test_only_finne_base_imports_key_material_libraries` |
| TC-662 | REQ | Repository source | AST scan | Only `finne/explain.py` may import a model SDK; it currently imports none | A10 | `test_only_explain_imports_a_model_sdk` |
| TC-663 | REQ | Repository source | Transitive import-graph walk | `finne/explain.py` has no import PATH to `finne.base` — the transitive closure, not just direct imports | INV-9 | `test_explain_has_no_import_path_to_finne_base` |
| TC-664 | REQ | Repository source | AST scan | No `importlib`, `__import__`, or dynamic import in application code. The test states plainly that aliasing `getattr` or assembling a name from fragments stays invisible to a static check, and that review is the final enforcement layer | | `test_application_code_uses_no_dynamic_imports` |
| TC-665 | REQ | `finne/authority/` source | AST scan | No import of `finne.memory` or `finne.base` from any module in the package — the engine's purity is what makes the invariants provable rather than trusted | INV-7 | GAP |
| TC-666 | REQ | `finne/authority/` source | AST scan | No `float(` call and no float literal in the authority path | INV-1 | GAP |
| TC-667 | REQ | Repository source | AST scan | No `os.environ` read outside `finne/base/env.py`, `finne/base/adapter.py`, `finne/cli.py` | A10, INV-9 | GAP |
| TC-668 | REQ | Repository source | Scan for a write to `config/owner_policy.toml` | No hit — the agent cannot rewrite its own authority policy | INV-2 | GAP |

## I.6 Property sweeps

`hypothesis` is already a dev dependency. Each row names its strategy so the test is reproducible rather than vaguely "fuzzed".

| TC | Class | Strategy | Property | Traces | Coverage |
| --- | --- | --- | --- | --- | --- |
| TC-680 | REQ | `OwnerPolicy` x `HardPolicy` x candidate lists x `Proposal`; amounts drawn as `Decimal` with 0–8 decimal places, including zero, ceiling-adjacent, and far above | `authorized_amount <= owner_policy.max_amount` on every generated input | INV-1 | `test_authorized_amount_never_exceeds_owner_ceiling` |
| TC-681 | REQ | Same | `BLOCK` or `ESCALATE` implies `authorized_amount == 0` | INV-1 | GAP |
| TC-682 | REQ | Same | **Restated after round 1**, which found the original compares fields `AuthorizationDecision` does not have: any decision with `authorized_amount > 0` implies the PROPOSAL matched every owner-approved scope dimension — `network`, `asset` and `action_class` equal, `target_class` and `function` in their allowlists | INV-2 | PARTIAL — `test_out_of_scope_network_is_never_authorized` covers one dimension by example |
| TC-683 | REQ | Hard-policy overrides drawn across and above the owner ceiling | The effective ceiling is never above `min(owner ceiling, override)` | INV-3 | `test_hard_policy_override_cannot_exceed_owner_ceiling` |
| TC-684 | REQ | Candidate sets over all 5 states x 2 outcomes | Adding a non-`active` candidate never raises `authorized_amount` versus the same set without it | INV-4 | PARTIAL — `test_withdrawn_precedent_never_raises_authority` covers withdrawn by example |
| TC-685 | UNRES | Random subsets of a candidate set, with `cold_start_autonomous_amount` drawn across zero AND non-zero | The subset's `authorized_amount` is never greater than the full set's. **This property is FALSE for non-zero cold start — see F-9. Blocked on Q1**; until then it may only be asserted with cold start pinned at zero | INV-5 | PARTIAL — `test_fewer_candidates_never_widen_authority` asserts it with cold start zero, which is the case that holds |
| TC-686 | REQ | Generated decisions across every reachable result kind | `explain(d) == deterministic_explanation(d)`, with and without an API key | INV-7, A10 | `test_neg_05_authorization_is_identical_with_and_without_a_model` |
| TC-687 | REQ | Generated strings including control characters, combining marks, bidi overrides, and the escape delimiter | `_clean` is injective: distinct inputs never share an output | A5 | GAP |
| TC-688 | REQ | Generated exception chains mixing defect and outage types across `__cause__` and `__context__`, including cycles | `is_memory_unavailable` returns False whenever any defect appears anywhere in the chain, and terminates on every input | NEG-01 | GAP |
| TC-689 | REQ | Generated `(previous, new)` state pairs | `AuthorityEventRecord` constructs exactly when the pair is in `LEGAL_TRANSITIONS` | INV-4 | GAP |
| TC-690 | UNRES | Generated event sequences, valid and corrupted, including duplicate timestamps | The fold returns a state only when the whole chain is consistent. **The duplicate-timestamp subset is blocked on Q2**; the rest is assertable now | INV-4, NEG-06 | GAP |
| TC-691 | REQ | Generated `Decimal` amounts with 0–6 decimal places, then 7+ | Round-trips exactly at 6 or fewer; always raises at 7+ rather than rounding | INV-1 | GAP |
| TC-692 | REQ | Every generated failure mode across the system | No path authorizes more than the ceiling | INV-1 | `test_invariant_7_no_failure_mode_authorizes_more_than_the_ceiling` |
---

# Traceability

These matrices are GENERATED from the case rows above and below, not written by hand. A case appears here only if its own row carries the trace, so the mapping is earned in both directions. Round 1 found the hand-written version listed cases that did not carry the trace and claimed one criterion (`A12`) that no row carried at all.

## Acceptance criteria

| # | Statement | Cases | Covered | Blocked |
| --- | --- | --- | --- | --- |
| A1 | Session 1 escalates rather than silently authorizing 25,000 at cold start | TC-104, TC-109, TC-170, TC-182, TC-226, TC-236, TC-240, TC-522, TC-559, TC-580, TC-588 | 4 of 11 | — |
| A2 | Session 1 persists the complete case and exits fully | TC-116, TC-296, TC-319, TC-320, TC-340, TC-359, TC-581, TC-583, TC-584, TC-594, TC-595 | 4 of 11 | — |
| A3 | Session 2 is a fresh process with no carried-over in-process state | TC-594, TC-610, TC-611 | 1 of 3 | — |
| A4 | Session 2 changes 25,000 proposed to 10,000 authorized | TC-090, TC-140, TC-154, TC-171, TC-172, TC-221, TC-232, TC-241, TC-253, TC-260, TC-397, TC-558, TC-566, TC-568, +4 more | 11 of 18 | — |
| A5 | The change names DV-001-V1 as the binding precedent on screen | TC-103, TC-171, TC-173, TC-221, TC-251, TC-253, TC-430, TC-521, TC-524, TC-544, TC-558, TC-566, TC-598, TC-610, +2 more | 11 of 16 | — |
| A6 | With the tenant emptied, Session 2 escalates and cannot execute | TC-170, TC-226, TC-268, TC-377, TC-560, TC-600, TC-603, TC-612 | 6 of 8 | TC-603 |
| A7 | CASE-003 (withdrawn) is displayed but never raises authority to 20,000 | TC-091, TC-094, TC-174, TC-181, TC-253, TC-263, TC-324, TC-329, TC-403, TC-561, TC-615, TC-631, TC-632 | 5 of 13 | — |
| A8 | A materially different proposal is not silently followed | TC-081, TC-082, TC-096, TC-144, TC-147, TC-148, TC-149, TC-150, TC-151, TC-152, TC-153, TC-160, TC-178, TC-179, +3 more | 7 of 17 | — |
| A9 | A 40,000 request is blocked regardless of precedent | TC-108, TC-200, TC-201, TC-202, TC-206, TC-239, TC-587, TC-606 | 4 of 8 | — |
| A10 | Results are identical with no model API key present | TC-136, TC-185, TC-237, TC-246, TC-247, TC-248, TC-520, TC-526, TC-527, TC-528, TC-529, TC-618, TC-662, TC-667, +1 more | 8 of 15 | — |
| A11 | A Base transaction executes within the bound and its hash is persisted | TC-307, TC-346, TC-411, TC-428, TC-429, TC-430, TC-432, TC-433, TC-435, TC-459, TC-461, TC-487, TC-500, TC-503, +2 more | 12 of 16 | — |
| A12 | Base failure produces no false success and no fabricated reference | TC-108, TC-415, TC-416, TC-420, TC-421, TC-452, TC-453, TC-455, TC-458, TC-468, TC-470, TC-486, TC-591, TC-641 | 11 of 14 | — |
| A13 | Duplicate execution is rejected at both application and contract level | TC-426, TC-454, TC-471, TC-501, TC-502, TC-507 | 5 of 6 | — |
| A14 | The demo resets to a known state and rehearses repeatably | TC-402, TC-449, TC-555, TC-601, TC-616, TC-630, TC-631, TC-633, TC-634, TC-635, TC-636, TC-637 | 5 of 12 | — |

## Invariants

| # | Statement | Cases | Covered | Blocked |
| --- | --- | --- | --- | --- |
| INV-1 | authorized_amount <= owner_policy.max_amount, always | TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-011, TC-012, TC-042, TC-043, TC-045, +44 more | 22 of 58 | — |
| INV-2 | The engine never introduces a network, asset, contract, protocol, function, or action class absent from the ceiling | TC-054, TC-055, TC-122, TC-130, TC-131, TC-211, TC-212, TC-213, TC-214, TC-215, TC-216, TC-217, TC-668, TC-682 | 1 of 14 | — |
| INV-3 | Intersection can only narrow | TC-048, TC-066, TC-133, TC-184, TC-222, TC-223, TC-235, TC-683 | 2 of 8 | — |
| INV-4 | A non-active precedent can never raise authority | TC-035, TC-036, TC-090, TC-091, TC-092, TC-093, TC-094, TC-097, TC-174, TC-175, TC-176, TC-177, TC-181, TC-253, +29 more | 20 of 43 | TC-362, TC-690 |
| INV-5 | A retrieval miss can only narrow authority, never widen it | TC-183, TC-189, TC-190, TC-685 | 1 of 4 | TC-183, TC-189, TC-190, TC-685 |
| INV-6 | Removing the load-bearing memory reads makes autonomous execution impossible | TC-170, TC-268, TC-600, TC-611, TC-612, TC-613, TC-614 | 4 of 7 | — |
| INV-7 | Authorization results are identical with and without a model API key | TC-247, TC-520, TC-527, TC-529, TC-618, TC-665, TC-686 | 5 of 7 | — |
| INV-8 | An immutable record is never overwritten | TC-280, TC-296, TC-307, TC-314, TC-333, TC-334, TC-340, TC-341, TC-342, TC-346, TC-347, TC-349, TC-350, TC-354, +7 more | 15 of 21 | — |
| INV-9 | No key material reaches Sibyl Memory, logs, or the repository | TC-441, TC-442, TC-445, TC-446, TC-464, TC-494, TC-496, TC-619, TC-620, TC-621, TC-647, TC-661, TC-663, TC-667 | 3 of 14 | — |
| INV-10 | Every demonstration transaction carries zero value | TC-460, TC-506, TC-509 | 1 of 3 | — |

## Negative cases

| ID | Statement | Cases | Covered | Blocked |
| --- | --- | --- | --- | --- |
| NEG-01 | Memory absent, empty, or unauthenticated | TC-109, TC-226, TC-240, TC-268, TC-274, TC-379, TC-380, TC-381, TC-382, TC-383, TC-384, TC-385, TC-387, TC-388, +13 more | 14 of 27 | — |
| NEG-02 | Only CASE-003 (withdrawn) matches | TC-094, TC-174, TC-263, TC-615 | 3 of 4 | — |
| NEG-03 | Proposal materially different from every active case | TC-056, TC-082, TC-085, TC-096, TC-141, TC-142, TC-143, TC-144, TC-145, TC-146, TC-156, TC-157, TC-158, TC-178, +7 more | 9 of 21 | — |
| NEG-04 | Proposal above the owner ceiling | TC-108, TC-200, TC-587, TC-606 | 1 of 4 | — |
| NEG-05 | No model API key, or malformed model output | TC-526, TC-527, TC-528, TC-618 | 4 of 4 | — |
| NEG-06 | Malformed or contradictory memory record | TC-088, TC-095, TC-176, TC-180, TC-261, TC-262, TC-275, TC-281, TC-282, TC-284, TC-285, TC-286, TC-292, TC-294, +24 more | 25 of 38 | TC-690 |
| NEG-07 | Base reverts or is rejected before broadcast | TC-308, TC-309, TC-410, TC-412, TC-413, TC-415, TC-416, TC-420, TC-421, TC-422, TC-423, TC-424, TC-425, TC-450, +17 more | 22 of 31 | TC-424, TC-425 |
| NEG-08 | The same authorized action executed twice | TC-454, TC-471, TC-501, TC-502 | 4 of 4 | — |
| NEG-09 | Broadcast but the receipt wait times out or errors | TC-037, TC-311, TC-347, TC-414, TC-417, TC-418, TC-419, TC-424, TC-456, TC-457, TC-478, TC-479, TC-485, TC-488, +4 more | 11 of 18 | TC-424 |

---

# Coverage Summary

Re-audited after round 1, which found the first draft's column unreliable in both directions. Only a row naming a test that actually asserts the case counts as covered; `PARTIAL` and `INDIRECT` do not.

| | Count |
| --- | --- |
| Total cases | 479 |
| Covered — a named test asserts the case | 205 |
| PARTIAL — a named test reaches it but does not assert all of it | 17 |
| INDIRECT — exercised only as setup, never asserted | 5 |
| GAP — no test found | 252 |

| Class | Count | Implementable now? |
| --- | --- | --- |
| `REQ` | 430 | Yes |
| `CHAR` | 32 | Yes, with a docstring saying it pins current behaviour |
| `DEFECT` | 8 | No — fix or formally accept the defect first |
| `UNRES` | 9 | No — blocked on an open question |

So 17 of 479 cases must NOT be implemented as written. That number is the point of the Class column: without it, every one of them would have been written as a passing test asserting behaviour this document simultaneously recommends changing.

The gap count is not alarming on its own. A large share are single rows inside a matrix whose interesting members are covered — the eligibility truth table (TC-097), the 30-pair transition matrix (TC-331), the 9-pair risk-tier table (TC-153) and the result-shape matrix (TC-424) each collapse into one parametrised test that would close 15 to 25 rows at once.
---

# Recommendations

Ordered by risk to the event gate, not by effort. Items 1 and 2 are decisions; the rest are work.

1. **Answer Q1 (`INV-5`).** `SPEC-001` currently states an invariant the code does not satisfy for a legal configuration. Whichever way it is resolved — condition the invariant, or clamp the derivation — the specification and the code should agree before either is used as evidence. Nine cases are blocked on this and the three other open questions.
2. **Decide F-2, F-3 and F-5.** Each is a defect with an obvious fix rather than a decision, but each changes described behaviour, so each needs a line in the audit trail: fixed, or accepted with a reason. F-2 matters most — it is a false statement rendered beside a correct decision, the exact failure class four rounds of seam (e) review were spent eliminating, reappearing in the engine's own explanation string where nobody thought to look.
3. **Close the single-read deletion cases (TC-613, TC-614).** Today's control empties the whole tenant. Removing only the outcome record, or only the authority events, proves the dependency is on the load-bearing READS rather than on the database file existing. This is the strongest available evidence for the organiser's gate and neither case exists.
4. **Implement the key-material sweep (TC-619, TC-620, TC-621) with the sentinel method.** `INV-9` is the weakest-covered invariant. The method in I.5.2 makes it implementable, including the honest exclusion of `.env`, which intentionally holds the key.
5. **Add the four parametrised matrices (TC-097, TC-153, TC-331, TC-424).** Four tests close roughly 60 rows and, more importantly, each fails loudly when a future change adds an enum member or a result shape. A hand-written enumeration only ever lists what its author already thought of — which is how the seam (e) round-2 defect survived, and how this document's own first draft missed the sixth result shape.
6. **Enumerate the exception paths in TC-464 before claiming anything about them.** `_redact_rpc_url` is applied in two places; every other failure path interpolates `{exc}` verbatim. Whether that leaks depends on what the underlying library puts in its message, which is a question to answer rather than a property to assert.
7. **Consider adding `coverage` as a dev extra.** It would replace this document's inspection-based column with measurement for the question "was this line executed." Round 1 is right that it proves less than the first draft implied: line coverage cannot establish that a test actually asserts the behaviour a row describes, which is precisely the error it found in five rows here. It supplements judgement; it does not replace it. It is also a dependency change requiring a decision record under `DECISION-023`.
8. **Add the contract-level zero-value case (TC-506).** `INV-10` is proven at the caller today. Asserting the contract itself reverts on non-zero `msg.value` proves it at the boundary that enforces it.

---

# Part II — Appendix: Behaviour Inventory

**This part is NOT authoritative.** It is a field-by-field record of how the code currently behaves, useful as a worklist and for onboarding. Treat it as observations, not as a contract: a row here being `CHAR` does not make the behaviour a requirement, and a change that contradicts one of these rows is not thereby a regression.

The exception is rows marked `REQ`. Those carry a real invariant and remain binding wherever they appear.

## II.1 `finne/models.py`

### II.1.1 Validation helpers

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | REQ | None | `require_finite_decimal("x", Decimal("1.00"))` | Returns None | INV-1 | GAP |
| TC-002 | REQ | None | `require_finite_decimal("x", 1.0)` | `ValidationError` naming `float` | INV-1 | `test_proposal_amount_rejects_non_finite_decimal` |
| TC-003 | REQ | None | Same with `1` (int) | `ValidationError` naming `int` | INV-1 | GAP |
| TC-004 | REQ | None | Same with `"1.00"` | `ValidationError` naming `str` | INV-1 | GAP |
| TC-005 | REQ | None | Same with `None` | `ValidationError` naming `NoneType` | INV-1 | GAP |
| TC-006 | REQ | None | `Decimal("NaN")` | `ValidationError` "must be finite", NOT `decimal.InvalidOperation` | INV-1 | `test_decimal_nan_raises_validation_error_not_invalid_operation` |
| TC-007 | REQ | None | `Decimal("Infinity")` | `ValidationError` "must be finite" | INV-1 | GAP |
| TC-008 | REQ | None | `Decimal("-Infinity")` | `ValidationError` "must be finite" | INV-1 | GAP |
| TC-009 | REQ | None | `Decimal("sNaN")` | `ValidationError`; no `InvalidOperation` escapes | INV-1 | GAP |
| TC-010 | REQ | None | `require_positive_or_zero("x", Decimal("0"))` | Returns None | | GAP |
| TC-011 | REQ | None | `Decimal("-0.01")` | `ValidationError` ">= 0" | INV-1 | GAP |
| TC-012 | REQ | None | `Decimal("NaN")` | `ValidationError` "must be finite", raised BEFORE the `< 0` comparison | INV-1 | `test_decimal_nan_raises_validation_error_not_invalid_operation` |
| TC-013 | REQ | None | `require_nonempty("x", "")` | `ValidationError` | | GAP |
| TC-014 | REQ | None | `"   "` | `ValidationError` | | GAP |
| TC-016 | REQ | None | `5` (non-str) | `ValidationError` naming `int` | | GAP |
| TC-018 | CHAR | None | `" a "` | Returns None — the interior value is checked, not stripped | | GAP |

### II.1.2 `RiskTier` and enums

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-020 | CHAR | None | `.rank` for the three members | 0, 1, 2 | | GAP |
| TC-022 | REQ | None | `RiskTier("critical")` | `ValueError` | | GAP |
| TC-023 | REQ | None | `RiskTier("LOW")` | `ValueError` — values are case-sensitive | | GAP |
| TC-033 | REQ | None | All 9 ordered pairs of `not_worse_than`, parametrised | Equals `self.rank <= other.rank` for every pair | | GAP |
| TC-035 | REQ | None | `AuthorityState` members | Exactly the five documented states | INV-4 | GAP |
| TC-036 | REQ | None | `AuthorityState("archived")` | `ValueError` — no undocumented state is constructible | INV-4 | GAP |
| TC-037 | CHAR | None | `Outcome` members | Exactly `success`, `failure`. There is deliberately no `pending`; pending is the ABSENCE of an `OutcomeRecord` | NEG-09 | GAP |
| TC-038 | CHAR | None | `AuthorizationResult` members | Exactly `allow`, `constrain`, `block`, `escalate` | | GAP |
| TC-039 | CHAR | None | Enum is a `str` subclass | `AuthorityState.ACTIVE == "active"` — serialisation depends on it | | GAP |

### II.1.3 `OwnerPolicy`, `HardPolicy`, `Proposal`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-042 | REQ | None | `max_amount=Decimal("NaN")` | `ValidationError` | INV-1 | `test_owner_policy_max_amount_rejects_non_finite_decimal` |
| TC-043 | REQ | None | `max_amount=Decimal("-1.00")` | `ValidationError` ">= 0" | INV-1 | GAP |
| TC-045 | CHAR | None | `max_amount=Decimal("0.00")` | Constructs — a zero ceiling is legal and means "authorize nothing" | INV-1 | GAP |
| TC-046 | REQ | None | `cold_start_autonomous_amount=Decimal("NaN")` | `ValidationError` | INV-1 | `test_owner_policy_cold_start_autonomous_amount_rejects_non_finite_decimal` |
| TC-048 | REQ | `max_amount=25000.00` | `cold_start=Decimal("25000.01")` | `ValidationError` "cannot exceed max_amount" | INV-1, INV-3 | GAP |
| TC-049 | REQ | `max_amount=25000.00` | `cold_start=Decimal("25000.00")` | Constructs — equal is not "exceeds" | INV-1 | GAP |
| TC-050 | REQ | None | `network=""`, `asset=""`, `action_class=""`, one each | `ValidationError` for each | | GAP |
| TC-054 | REQ | None | `approved_target_classes=()` | `ValidationError` — an empty allowlist must not silently mean "allow everything" | INV-2 | GAP |
| TC-055 | REQ | None | `approved_functions=()` | `ValidationError` | INV-2 | GAP |
| TC-056 | REQ | None | `unknown_situation_behaviour="allow"` | `ValidationError` — the only accepted value is `escalate_to_owner`, so an unknown situation can never be configured to allow | NEG-03 | GAP |
| TC-058 | REQ | Constructed policy | Attribute assignment | `FrozenInstanceError` — the ceiling cannot be mutated after construction | INV-1 | GAP |
| TC-060 | CHAR | None | `schema_version=2` passed explicitly | Constructs — the model does not police its own version; `finne.memory.schema` does, on read | | GAP |
| TC-062 | CHAR | None | `HardPolicy()` | `max_amount_override is None` — the documented no-op | | `test_hard_policy_none_override_is_still_valid` |
| TC-063 | REQ | None | `max_amount_override=Decimal("NaN")` | `ValidationError` | INV-1 | `test_hard_policy_override_rejects_non_finite_decimal` |
| TC-066 | CHAR | None | `max_amount_override=Decimal("999999999")` | Constructs — clamping is the ENGINE's job; asserting rejection here would encode the wrong boundary | INV-3 | GAP |
| TC-069 | REQ | None | `Proposal(amount=Decimal("NaN"))` | `ValidationError` | INV-1 | `test_proposal_amount_rejects_non_finite_decimal` |
| TC-070 | REQ | None | `amount=Decimal("-1.00")` | `ValidationError` ">= 0" | INV-1 | GAP |
| TC-073 | REQ | None | Each of the five string dimensions empty, one per case | `ValidationError` for each | | GAP |
| TC-074 | REQ | None | `proposed_at=""` | `ValidationError` | | GAP |
| TC-075 | CHAR | None | `proposed_at="not-a-timestamp"` | Constructs — provenance-only and deliberately not parsed. Pins the decision so a future "validate ISO-8601" change is deliberate | | GAP |
| TC-076 | DEFECT | None | `counterparty_risk_tier="low"` (raw string) | **Observed:** constructs, and `compare()` later raises `AttributeError: 'str' object has no attribute 'not_worse_than'` (F-1). **Desired:** `ValidationError` at construction, like every other field | | GAP |
| TC-078 | CHAR | None | `amount=Decimal("0.000001")` and `Decimal("0.0000001")` | Both construct — 6-decimal representability is enforced at the Base boundary, not here | | GAP |

### II.1.4 Comparability, candidate, constraint, decision models

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-081 | REQ | None | `Comparability(is_comparable=True, material_differences=(d,))` | `ValidationError` — a comparable candidate cannot carry differences | A8 | GAP |
| TC-082 | REQ | None | `Comparability(is_comparable=False)` with no differences | `ValidationError` — a non-comparable candidate must state a reason | A8, NEG-03 | GAP |
| TC-085 | REQ | None | Two `MaterialDifference` with swapped precedent/current | Not equal — direction is part of a difference's identity | NEG-03 | GAP |
| TC-087 | REQ | None | `EvaluatedCandidate(decision_version_id="")` | `ValidationError` | | GAP |
| TC-088 | REQ | None | `authorized_amount=Decimal("-1")` | `ValidationError` ">= 0" — note this is STRICTER than `CaseVersionRecord`, which is the F-5 asymmetry | INV-1, NEG-06 | GAP |
| TC-089 | REQ | None | `authorized_amount=Decimal("NaN")` | `ValidationError` | INV-1 | `test_evaluated_candidate_authorized_amount_rejects_non_finite_decimal` |
| TC-098 | DEFECT | Comparable, ACTIVE, SUCCESS, `authorized_amount=Decimal("0.00")` | `is_eligible()` | **Observed:** True, producing a precedent-basis constraint of zero that the engine then explains as "no precedent supports it" while citing it (F-2). **Desired:** either such a precedent is ineligible, or the explanation stops contradicting the citation | | GAP |
| TC-103 | REQ | None | `LearnedConstraint(basis="precedent")` with no supporting ids | `ValidationError` — a precedent-basis constraint must name what it rests on | A5 | GAP |
| TC-104 | REQ | None | `basis="cold_start"` WITH supporting ids | `ValidationError` — a cold start rests on nothing and must not appear to cite | A1 | GAP |
| TC-105 | REQ | None | `basis="learned"` | `ValidationError` "unrecognized basis" | | GAP |
| TC-106 | REQ | None | `learned_max_amount=Decimal("NaN")` | `ValidationError` | INV-1 | `test_learned_constraint_rejects_non_finite_decimal` |
| TC-108 | REQ | None | `AuthorizationDecision(result=BLOCK, authorized_amount=Decimal("1"))` | `ValidationError` — a block that authorizes anything is unrepresentable | A9, A12, NEG-04, INV-1 | GAP |
| TC-109 | REQ | None | `result=ESCALATE, authorized_amount=Decimal("0.01")` | `ValidationError` | A1, NEG-01 | GAP |
| TC-112 | REQ | None | `authorized_amount=Decimal("NaN")` | `ValidationError` | INV-1 | `test_authorization_decision_authorized_amount_rejects_non_finite_decimal` |
| TC-115 | REQ | Constructed decision | Attribute assignment on any field | `FrozenInstanceError` — a decision cannot be edited after the engine returns it | INV-1 | GAP |
| TC-116 | REQ | Constructed decision | `dataclasses.replace(...)` as `session1.py` does | Returns a new decision; the engine's original is unchanged | A2 | GAP |

## II.2 `finne/policy.py`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-120 | REQ | Real config | `load_owner_policy()` | `max_amount == Decimal("25000.00")` and `cold_start == Decimal("0.00")`, compared with `==` AND `str()` so scale is asserted | INV-1 | `test_real_config_file_loads_with_exact_decimal_values` |
| TC-122 | REQ | Real config | Inspect | `approved_target_classes` is a TUPLE, not a list — the model is frozen and a list would be mutable through the reference | INV-2 | GAP |
| TC-125 | REQ | Temp TOML, quoted amount | `load_owner_policy(path)` | Loads exactly | INV-1 | `test_quoted_string_amounts_load_as_exact_decimal` |
| TC-126 | REQ | Temp TOML, `max_amount = 25000.0` | `load_owner_policy(path)` | `ValidationError` naming `float` and explaining precision corruption | INV-1 | `test_unquoted_numeric_max_amount_is_rejected` |
| TC-127 | REQ | Temp TOML, `max_amount = 25000` | `load_owner_policy(path)` | `ValidationError` naming `int` | INV-1 | GAP |
| TC-128 | REQ | Temp TOML, unquoted cold start | `load_owner_policy(path)` | `ValidationError` | INV-1 | `test_unquoted_cold_start_amount_is_rejected` |
| TC-129 | DEFECT | Temp TOML, `max_amount = "not-a-number"` | `load_owner_policy(path)` | **Observed:** `decimal.InvalidOperation` (`ConversionSyntax`) propagates, not the `ValidationError` every other malformed value produces (F-3). **Desired:** `ValidationError` naming the field | | GAP |
| TC-130 | REQ | Temp TOML with no `[owner_policy]` section | `load_owner_policy(path)` | `KeyError` — loud, not a defaulted empty policy | INV-2 | GAP |
| TC-131 | REQ | Temp TOML missing `approved_functions` | `load_owner_policy(path)` | `KeyError` — a missing allowlist never defaults to permissive | INV-2 | GAP |
| TC-133 | REQ | Temp TOML, cold start above `max_amount` | `load_owner_policy(path)` | `ValidationError` — the file cannot configure a cold start above the ceiling | INV-1, INV-3 | GAP |
| TC-134 | CHAR | None | `default_hard_policy()` | `HardPolicy(max_amount_override=None)` | | GAP |
| TC-136 | REQ | Real config | `load_owner_policy() == load_owner_policy()` | Equal — loading is deterministic and has no hidden state | A10 | GAP |

## II.3 `finne/memory/schema.py`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-280 | REQ | None | `_require_current_schema_version({"schema_version": 1})` | Returns None | INV-8 | GAP |
| TC-281 | REQ | None | Body with no `schema_version` | `ValidationError` — missing is rejected, never defaulted | NEG-06 | `test_missing_schema_version_reads_as_none` |
| TC-282 | REQ | None | `schema_version: 2` | `ValidationError` — a future schema is not read as the current one | NEG-06 | `test_wrong_schema_version_reads_as_none` |
| TC-284 | REQ | None | `schema_version: "1"` (string) | `ValidationError` — the comparison is type-strict | NEG-06 | GAP |
| TC-285 | REQ | None | Body is a list | `ValidationError` "must be a dict", NOT `AttributeError` | NEG-06 | `test_non_dict_stored_body_reads_as_none_not_crash` |
| TC-286 | REQ | None | Body is a string, an int, `None`, one case each | `ValidationError` for each | NEG-06 | PARTIAL — the cited test covers one non-dict shape |
| TC-289 | REQ | None | `_decimal_or_raise("x", 10000.0)` | `ValidationError` — a raw float must never become a Decimal by binary approximation | INV-1 | GAP |
| TC-292 | REQ | None | `_decimal_or_raise("x", "abc")` | `ValidationError` "not a valid decimal", raised from `InvalidOperation` | NEG-06 | GAP |
| TC-294 | REQ | None | `"NaN"`, `"Infinity"`, `"-Infinity"` | `ValidationError` "must be finite" for each — these ARE parseable Decimals, so the finiteness check is what stands between a stored `Infinity` and an unbounded comparison | INV-1, NEG-06 | GAP |
| TC-296 | REQ | Valid record | `from_body(to_body(r))` | Equal, including `Decimal` scale and every fact field | A2, INV-8 | `test_case_version_round_trips_exactly` |
| TC-298 | REQ | None | `facts` given as a dict rather than a `Proposal` | `ValidationError` "must be a Proposal" | | GAP |
| TC-300 | DEFECT | None | `CaseVersionRecord(authorized_amount=Decimal("-1.00"))` | **Observed:** constructs and round-trips, because this record uses `require_finite_decimal` while `EvaluatedCandidate` uses `require_positive_or_zero`. The record then crashes retrieval (F-5, TC-275). **Desired:** `ValidationError` at write, so the asymmetry cannot arise | NEG-06 | GAP |
| TC-301 | REQ | Stored body missing `facts` but WITH a valid `schema_version` | `from_body` | `KeyError`, caught by the caller and surfaced as absent | NEG-06 | GAP — round 1 found the previously cited test uses a body with no `schema_version`, so it fails at the version gate and never reaches the missing-`facts` path |
| TC-302 | REQ | Stored body with `facts` missing `function` | `from_body` | `ValidationError` "malformed matter facts" | NEG-06 | GAP |
| TC-303 | REQ | Stored body with `counterparty_risk_tier: "extreme"` | `from_body` | `ValidationError` | NEG-06 | GAP |
| TC-304 | CHAR | Stored body with extra unknown keys | `from_body` | Parses, ignoring them — forward tolerance is deliberate | | GAP |
| TC-305 | REQ | Valid record | `to_body()` | Monetary fields are STRINGS in the body, never JSON numbers | INV-1 | GAP |
| TC-307 | REQ | Valid outcome | `from_body(to_body(r))` | Equal | A11, INV-8 | `test_outcome_round_trips_exactly` |
| TC-308 | CHAR | None | `OutcomeRecord(outcome=SUCCESS, base_tx_hash=None)` | Constructs — the seeded fixtures do this. So the record type alone does not enforce NEG-07's "no success without a reference"; `BaseExecutionResult` does | NEG-07 | GAP |
| TC-309 | REQ | None | `base_tx_hash=12345` | `ValidationError` | NEG-07 | GAP |
| TC-311 | REQ | Stored body with `outcome: "pending"` | `from_body` | `ValueError` from the enum, caught as absent — there is no pending outcome, only an absent one | NEG-09 | GAP |
| TC-314 | REQ | Valid snapshot | `from_body(to_body(s))` | Equal, with allowlists restored as TUPLES from stored lists | INV-8 | `test_owner_policy_snapshot_round_trips_exactly` |
| TC-315 | CHAR | None | `OwnerPolicySnapshot(max_amount=Decimal("-1"))` | Constructs — `require_finite_decimal` again. Audit-only record, so this is a sibling of F-5's asymmetry rather than part of its failure chain | | GAP |
| TC-333 | REQ | Valid event | `from_extra(to_extra(e), ts)` | Equal; `previous_status` None round-trips as JSON `null` | INV-8 | GAP |
| TC-334 | REQ | Valid event | `to_extra()` | Contains `kind == "finne_authority_event"` — the only marker distinguishing authority events from other journal entries | INV-8 | GAP |
| TC-335 | REQ | None | `from_extra("not a dict", ts)` called DIRECTLY | `ValidationError` "must be a dict" | NEG-06 | GAP — round 1 found the previously cited test exercises the fold, which skips a non-dict `extra` before `from_extra` is ever called, so this validation branch is unreached |
| TC-336 | REQ | None | `from_extra` with `new_status: "archived"` | `ValueError` from the enum | NEG-06 | GAP |
| TC-338 | CHAR | Module source | Inspect | `PrecedentRelationshipRecord` is absent with the reason in a comment — deferred, not forgotten | | GAP |

## II.4 `finne/memory/client.py` — remaining surface

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-340 | REQ | Empty store | Write then read a case version | Round-trips exactly | A2, INV-8 | `test_case_version_round_trips_exactly` |
| TC-343 | REQ | Empty store | `read_case_version("missing")` | `None`, not an exception | NEG-06 | `test_missing_case_version_reads_as_none` |
| TC-344 | REQ | Store holding a body that fails validation | `read_case_version` | `None` — absent, never permission | NEG-06 | `test_malformed_stored_case_version_reads_as_none_not_permission` |
| TC-345 | REQ | Store holding a non-dict body | `read_case_version` | `None`, no crash | NEG-06 | `test_non_dict_stored_body_reads_as_none_not_crash` |
| TC-346 | REQ | Empty store | Write then read an outcome | Round-trips exactly | A11, INV-8 | `test_outcome_round_trips_exactly` |
| TC-348 | REQ | Empty store | `read_outcome("missing")` | `None` | NEG-06 | `test_missing_outcome_reads_as_none` |
| TC-349 | REQ | Empty store | Write then read a snapshot | Round-trips; the reference body arrives JSON-stringified under `"body"` and is parsed back | INV-8 | `test_owner_policy_snapshot_round_trips_exactly` |
| TC-352 | REQ | Reference holding invalid JSON | `read_owner_policy_snapshot` | `None` | NEG-06 | `test_malformed_stored_snapshot_reads_as_none` |
| TC-353 | REQ | Reference whose `body` is not a string | `read_owner_policy_snapshot` | `None` — `TypeError` from `json.loads` is caught | NEG-06 | GAP |
| TC-355 | CHAR | Two `MemoryStore` instances over one file | Concurrent writes | NOT protected — the architecture is single-writer-at-a-time by design. Recorded so the limit is a decision, not a surprise | | GAP |
| TC-397 | REQ | Store with several cases | `search_cases(query)` | Matching validated records returned | A4 | `test_search_cases_finds_matching_records` |
| TC-398 | REQ | Store with one malformed body | `search_cases` | Malformed skipped, others returned — a bad record removes itself, not the query | NEG-06 | `test_search_cases_excludes_malformed_records` |
| TC-400 | REQ | Store for tenant X | `clear_all_case_data_for_demo_reset(confirm_tenant_id="Y")` | `ValueError`; nothing deleted. The tenant is read from the CLIENT, not echoed from the argument | | GAP |
| TC-402 | REQ | Store with snapshots and events | Same call with the correct tenant | Snapshots and journal entries SURVIVE — no delete exists for those tiers, which is why a full rehearsal needs a new database file | A14, INV-8 | `test_reset_refuses_when_prior_session_data_exists` |
| TC-403 | REQ | Module source | Inspect | `archive_entity` is never called — withdrawn and superseded cases must stay retrievable while ineligible | A7 | GAP |

## II.5 `finne/base/` — hashing, units, environment

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-426 | REQ | None | `_decision_id("DV-001-V1")` twice | Identical; equals `keccak256` of the UTF-8 text, matching the contract's key | A13 | `test_decision_id_is_deterministic_and_distinguishes_inputs` |
| TC-428 | REQ | None | `_facts_hash` twice on the same inputs | Identical | A11 | `test_facts_hash_is_deterministic_and_sensitive_to_material_facts` |
| TC-429 | REQ | None | `_facts_hash` with each of the seven fact fields varied in turn | A different hash for each of the seven | A11 | PARTIAL — the cited test varies `network` and the citation tuple only; the other six fact fields are unvaried |
| TC-430 | REQ | None | `_facts_hash` with `cited_precedents` varied | Different hash — the receipt binds to the precedents relied upon | A5, A11 | `test_facts_hash_is_deterministic_and_sensitive_to_material_facts` |
| TC-431 | CHAR | None | `cited_precedents` reordered | Different hash — order is significant because the payload is a JSON list | | GAP |
| TC-432 | CHAR | None | `authorized_amount` varied, all else equal | SAME hash — the amount is not in the payload; it is recorded separately as the contract's `authorizedAmount`, so the receipt as a whole still binds it | A11 | GAP |
| TC-433 | REQ | None | Payload dict built in a different key order | Same hash — `sort_keys=True` makes it canonical and independently reproducible | A11 | GAP |
| TC-434 | CHAR | None | `proposed_at` varied | Same hash — provenance is deliberately excluded | | GAP |
| TC-435 | REQ | None | `_authorized_amount_units(Decimal("10000.00"))` | `10000000000` | A11 | `test_authorized_amount_units_converts_to_six_decimals` |
| TC-436 | REQ | None | `Decimal("0.000001")` | `1` — the smallest representable unit | | GAP |
| TC-437 | REQ | None | `Decimal("0.0000001")` (7dp) | `ValueError` — refuses to round, because rounding up would record a policy value above what was authorized | INV-1 | `test_authorized_amount_units_rejects_amounts_finer_than_six_decimals` |
| TC-447 | REQ | `config/base_deployment.json` absent | `_load_deployment()` | `RuntimeError` naming `deploy_contract.py` | | GAP |
| TC-462 | CHAR | Any submission path | Inspect fee fields | Derived from the network, not hardcoded gwei — Base Sepolia's real prices are fractions of a gwei and a mainnet assumption is rejected outright | | GAP |
| TC-472 | REQ | Log in the first chunk | `_find_transaction_hash` | Found; stops immediately | | `test_find_transaction_hash_finds_log_in_first_chunk` |
| TC-473 | REQ | Log several chunks back | `_find_transaction_hash` | Found | | `test_find_transaction_hash_finds_log_in_middle_chunk` |
| TC-474 | REQ | Log exactly at the deployment block | `_find_transaction_hash` | Found — the lower boundary is inclusive | | `test_find_transaction_hash_finds_log_at_deployment_block_boundary` |
| TC-475 | REQ | No log within 25 chunks | `_find_transaction_hash` | `None` after a bounded scan | | `test_find_transaction_hash_exhausts_scan_and_returns_none` |
| TC-476 | REQ | RPC failing mid-scan | `_find_transaction_hash` | `None`, no exception escaping — the "413 Payload Too Large" class of failure is handled | | `test_find_transaction_hash_returns_none_on_mid_scan_rpc_failure` |
| TC-490 | REQ | Deployment file exists | `deploy_contract(force=False)` | `RuntimeError` — no accidental redeploy | | GAP |
| TC-491 | REQ | Deployer balance 0 | `deploy_contract` | `RuntimeError` naming the address, before compiling or signing | | GAP |
| TC-492 | REQ | Deployment receipt `status=0` | `deploy_contract` | `RuntimeError` "reverted"; no deployment file written | | GAP |
| TC-493 | REQ | Successful deploy | `deploy_contract(force=True)` | Writes address, ABI, `chain_id` READ FROM THE RPC, tx hash, deployment block | | GAP |
| TC-494 | REQ | Variable set in the process environment AND in `.env` with different values | `get_env_var` | The process environment wins | INV-9 | GAP |
| TC-496 | REQ | Variable set nowhere | `get_env_var` | `RuntimeError` with an actionable message — never an empty string or `None` | INV-9 | GAP |
| TC-497 | CHAR | Variable `""` in the environment, present in `.env` | `get_env_var` | Falls through to `.env` — empty is treated as unset | | GAP |
| TC-498 | REQ | `.env` with comments, blank lines, and a line with no `=` | `_read_dotenv_file` | Those lines skipped, valid pairs parsed | | GAP |
| TC-499 | DEFECT | `.env` containing `KEY="quoted"` | `_read_dotenv_file` | **Observed:** the value includes the quotes (F-7). **Desired:** strip a single matched pair of surrounding quotes, as every dotenv reader does | | GAP |

## II.6 `finne/cli.py`

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-541 | REQ | None | `"a\nb"` | Newline PRESERVED — it is content, and multi-line explanations need it | | GAP |
| TC-542 | REQ | None | `"\x1b[2J"` | Escaped to a visible form; no raw escape survives | | `test_rendering_strips_control_sequences_that_could_rewrite_the_screen` |
| TC-543 | REQ | None | `"A\x00B"` versus `"AB"` | Render DIFFERENTLY — deleting control characters made these identical, the first failed attempt | | `test_rendering_escapes_combining_marks_without_conflating_values` |
| TC-544 | REQ | None | `"e" + U+0301` versus `U+00E9` | Render DIFFERENTLY — NFC normalisation made these identical, the second failed attempt. Two distinct ids must never display as one | A5 | `test_rendering_escapes_combining_marks_without_conflating_values` |
| TC-545 | REQ | None | Literal `"<U+0301>"` versus a real combining acute | Render DIFFERENTLY — escaping without escaping the delimiter made these collide, the third failed attempt | | `test_rendering_escapes_combining_marks_without_conflating_values` |
| TC-546 | REQ | None | `"7" + U+0338` | The combining mark escaped, so it cannot strike through the digit beside it | | `test_rendering_escapes_combining_marks_without_conflating_values` |
| TC-547 | REQ | None | `U+202E` (right-to-left override) | Escaped — category `Cf` is caught by the `C*` rule | | GAP |
| TC-548 | REQ | None | `U+200D` (zero-width joiner) | Escaped | | GAP |
| TC-551 | REQ | None | `"<"` | Escaped, so an escape can never be forged | | GAP |
| TC-553 | REQ | Any frame | Caller text containing `"[/x]"` | Rendered literally; no `MarkupError` | | `test_rendering_never_parses_caller_text_as_markup` |
| TC-554 | REQ | Any frame | Caller text containing `"[bold red]"` | Rendered literally, not styled | | GAP |
| TC-555 | CHAR | `FINNE_PLAIN_OUTPUT=1` | `console()` | `no_color=True`, width 100 — captured output stays stable and diffable | A14 | GAP |
| TC-557 | CHAR | `FINNE_PLAIN_OUTPUT=0` | `console()` | Styled — only the exact string `"1"` enables plain mode | | GAP |
| TC-558 | REQ | Both modes | `decision_panel(...)` | The canonical change line appears VERBATIM in both, so tests check the same string a viewer sees | A4, A5 | `test_session2_constrains_and_cites_precedent_once_precedent_has_a_recorded_outcome` |
| TC-559 | REQ | Decision with no citations | `decision_panel` | Change line renders `(citing no precedent)` | A1 | GAP |
| TC-560 | REQ | Empty candidate list | `candidates_table([])` | Prints "Retrieved 0 candidate(s)" — a FACT about history | A6 | GAP |
| TC-561 | REQ | Mixed eligibility | `candidates_table` | Comparability, authority state and outcome shown as three SEPARATE columns plus a verdict — similarity is never conflated with authority | A7 | GAP |
| TC-562 | REQ | Any detail string | `memory_failure(detail)` | States "MEMORY FAILURE", "RESULT: ESCALATE", and that nothing was authorized, submitted or persisted — deliberately distinct from "Retrieved 0 candidate(s)", because an outage is the absence of any fact | NEG-01 | `test_neg_01_unavailable_memory_escalates_visibly_and_never_crashes` |
| TC-564 | REQ | Console whose `print` raises | `note(...)` | Falls back to plain `print`; no exception escapes | | `test_output_failure_after_persistence_does_not_abort_the_session` |
| TC-565 | REQ | Both output paths failing | `note` / `warn` / `candidates_table` | Silence; no exception — an authorization may already be persisted and settled, so a closed pipe must not abort the remaining work | | `test_non_critical_output_still_degrades_quietly_when_nothing_can_be_written` |
| TC-566 | REQ | Both output paths failing | `decision_panel(...)` | `PresentationError` — a session that persists and submits an authorization no one ever saw satisfies none of the acceptance criteria | A4, A5 | `test_the_decision_frame_fails_closed_when_it_cannot_be_shown` |
| TC-567 | REQ | Both output paths failing | `memory_failure(...)` | `PresentationError` | NEG-01 | GAP |
| TC-568 | REQ | Rich failing, plain succeeding | `decision_panel(...)` | No exception; the plain fallback carries the full change line and explanation | A4 | GAP |
| TC-570 | REQ | Any frame | Inspect | Every caller-supplied string passes through `_clean`; no frame interpolates raw caller text into a markup string | | GAP |

## II.7 Demo scripts

| TC | Class | Precondition | Input | Expected | Traces | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| TC-630 | REQ | Fresh database | `reset_demo.py` | `CASE-003`…`CASE-008` seeded; `CASE-001` and `CASE-002` NOT seeded — the recall must be genuine, not staged | A14 | `test_reset_seeds_known_state_and_leaves_case_001_unseeded` |
| TC-631 | REQ | After reset | Inspect each seeded fixture | Amounts, outcomes and folded states match `ACTIVE_DEMO_DESIGN` section 5 exactly: `DV-003` 20000 withdrawn, `DV-004` 5000 active, `DV-005` 10000 active non-comparable, `DV-006` 15000 superseded, `DV-007` 12000 failure questioned, `DV-008` 18000 draft | A7, A14 | PARTIAL — `test_full_active_demo_corpus_yields_documented_outcome` asserts the engine's result over the corpus, not each fixture's stored state |
| TC-632 | REQ | After reset | Inspect | Four of the six seeded fixtures carry amounts ABOVE 10,000 — the deliberate trap, so a broken authority filter raises the derived ceiling and fails loudly | A7, INV-4 | GAP |
| TC-633 | REQ | Database where `session1.py` has already run | `reset_demo.py` | Refuses with an actionable message naming `DV-001-V1`; exit 1 | A14, INV-8 | `test_reset_refuses_when_prior_session_data_exists` |
| TC-634 | REQ | Database with ONLY a case version for `DV-001-V1` | `reset_demo.py` | Refuses — the residue check covers case version, snapshot AND events, because an interrupted run may have written only some | A14 | GAP |
| TC-635 | REQ | Database with ONLY a snapshot for `DV-002-V1` | `reset_demo.py` | Refuses | A14 | GAP |
| TC-636 | REQ | Database with ONLY authority events for `DV-001-V1` | `reset_demo.py` | Refuses | A14 | GAP |
| TC-637 | REQ | Fresh database | `reset_demo.py` twice | Second run succeeds — seeded fixtures are cleared and re-seeded; only live-created ids block a reset | A14 | `test_demo_resets_and_rehearses_repeatably` |
| TC-638 | REQ | Any run | Inspect the tenant used | `DEMO_TENANT_ID` only; the hard delete is never invoked against another tenant | | GAP |
| TC-639 | REQ | Decision with an outcome already recorded | `reconcile_outcome.py` | Prints the existing outcome; exit 0; writes nothing | INV-8 | `test_reconcile_outcome_is_idempotent_when_already_recorded` |
| TC-640 | REQ | Decision with no case version | `reconcile_outcome.py` | Refuses; exit 1; writes nothing | NEG-09 | `test_reconcile_outcome_refuses_for_a_decision_with_no_case_version` |
| TC-646 | REQ | Deployment file exists | `deploy_contract.py` without `--force` | Prints the failure; exit 1 | | GAP |
| TC-647 | REQ | Any invocation | Source inspection | The script imports no `web3`, `eth_account` or `solcx` — every key-touching path lives in `finne/base/adapter.py` | INV-9 | `test_only_finne_base_imports_key_material_libraries` |
---

# Out Of Scope

- Performance, load, and soak testing. Nothing in `SPEC-001` states a latency or throughput requirement.
- Anything requiring `PrecedentRelationship` persistence, deferred per `ACTIVE_DEMO_DESIGN` section 6 and excluded by `SPEC-001` section 15.
- Multi-domain precedent support, a second domain instantiation of the `PREREQ-002` model, and any web or hosted interface.
- Base mainnet cases. `ORG-Q1` is open and the build targets Sepolia, with the network as a configuration value.
- Any test requiring a model at runtime. No module calls one, and reinstating one requires an approved specification change first.

# Next Step

This catalogue is a specification and remains unapproved. Nothing in it may be implemented until Q1–Q4 are answered, because nine cases are blocked on them and two of the answers change what the expected result should be.

Implementation, when authorized, is a separate bounded change under the normal lifecycle — `DECIDE → SPEC → BRANCH → IMPLEMENT → REVIEW → COMMIT` — taking the Recommendations in the order given.

# Review History

| Round | Date | Verdict | Outcome |
| --- | --- | --- | --- |
| 1 | 2026-09-08 | NOT READY FOR COMMIT — 2 blockers, 8 important, 2 nice-to-have | All 12 reproduced and accepted. Blocker 1 became `F-9` and open question Q1. Blocker 2 produced the Class column and the Part I / Part II split. Two findings the draft missed became `F-10` and Q3. `F-2` and `F-6` were upgraded from "odd" and "theoretical" to a false explanation and an undefined fold. Five coverage false positives corrected, eighteen unnamed coverage claims removed, the traceability matrices regenerated from row data, and the document trimmed from 564 rows to 479 |
