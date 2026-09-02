# PREREQ-001: Finné Memory V1 Product Definition Proposal

## Proposal Status

- CONFIRMED: This document is a planning proposal for Arko's review and does not authorize implementation.
- CONFIRMED: Arko approved the four decision packages in Section 10 and the associated V1 product definition in this proposal.
- CONFIRMED: `PREREQ-001` is complete following Arko's approval and clarification of all four decision packages.
- CONFIRMED: `TASK-001` must not be created as part of this prerequisite.

## 1. Primary User And Buyer

- CONFIRMED: The primary user is a supplier-risk or procurement-compliance professional who uses an automated decision system to evaluate supplier onboarding matters.
- CONFIRMED: The primary buyer is the procurement, supplier-risk, or compliance function of an organization operating repeatable supplier-onboarding decisions.
- CONFIRMED: The primary user remains accountable for the supplier outcome and uses Finné Memory as decision support rather than as the final decision-maker.
- ASSUMPTION: The V1 user is comfortable reviewing structured facts, policy references, prior decisions, and citations.
- UNRESOLVED: The production buyer's organization size, industry, regulatory environment, procurement volume, and deployment model are outside the decisions needed to close `PREREQ-001`.

## 2. Exact Problem

- CONFIRMED: Automated decision systems commonly treat recurring consequential matters as new reasoning events even when relevant prior decisions exist.
- CONFIRMED: Ordinary memory does not establish which prior decisions are relevant, whether they remain authoritative, or why they should be followed, distinguished, questioned, or ignored.
- CONFIRMED: In the V1 domain, supplier-risk and procurement-compliance professionals lack a reliable machine-readable precedent layer connecting current supplier facts to prior onboarding decisions, evidence, policy versions, citations, and recorded authority status.
- CONFIRMED: The resulting product problem is that an automated supplier-onboarding workflow cannot consistently explain which prior decisions matter or whether a factually similar decision remains valid authority.
- CONFIRMED: Finné Memory addresses this problem by producing a cited precedent packet; it does not approve, reject, or escalate the supplier itself.

## 3. Representative Matter

- CONFIRMED: The representative V1 matter is whether a supplier with incomplete beneficial-ownership evidence should be approved, rejected, or escalated.
- CONFIRMED: The matter must make similarity and authority diverge by including at least one highly similar prior decision that is no longer authoritative and at least one less-similar prior decision that remains active.
- ASSUMPTION: The synthetic matter can be understood without specialist legal advice and can be demonstrated using fictional suppliers, people, policies, and evidence.
- CONFIRMED: The exact synthetic facts, evidence, policy text, recorded outcomes, and precedent records are defined in the approved `PREREQ-002` contract and seed-data appendix.

## 4. Inputs And Outputs

### Inputs

- CONFIRMED: A new decision matter containing a stable matter reference and a plain-language description of the supplier-onboarding question.
- CONFIRMED: Structured facts or source material from which facts can be extracted, including the state of beneficial-ownership evidence.
- CONFIRMED: Evidence and source references supplied for the current matter.
- CONFIRMED: The applicable policy or policy-version context when known.
- CONFIRMED: A system-managed corpus of prior decision records, sources, citations, authority states, and supersession relationships is required for precedent analysis.
- ASSUMPTION: V1 uses entirely synthetic input data and does not require production supplier or personal data.
- CONFIRMED: Technology-neutral fields, required-versus-optional inputs, validation semantics, and identifiers are defined by `PREREQ-002`; physical formats remain DEFERRED to `PREREQ-003`.

### Outputs

- CONFIRMED: The primary machine-readable output is a structured, cited `PrecedentPacket`.
- CONFIRMED: The packet identifies the current matter, relevant prior decisions, each candidate's recorded authority status, material similarities and differences, validated source references, and important evidence gaps or limitations.
- CONFIRMED: The packet may explain whether a precedent appears suitable to follow, distinguish, question, or disregard, but this treatment is decision support and not the supplier outcome.
- CONFIRMED: A readable `PrecedentBrief` may be generated from validated packet content.
- CONFIRMED: The output does not contain a Finné Memory-made final approval, rejection, or escalation decision.
- CONFIRMED: After an external final decision is made and an authorized human confirms it, Finné Memory may create a new decision record for future precedent use.
- CONFIRMED: Citation representation and the write-back record structure are defined by `PREREQ-002`.
- DEFERRED: The complete packet and brief schemas and any confidence representation require later bounded specification without changing the approved decision-record contract.

## 5. Complete V1 Workflow

1. CONFIRMED: A permitted human user or automated client submits the current supplier matter, facts, evidence, and available policy context.
2. CONFIRMED: Finné Memory validates required deterministic references and either receives structured facts or uses model assistance to propose facts extracted from source material.
3. CONFIRMED: Finné Memory retrieves factually relevant prior decision records from the synthetic corpus.
4. CONFIRMED: Finné Memory reads recorded authority status and validates citation and supersession relationships deterministically.
5. CONFIRMED: Finné Memory compares current facts with candidate precedents and keeps factual similarity separate from authority eligibility.
6. CONFIRMED: Finné Memory assembles a schema-valid `PrecedentPacket` containing candidates, authority information, comparisons, citations, and limitations.
7. CONFIRMED: Finné Memory renders a readable cited `PrecedentBrief` from the validated packet.
8. CONFIRMED: A downstream human or system makes the supplier approval, rejection, or escalation decision outside Finné Memory.
9. CONFIRMED: An authorized human reviews the completed outcome and explicitly confirms whether it may be recorded as a new decision record.
10. CONFIRMED: After confirmation and deterministic validation, the completed decision enters the precedent corpus with provenance and an initial authority state defined by `PREREQ-002`.
11. CONFIRMED: The demo can be reset to a known synthetic starting state and rerun through the same workflow.
- DEFERRED: Exact validation responses, retry behavior, human review screens, and whether model-assisted fact extraction requires confirmation require later bounded specification.

## 6. User Roles And Permissions

- CONFIRMED: A `Matter Submitter` may create a matter, provide facts and evidence, request precedent analysis, and view the resulting packet and brief.
- CONFIRMED: A `Decision Reviewer` is the accountable procurement or compliance professional who may use the packet, record the externally made outcome, and confirm write-back.
- CONFIRMED: An `Authority Steward` may curate policy versions, recorded authority states, supersession relationships, and corpus corrections under deterministic rules.
- CONFIRMED: An `Automated Client` may submit matters and consume packets only under delegated permission; it may not confirm final outcomes, write completed decisions into the authoritative corpus, or alter authority state.
- CONFIRMED: No role grants Finné Memory or its model authority to make the final supplier decision.
- CONFIRMED: Model output may not grant permissions, alter authority, or bypass deterministic validation.
- CONFIRMED: One demo user may hold both Decision Reviewer and Authority Steward roles, but confirmation and activation remain separate, timestamped actions.
- DEFERRED: Identity establishment, technical authorization enforcement, and whether authority stewardship is exposed in the V1 interface belong to `PREREQ-003` and later interface specification.

## 7. Product Boundaries

- CONFIRMED: Finné Memory is an institutional-memory and precedent layer for autonomous decision-making.
- CONFIRMED: Finné Memory retrieves relevant prior decisions, reports their recorded authority, compares facts, validates citations, and produces cited decision support.
- CONFIRMED: Finné Memory does not make or enforce the final supplier decision.
- CONFIRMED: Finné Memory remains completely separate from Finné/x402.
- CONFIRMED: Finné Memory does not process payments, x402 requests, escrow, refunds, settlement, transaction-performance verification, or dispute resolution.
- CONFIRMED: Finné Memory does not determine whether a purchased service was delivered.
- CONFIRMED: Finné Memory does not permit model output to invent sources or decisions, change authority state, establish unvalidated citation relationships, or override deterministic rules.
- CONFIRMED: V1 is limited to one synthetic supplier-onboarding workflow and does not claim general multi-domain readiness.
- UNRESOLVED: External integrations, if any, are not selected in `PREREQ-001`.

## 8. V1 Acceptance Criteria

- CONFIRMED: A prepared synthetic supplier matter can be submitted with facts, evidence, and policy context sufficient to run the full V1 workflow.
- CONFIRMED: Finné Memory retrieves the prepared candidate precedents needed to demonstrate baseline, following, distinguishing, supersession, inactive-but-similar, and active-but-less-similar cases.
- CONFIRMED: The result displays factual similarity separately from recorded authority status.
- CONFIRMED: A highly similar but inactive precedent is not represented as active authority.
- CONFIRMED: Every cited source and decision resolves to a deterministic record; unresolved or invalid citations are rejected or explicitly surfaced.
- CONFIRMED: The packet explains material similarities, differences, evidence gaps, and precedent treatment using only supplied facts and validated records.
- CONFIRMED: Neither the packet nor the brief represents Finné Memory as making the supplier's final approval, rejection, or escalation decision.
- CONFIRMED: An automated client cannot confirm a final outcome, write a completed decision into the authoritative corpus, or alter authority status.
- CONFIRMED: A completed external decision enters the corpus only after explicit confirmation by an authorized human and deterministic validation.
- CONFIRMED: Model output cannot change authority state, create accepted citations without validation, or corrupt deterministic records when malformed or unavailable.
- CONFIRMED: The synthetic demo can be restored to a known starting state and rerun reproducibly.
- CONFIRMED: No accepted V1 behavior implements any excluded Finné/x402 or commerce function.
- CONFIRMED: Product-level deterministic invariants and synthetic lifecycle cases are defined by `PREREQ-002`.
- DEFERRED: Executable tests, physical schemas, error responses, performance thresholds, and interface behavior require later approved specifications.

## 9. Explicit Exclusions

- CONFIRMED: Payments and payment authorization are excluded.
- CONFIRMED: x402 protocol behavior is excluded.
- CONFIRMED: Escrow, custody, refunds, and settlement are excluded.
- CONFIRMED: Transaction-performance and service-delivery verification are excluded.
- CONFIRMED: Transaction or payment dispute resolution and arbitration are excluded.
- CONFIRMED: Autonomous final supplier approval, rejection, or escalation by Finné Memory is excluded.
- CONFIRMED: Real supplier data, production policy ingestion, and production identity integrations are excluded from V1.
- CONFIRMED: Multi-domain precedent support and production-scale corpus migration are excluded from V1.
- CONFIRMED: A production administration console is excluded unless later shown to be necessary for the judged demo.
- UNRESOLVED: Sponsor integrations and event-specific submission requirements remain governed by `HACKATHON_RULES.md` and later planning.

## 10. Approved Decisions Closing PREREQ-001

- CONFIRMED: Supplier onboarding and procurement compliance is the V1 domain.
- CONFIRMED: The supplier-risk or procurement-compliance professional is the primary user, and the organization's procurement, supplier-risk, or compliance function is the primary buyer.
- CONFIRMED: Incomplete beneficial-ownership evidence is the representative supplier matter.
- CONFIRMED: Finné Memory produces a cited precedent packet but does not make the final supplier decision; after the downstream decision is made, it may enter the precedent corpus only after explicit confirmation by an authorized human.
- CONFIRMED: These approvals close `PREREQ-001`; authority, citation, and technology-neutral decision-record details were subsequently completed in `PREREQ-002`, while architecture remains assigned to `PREREQ-003`.
