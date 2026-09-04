# Hackathon Rules Register

## Status

- CONFIRMED: The official event is the **Sibyl Labs Hackathon** ("build with agents that don't forget"), organised by Sibyl Labs and supported by Base and Virtuals Protocol.
- CONFIRMED: The rules below were verified on `2026-09-03` from the official sources listed in the Source Register.
- CONFIRMED: Verified rules in this register are hard project constraints.
- RESOLVED: `ORG-Q2` was resolved by Arko on 2026-09-03. The repository is licensed MIT; see `LICENSE`. `DECISION-024` records the choice.
- UNRESOLVED: `ORG-Q1` remains open and is listed in the Open Organiser Questions section; it materially affects the Base partner multiplier. `ORG-Q3` is resolved — see below.
- CONFIRMED: Voluntarily adopted development controls are governed separately by `AI_BUILD_GOVERNANCE.md`; they are not official event rules.
- CONFIRMED: No ETHOnline rule, sponsor, bounty, deadline, prize cap, submission format, or demo requirement is imported into this project.

## Source Register

| Source | Verified | Used for |
| --- | --- | --- |
| `https://hack.sibyllabs.org/` | 2026-09-03 | Event identity, timeline, prizes, partner stacks, multipliers, memory thesis |
| `https://hack.sibyllabs.org/rules` | 2026-09-03 | Gate test, rubric weights, PMF bonus, partner criteria, eligibility, IP, submission requirements |
| `https://hack.sibyllabs.org/submissions` | 2026-09-03 | Submission fields, demo content, deadline |
| `https://docs.sibyllabs.org/memory` | 2026-09-03 | Sibyl Memory product description and storage model |
| `https://docs.sibyllabs.org/memory/install` | 2026-09-03 | Install path, account/credential requirement, Python version |
| `https://docs.sibyllabs.org/memory/integrations` | 2026-09-03 | Python direct-integration package and client class |
| `https://docs.sibyllabs.org/memory/cli` | 2026-09-03 | CLI command surface |
| `https://pypi.org/pypi/sibyl-memory-client/json` | 2026-09-03 | Package version, licence, Python requirement, published API surface |

## Verified Official Rules

### Timeline

- CONFIRMED: Registration ran 2026-08-16 to 2026-08-31.
- CONFIRMED: Build window is 2026-09-01 to 2026-09-10.
- CONFIRMED: Submission deadline is 2026-09-10 at 23:59 UTC.
- CONFIRMED: Partner workshops run 2026-09-05 to 2026-09-07.
- CONFIRMED: Judging runs 2026-09-11 to 2026-09-12; winners are announced 2026-09-13 to 2026-09-15.
- CONFIRMED: All deadlines are stated in UTC.

### Memory Requirement

- CONFIRMED: Sibyl Memory is mandatory.
- CONFIRMED: Memory must be load-bearing: critical to core function, not decorative.
- CONFIRMED: The organiser's gate test is a deletion test — removing the memory calls must cause the project to fail.
- CONFIRMED: The agent must recall and use persisted context in a genuinely fresh session to change what it knows, decides, or does.
- CONFIRMED: Fresh-session recall must be demonstrated in the demo video as one continuous unedited segment.
- CONFIRMED: The README must identify the memory read and write locations, findable within two minutes.
- CONFIRMED: Non-load-bearing integrations — trivial notepads, decorative storage, thin wrappers — are disqualified.
- CONFIRMED: Sibyl Memory is a local-first, file-based memory layer: SQLite under `~/.sibyl-memory/`, FTS5 full-text search, no vector database and no embeddings.

### Submission Requirements

- CONFIRMED: Public GitHub repository with genuine commit history.
- CONFIRMED: The repository licence must be OSI-approved: MIT or Apache-2.0.
- CONFIRMED: The README must state functionality, the load-bearing memory location, partner stacks used, an explanation of how memory made the project possible, complete setup and run instructions, and a Prior Work declaration.
- CONFIRMED: Demo video must be 2 to 5 minutes and must cover the problem, the audience, the product, the mechanics, and the memory integration.
- CONFIRMED: The submission must name the builders and every Base or Virtuals stack used.
- CONFIRMED: The submission must include a memory implementation note explaining what the agent persists, recalls, and uses to make decisions.
- CONFIRMED: Two public build-in-public posts are required — the demo video plus at least one build-log post — tagging `@sibylcap` and every claimed partner.

### Judging

- CONFIRMED: Two-stage process. Stage one is a pass/fail gate decided by majority panel vote; a tie is a failure. The gate is the load-bearing memory deletion test.
- CONFIRMED: Stage two is a 100-point rubric scored as the mean of passing judges: memory is load-bearing 40%, innovation and originality 25%, technical execution 20%, pitch and presentation 15%.
- CONFIRMED: A PMF bonus of +0 to +10 requires publicly verifiable evidence such as a named audience, a validated pain point, a waitlist, design partners, real usage, or pilots. Claims alone earn nothing and fabricated evidence disqualifies.
- CONFIRMED: Final score is `(Rubric + PMF Bonus) × Partner Multiplier`.

### Partner Stacks

- CONFIRMED: Base and Virtuals are optional partner stacks.
- CONFIRMED: Zero verified stacks give ×1.00; one verified stack gives ×1.15; two verified stacks give ×1.25, and the multiplier is capped there.
- CONFIRMED: Base eligibility is established by deployment. The bonus is earned by an executed onchain action — a wallet operation, an x402 payment, a B20 read, or a contract interaction — shown in the demo.
- CONFIRMED: Virtuals eligibility requires an ACP job, a registered or transacting agent, or a Virtuals-native integration exercised in the demo.
- CONFIRMED: This project claims Base only. Virtuals is out of scope; the achievable multiplier is therefore ×1.15.

### Eligibility, IP, And Prizes

- CONFIRMED: Entrants must be 18 or older.
- CONFIRMED: Sanctioned jurisdictions, Sibyl Labs staff, and reference builds are excluded.
- CONFIRMED: Entrants retain all IP. Submission grants Sibyl Labs and partners a non-exclusive, royalty-free, attribution-required licence for promotional use.
- CONFIRMED: Winners provide payout details and participate in a brief case-study interview.
- CONFIRMED: The prize pool is $10,000 USDC paid on Base, split across the top five: $4,000 plus a Network School residency; $2,500 plus one Base Support Program entry; $1,500; $1,000; $1,000.

## Open Organiser Questions

These are unresolved against the official sources and must be answered by the organisers or explicitly ruled inapplicable by Arko.

| ID | Question | Why it matters | Current handling |
| --- | --- | --- | --- |
| `ORG-Q1` | Does an executed onchain action on **Base Sepolia** satisfy the Base partner multiplier, or is **Base mainnet** required? | Directly determines whether the ×1.15 multiplier is earned, and whether the demo must spend real funds. The published rules state deployment plus an executed onchain action but do not name a network. | Architecture is network-agnostic and configuration-driven. Default build target is Base Sepolia; a mainnet switch must remain a single configuration change. Do not assume Sepolia qualifies. |
| `ORG-Q2` | ~~Is `MIT` or `Apache-2.0` preferred?~~ | Both are explicitly permitted by the rules, so no organiser input is needed. | **RESOLVED 2026-09-03.** Arko selected MIT. `LICENSE` exists at repository root. Recorded as `DECISION-024`. |
| `ORG-Q3` | ~~Does the free Sibyl Memory tier's `sibyl init` requirement and 5 MB cap impose any limit affecting judging or the deletion test?~~ | Verified empirically against the installed `sibyl-memory-client` 0.8.0 (2026-09-04): `MemoryClient.local()` requires **no credentials at all** for local operations — `account_id`/`session_token`/`credentials_*` are optional keyword arguments defaulting to `None`, and every core operation (`set_entity`, `get_entity`, `write_event`, `search`, ...) works immediately against a fresh tenant with no sign-in step. The browser-auth `sibyl init` flow applies to the CLI's cloud-tier features (learning, linting, tier upgrades), not to this library's core local API. | **RESOLVED 2026-09-04.** No `sibyl init` prerequisite exists for judges reproducing the build. The 5 MB free-tier cap still applies; the demo corpus stays far below it. |

## Submission Practice: AI-Tool Attribution (Self-Imposed, Not An Official Rule)

- CONFIRMED: No sourced official Sibyl Labs rule in this register mandates disclosing which AI tools were used to build a submission. This section is **not** a `Verified Official Rule` — it records Arko's own submission practice, adopted voluntarily and governed the same way as `AI_BUILD_GOVERNANCE.md`.
- CONFIRMED: Arko's practice is to attribute both AI tools used on this project prominently in the submission, not only in the internal audit trail:
  - **Claude Code (Anthropic)** — implementation, drafting, and planning across this repository.
  - **Codex (OpenAI)** — independent second-pass review, per `AGENT_BUILD_INSTRUCTIONS.md` Section 11.
- CONFIRMED: The substantive, detailed record of what each tool did already exists in `AI_USAGE.md`, `BUILD_LOG.md`, `HUMAN_DECISIONS.md`, and `prompts/`, and in `Co-Authored-By` trailers on individual commits. This section exists so that attribution is also visible where a judge would actually look: the PR description and the README.
- CONFIRMED: Before submission, the PR description and the README must each name both tools and point to `AI_USAGE.md` for the full record. This is a submission-readiness checklist item, not a change to any product, authority, or approval rule.

## Source Requirements

Before any official event rule is marked `CONFIRMED`, record its source, exact requirement, applicability to this project, and verification date. Do not infer or invent event rules from a different hackathon, product, sponsor, or prior project. Re-verify this register before submission.
