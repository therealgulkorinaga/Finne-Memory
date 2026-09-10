# Insurance-claims domain pivot — kickoff

Recorded 2026-09-10, before implementation, per `AI_BUILD_GOVERNANCE.md`'s lifecycle and `DECISION-025`.

---

## What Arko argued

His own analysis, condensed from a long message on 2026-09-10. Two connected objections:

**Base is not naturally central.**

> "If we force it in, it will look like bounty engineering. The real product is an institutional decision-control / dispute-prevention layer. That can run entirely offchain."

He proposed Base earn its place as an attestation layer instead:

> "We don't put confidential case files onchain. We anchor proof that the institutional decision record existed and has not been altered."

And named the competitive risk directly: CANON already uses case history to determine deal terms and settle in USDC; Meritor uses counterparty memory to set collateral. Staying in agent-spending means competing where the field is crowded.

**The commercial framing was weak.** From "we help institutions remember how they made decisions" to:

> "We help institutions make consistent, defensible decisions before they become disputes."

> "Finné helps institutions catch inconsistent decisions before customers do."

His worked example — the one that decided this — was insurance. Policy covers "sudden and accidental" water damage but excludes gradual leakage. Claim A was paid: a pipe ruptured overnight. Claim B was declined: photographs showed long-term dampness. Claim C arrives looking superficially like B, but the plumber's report shows an abrupt rupture. Without precedent memory, a junior handler or an AI classifies on surface similarity and declines it — and that is the decision that becomes a complaint, then an ombudsman referral.

## What was checked before agreeing

The rules register was re-read. Nothing requires a particular domain. The 40% gate is memory being load-bearing, which is unaffected — a fresh session still retrieves precedent and still cannot act without it.

The blast radius was measured rather than estimated. `network` and `asset` appear in 27 files; the other five fact dimensions are already domain-neutral. Both of the two have genuine insurance meanings — in-network/out-of-network is standard vocabulary, and `finne/cli.py` already renders `asset` as the unit beside the amount, so it maps to settlement currency. **Conclusion: no type-layer rename.** The engine, memory adapter, state machine, retrieval and Base adapter are untouched.

## What is being built

Per `DECISION-028`. The corpus becomes eight claim precedents, the owner policy becomes a claims handler's delegated settlement authority, and the agent assesses a claim rather than an investment.

The mapping that made this cheap:

| Field | Was | Becomes |
| --- | --- | --- |
| `network` | `base` | the claims channel / panel |
| `asset` | `USDC` | settlement currency |
| `action_class` | `capital_deployment` | `claim_assessment` |
| `target_class` | `yield_vault_conservative` | the peril |
| `function` | `deposit` | the decision |
| `counterparty_risk_tier` | counterparty risk | claim risk tier |
| `amount` | amount to deploy | settlement amount |

The authority states stop being synthetic: `active` stands as precedent, `questioned` is under complaint, `superseded` was decided under replaced policy wording, `withdrawn` was overturned by an ombudsman. A withdrawn decision staying retrievable but unable to authorize is exactly what an insurer needs, and it is what the engine already does.

## Standing constraints carried into this work

- **The demonstration's mechanics do not change.** Same retrieval, same derivation, same intersection, same deletion gate. If any of those need changing to fit the domain, stop — that means the engine was not domain-agnostic and the claim that it is was false.
- **The corpus is synthetic and must never be presented otherwise.** `HACKATHON_RULES.md` line 62: PMF evidence must be publicly verifiable and fabricated evidence disqualifies. No pilot, design partner, or insurer engagement is to be claimed anywhere.
- **Commit per phase, not in one lump.** Arko asked specifically that `master` not receive a single mass commit. One branch, several real commits, one merge — never `--squash`.
- **`master` stays shippable throughout.** The branch is abandonable at any point; nothing lands until the whole pivot is verified.
- Do not touch `finne/authority/`, `finne/memory/`, `finne/base/`, or `finne/models.py`. If the pivot appears to require it, that is a finding to report, not a change to make.

## Known state at kickoff

- Branch `feat/insurance-claims-domain`, from `master` at `faae7ce`.
- Suite: 262 passed, 4 skipped. The live agent path is verified and stable — five consecutive calls proposed 20,000.00 identically.
- No abort time set; Arko declined one. Deadline 2026-09-10 23:59 UTC.
