# PREREQ-002: Decision Record And Precedent Corpus Proposal

> **HISTORICAL.** This proposal was resolved into the approved `PREREQ-002` contract and is doubly historical: it was superseded as a proposal, and its supplier-onboarding domain was superseded by `DECISION-022` (2026-09-03). The object model, authority semantics, and invariants carry forward unchanged; only the supplier-domain instantiation is superseded. The active demo design is `docs/product/ACTIVE_DEMO_DESIGN.md`. Preserved unrewritten as historical design work.

## Proposal Status

- CONFIRMED: This is a planning proposal only and does not authorize application code, scaffolding, dependencies, architecture selection, or implementation tasks.
- CONFIRMED: This proposal has been resolved and superseded by `PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md` and its synthetic seed-data appendix.
- CONFIRMED: Supplier onboarding and procurement compliance is the V1 domain.
- CONFIRMED: Finné Memory produces cited precedent support but does not make the final supplier decision.
- CONFIRMED: A completed downstream decision may enter the precedent corpus only after explicit confirmation by an authorized human.
- CONFIRMED: Arko approved decision packages `P2-02` through `P2-10` and `P2-12` in principle with the amendments incorporated below.
- CONFIRMED: Decision packages `P2-01`, `P2-11`, and `P2-13` were approved after exact review and the ten detected issues were resolved as recorded in `PREREQ-002_TRACEABILITY_REVIEW.md`.
- CONFIRMED: `PREREQ-002` is complete; historical `PROPOSED` labels below preserve the reviewed proposal and are not the current authoritative contract.
- CONFIRMED: Similarity, authority, and outcome are separate dimensions throughout this proposal.

## 1. Separation Of Similarity, Authority, And Outcome

- CONFIRMED: Similarity describes how closely the facts of a current matter resemble a prior decision.
- CONFIRMED: Authority describes the recorded eligibility of a prior decision to be treated as precedent.
- CONFIRMED: Outcome describes the external supplier decision: approval, rejection, or escalation.
- PROPOSED: Similarity is query-time analysis stored in a `PrecedentCandidate` or packet, not an authority property of a `DecisionRecord`.
- PROPOSED: Authority is deterministic recorded state and is never inferred from similarity or outcome.
- PROPOSED: Outcome is recorded historical fact and never determines authority by itself.
- PROPOSED: A highly similar decision may be inactive, and a less-similar decision may remain active.
- PROPOSED: No score, model output, or outcome automatically changes an authority state.

## 2. DecisionMatter

- PROPOSED: A `DecisionMatter` represents the current question before a downstream outcome exists.
- PROPOSED: `DecisionMatter.matter_id` is a stable unique identifier.
- PROPOSED: `DecisionMatter.domain` is `supplier_onboarding` in V1.
- PROPOSED: `DecisionMatter.question` contains the decision question in plain language.
- PROPOSED: `DecisionMatter.submitted_by` identifies the permitted human or automated client that submitted it.
- PROPOSED: `DecisionMatter.submitted_at` records when it entered Finné Memory.
- CONFIRMED: `DecisionMatter.relevant_at` is the single explicit date used to select the applicable policy version and authority snapshot for analysis.
- PROPOSED: `DecisionMatter.fact_ids` references the matter's structured facts.
- PROPOSED: `DecisionMatter.evidence_ids` references supporting or conflicting evidence.
- PROPOSED: `DecisionMatter.source_ids` references supplied source records.
- PROPOSED: `DecisionMatter.policy_version_ids` identifies applicable policy versions when known.
- PROPOSED: `DecisionMatter.status` is limited to `open`, `packet_generated`, or `closed` and is separate from precedent authority.
- PROPOSED: `DecisionMatter.packet_ids` records packets generated for the matter without making any packet the final outcome.
- UNRESOLVED: Exact serialization types and storage representation belong to `PREREQ-003`.

## 3. Complete DecisionRecord

- PROPOSED: A `DecisionRecord` represents a completed downstream decision that has passed human confirmation and deterministic validation for entry into the corpus.
- PROPOSED: `DecisionRecord.decision_id` is a stable unique identifier within Finné Memory.
- PROPOSED: `DecisionRecord.record_version` is a positive integer identifying an immutable version of the record.
- PROPOSED: `DecisionRecord.previous_version_id` references the prior version when a correction is issued and is absent for the first version.
- PROPOSED: `DecisionRecord.matter_id` references the originating `DecisionMatter`.
- PROPOSED: `DecisionRecord.domain` is `supplier_onboarding` in V1.
- PROPOSED: `DecisionRecord.question` preserves the question answered by the downstream decision-maker.
- PROPOSED: `DecisionRecord.fact_ids` references the facts considered for the completed decision.
- PROPOSED: `DecisionRecord.evidence_ids` references the evidence considered.
- PROPOSED: `DecisionRecord.source_ids` references all directly cited sources.
- PROPOSED: `DecisionRecord.relevant_at` preserves the originating matter's `relevant_at` date.
- PROPOSED: `DecisionRecord.policy_version_ids` references the policy versions applicable at `DecisionMatter.relevant_at`.
- CONFIRMED: `DecisionRecord.created_at` records when the immutable record version was created.
- CONFIRMED: `DecisionRecord.decided_at` separately records when the downstream decision was made.
- PROPOSED: `DecisionRecord.outcome` contains an external `DecisionOutcome` and is separate from authority state.
- PROPOSED: `DecisionRecord.outcome.outcome_type` is one of `approved`, `rejected`, or `escalated` for V1.
- PROPOSED: `DecisionRecord.outcome.rationale_summary` records the downstream decision-maker's rationale without presenting it as model-authored authority.
- PROPOSED: `DecisionRecord.outcome.decided_by` identifies the downstream decision-maker or authoritative external system.
- PROPOSED: `DecisionRecord.precedent_packet_id` optionally references the packet used during the downstream decision.
- PROPOSED: `DecisionRecord.authority_state` is the current deterministic state derived from the latest valid authority event and remains independent of outcome.
- PROPOSED: `DecisionRecord.authority_history` references an append-only sequence of authority-state events, so a state transition does not rewrite the immutable decision content.
- PROPOSED: `DecisionRecord.citation_edge_ids` references validated citations made by the decision.
- PROPOSED: `DecisionRecord.precedent_relationship_ids` references validated relationships to prior decisions.
- PROPOSED: `DecisionRecord.confirmation.confirmed_by` identifies the authorized human who confirmed corpus entry.
- PROPOSED: `DecisionRecord.confirmation.confirmed_at` records the confirmation time.
- PROPOSED: `DecisionRecord.confirmation.attestation` records that the outcome, provenance, and referenced materials accurately reflect the completed downstream decision.
- PROPOSED: `DecisionRecord.provenance.created_by` identifies the actor that prepared the record.
- PROPOSED: `DecisionRecord.provenance.origin` is one of `human_entry`, `automated_client`, `imported`, or `synthetic_seed`.
- PROPOSED: `DecisionRecord.provenance.source_system_reference` optionally identifies the external system of record.
- PROPOSED: `DecisionRecord.is_synthetic` is `true` for every V1 demo record.
- PROPOSED: Corrections create a new immutable `record_version`; they do not overwrite historical versions.
- PROPOSED: Only the latest valid record version participates in authority evaluation, while prior versions remain auditable.
- UNRESOLVED: Identifier format, timestamp format, field encoding, and physical persistence belong to `PREREQ-003`.

## 4. Facts, Evidence, And Sources

### Fact

- PROPOSED: A `Fact` is a structured assertion about a matter or decision and does not itself carry precedent authority.
- PROPOSED: `Fact.fact_id` is a stable unique identifier.
- PROPOSED: `Fact.subject` identifies what the assertion concerns.
- PROPOSED: `Fact.predicate` identifies the property being asserted.
- PROPOSED: `Fact.value` contains the asserted value.
- PROPOSED: `Fact.value_type` describes the value as `text`, `boolean`, `number`, `date`, or `category` in V1.
- PROPOSED: `Fact.evidence_ids` references evidence supporting or conflicting with the fact.
- PROPOSED: `Fact.source_ids` references the sources from which the assertion came.
- PROPOSED: `Fact.origin` is `human_supplied`, `system_supplied`, or `model_extracted`.
- PROPOSED: `Fact.verification_status` is `unverified`, `supported`, `disputed`, or `confirmed`.
- PROPOSED: `Fact.extraction_confidence` is present only for model-extracted facts and must not be treated as authority.
- PROPOSED: `Fact.recorded_at` and `Fact.recorded_by` preserve provenance.
- PROPOSED: A model-extracted fact must cite at least one evidence item and remains `unverified` until a permitted human or deterministic source confirms it.
- CONFIRMED: Unverified or disputed facts remain visible with status and provenance but cannot support an authoritative conclusion.

### Evidence

- PROPOSED: `Evidence` is a bounded item used to support or contradict one or more facts.
- PROPOSED: `Evidence.evidence_id` is a stable unique identifier.
- PROPOSED: `Evidence.source_id` references exactly one source record.
- PROPOSED: `Evidence.description` identifies the relevant content without silently changing it.
- PROPOSED: `Evidence.locator` identifies a page, section, field, or other reproducible location within the source when available.
- PROPOSED: `Evidence.supports_fact_ids` and `Evidence.contradicts_fact_ids` record explicit fact relationships.
- PROPOSED: `Evidence.observed_at` records when the evidence was captured or observed.
- PROPOSED: `Evidence.added_by` identifies the supplying actor.
- PROPOSED: Evidence may be incomplete or conflicting and must not be silently converted into a confirmed fact.

### Source

- PROPOSED: A `Source` identifies the origin of evidence, policy, or decision support.
- PROPOSED: `Source.source_id` is a stable unique identifier controlled by the deterministic system.
- PROPOSED: `Source.source_type` is one of `policy`, `registry_record`, `supplier_document`, `attestation`, `risk_assessment`, `decision_record`, or `other` in V1.
- PROPOSED: `Source.title` and `Source.issuer` identify the material and its originator.
- PROPOSED: `Source.reference` contains a URI, document reference, or synthetic fixture reference.
- PROPOSED: `Source.issued_at` and `Source.retrieved_at` preserve temporal context when applicable.
- PROPOSED: `Source.content_fingerprint` detects source substitution without prescribing a hashing implementation.
- PROPOSED: `Source.is_synthetic` distinguishes demo fixtures from real records.
- CONFIRMED: Models may reference only source IDs supplied by the deterministic system and may not invent source records.

## 5. Authority States And Meanings

- CONFIRMED: `draft` means the confirmed decision record exists in the corpus but is not eligible to be cited as active authority.
- CONFIRMED: `active` means the record is currently eligible to be treated as authority, subject to policy date and hierarchy checks.
- CONFIRMED: `questioned` means a permitted human has raised a material concern; the record remains visible but is not eligible as active authority until resolved.
- CONFIRMED: `superseded` means a newer validated decision or policy-controlled precedent relationship has replaced the record; it remains visible but is not active authority.
- CONFIRMED: `withdrawn` means a permitted human has removed the record from authoritative use without requiring a replacement; it remains visible for audit but is not active authority.
- CONFIRMED: Authority status answers eligibility only and does not express factual similarity, correctness of outcome, or approval of a supplier.

### AuthorityState

- PROPOSED: `AuthorityState.status` contains exactly one authority state.
- PROPOSED: `AuthorityState.effective_at` records when the state became effective.
- PROPOSED: `AuthorityState.reason` is required for every transition after initial `draft` creation.
- PROPOSED: `AuthorityState.changed_by` identifies the authorized human actor.
- PROPOSED: `AuthorityState.successor_decision_ids` is required for `superseded` and empty for all other states.
- PROPOSED: `AuthorityState.previous_status` records the immediately preceding state.
- PROPOSED: Every state change creates an append-only authority event.

## 6. Permitted Authority-State Transitions

- CONFIRMED: A newly confirmed write-back record enters the corpus as `draft`.
- CONFIRMED: `draft -> active` is permitted only through a separately recorded Authority Steward event after required sources, policy context, citations, provenance, and confirmation are validated.
- CONFIRMED: Activation requires every fact material to the precedent rationale or relationship to be `supported` or `confirmed`; `unverified` or `disputed` facts remain visible with status and provenance but cannot support an authoritative conclusion.
- CONFIRMED: `draft -> withdrawn` is permitted when the record must not enter authoritative use.
- CONFIRMED: `active -> questioned` is permitted when a material concern requires review.
- CONFIRMED: `active -> superseded` is permitted only with at least one validated `supersedes` relationship to a successor decision.
- CONFIRMED: `active -> withdrawn` is permitted with a recorded reason.
- CONFIRMED: `questioned -> active` is permitted when the concern is resolved and the resolution is recorded.
- CONFIRMED: `questioned -> superseded` is permitted with a validated successor relationship.
- CONFIRMED: `questioned -> withdrawn` is permitted with a recorded reason.
- CONFIRMED: `superseded` and `withdrawn` are terminal authority states.
- CONFIRMED: A correction to a terminal record creates a new record version and does not reactivate the historical version.
- CONFIRMED: All unlisted transitions are invalid.

## 7. Citation And Precedent Relationships

### CitationEdge

- CONFIRMED: A `CitationEdge` records support for a specific claim and is separate from a precedent-treatment relationship.
- PROPOSED: `CitationEdge.citation_id` is a stable unique identifier.
- PROPOSED: `CitationEdge.from_id` identifies the decision record or precedent packet making the claim.
- PROPOSED: `CitationEdge.target_type` is `decision`, `policy_version`, `source`, or `evidence`.
- PROPOSED: `CitationEdge.target_id` must resolve to an existing deterministic record of the declared target type.
- PROPOSED: `CitationEdge.claim` states the proposition supported by the citation.
- PROPOSED: `CitationEdge.created_by` and `CitationEdge.created_at` preserve provenance.
- PROPOSED: `CitationEdge.validation_status` is `valid` or `invalid`; only valid citations may appear as supporting citations in a final packet or active decision record.
- PROPOSED: Citation validation confirms referential and eligibility rules but does not claim that a source is true.

### PrecedentRelationship

- CONFIRMED: A `PrecedentRelationship` records how one completed decision treats another and is separate from factual similarity.
- PROPOSED: `PrecedentRelationship.relationship_id` is a stable unique identifier.
- PROPOSED: `PrecedentRelationship.from_decision_id` identifies the later decision applying the treatment.
- PROPOSED: `PrecedentRelationship.to_decision_id` identifies the earlier decision being treated.
- PROPOSED: `PrecedentRelationship.relationship_type` is `follows`, `distinguishes`, `questions`, or `supersedes`.
- PROPOSED: `PrecedentRelationship.rationale` explains the treatment.
- PROPOSED: `PrecedentRelationship.fact_ids` references facts material to the relationship.
- PROPOSED: `PrecedentRelationship.citation_ids` references validated support.
- PROPOSED: `PrecedentRelationship.confirmed_by` and `confirmed_at` are required before persistence as an authoritative corpus relationship.
- CONFIRMED: Models may suggest relationships, but only a deterministically validated, human-confirmed relationship may be persisted.
- CONFIRMED: Creating a valid `supersedes` relationship and moving the target to `superseded` occur as one logical operation.
- CONFIRMED: `follows`, `distinguishes`, and `questions` do not automatically change authority state.

## 8. Policy Versions And Effective Dates

- PROPOSED: A `PolicyVersion` is an immutable version of a named policy.
- PROPOSED: `PolicyVersion.policy_id` identifies the policy family.
- PROPOSED: `PolicyVersion.version_id` uniquely identifies the immutable version.
- PROPOSED: `PolicyVersion.title` names the policy.
- PROPOSED: `PolicyVersion.source_id` references the policy source.
- PROPOSED: `PolicyVersion.issued_at` records publication time.
- CONFIRMED: `PolicyVersion.effective_from` is inclusive.
- CONFIRMED: `PolicyVersion.effective_to` is exclusive and may be absent for the current version.
- PROPOSED: `PolicyVersion.supersedes_version_id` references the immediately prior version when applicable.
- PROPOSED: `PolicyVersion.authority_rank` is a deterministic ordinal used only among policies within the approved V1 hierarchy.
- CONFIRMED: A matter uses the policy version effective at `DecisionMatter.relevant_at`.
- CONFIRMED: A completed decision preserves the matter's `relevant_at`, the selected policy version, its own `created_at`, and its separate `decided_at`.
- CONFIRMED: Policy-version date ranges for the same policy may not overlap.
- CONFIRMED: Replacing a policy version does not silently rewrite historical decision records or automatically change their authority.
- CONFIRMED: An Authority Steward must explicitly question, supersede, or withdraw an affected decision through a separately recorded authority event.
- UNRESOLVED: The exact V1 policy hierarchy and meaning of `authority_rank` remain subject to Proposal `P2-01` review.

## 9. User Roles And Permissions

- CONFIRMED: A `Matter Submitter` may create a matter, provide facts and evidence, request analysis, and view its packet and brief.
- CONFIRMED: A `Decision Reviewer` is an authorized human who may record the downstream outcome and explicitly confirm write-back.
- CONFIRMED: An `Authority Steward` is an authorized human who may activate, question, supersede, or withdraw decision authority under deterministic rules.
- CONFIRMED: An `Automated Client` may submit matters and consume packets under delegated permission but may not confirm write-back or alter authority.
- CONFIRMED: A `Read-Only Auditor` may inspect matters, decision records, sources, citations, relationships, authority history, and confirmation events but may not mutate them.
- CONFIRMED: One human may hold both Decision Reviewer and Authority Steward roles in the V1 demo, but confirmation and every authority action remain separate timestamped audit events.
- CONFIRMED: Activation cannot occur implicitly during confirmation.
- CONFIRMED: Only a Decision Reviewer may confirm that a downstream outcome should enter the corpus.
- CONFIRMED: Only an Authority Steward may change authority state or confirm a persisted precedent relationship.
- CONFIRMED: A Matter Submitter or Automated Client may propose facts and relationships but may not mark them confirmed or authoritative.
- CONFIRMED: Models have no user role and receive no direct mutation permission.
- UNRESOLVED: Identity provider, authentication mechanism, tenancy, and technical authorization enforcement belong to `PREREQ-003`.

## 10. Human-Confirmation Workflow

1. CONFIRMED: Finné Memory produces a cited precedent packet without making the final supplier decision.
2. CONFIRMED: A downstream authorized person or system makes the approval, rejection, or escalation decision outside Finné Memory.
3. CONFIRMED: A Decision Reviewer records the outcome, rationale summary, decision-maker reference, `decided_at`, facts, evidence, policy versions selected by `relevant_at`, and packet reference.
4. CONFIRMED: Finné Memory validates identifiers, required provenance, source and evidence references, policy dates, citation edges, and outcome completeness.
5. CONFIRMED: The Decision Reviewer explicitly attests that the record accurately represents the completed external decision and confirms corpus entry in a timestamped audit event.
6. CONFIRMED: Successful confirmation creates an immutable `DecisionRecord` version in `draft` authority state and records its separate `created_at`.
7. CONFIRMED: An Authority Steward separately reviews the draft and either activates or withdraws it through a later timestamped authority event; the draft history is not overwritten.
8. CONFIRMED: If one human holds both roles in the V1 demo, confirmation and authority action remain distinct events and activation cannot occur implicitly.
9. CONFIRMED: Validation failure prevents record creation and preserves the matter and proposed write-back for correction.
10. CONFIRMED: An Automated Client or model cannot perform the human-confirmation or authority-activation steps.

## 11. Synthetic Demo Corpus

### Policy Fixtures

- PROPOSED: `POL-BO/V1` is effective from `2025-01-01` until the exclusive end date `2025-07-01` and permits escalation while incomplete beneficial-ownership evidence is resolved under the original supplier-onboarding rule.
- PROPOSED: `POL-BO/V2` is effective from `2025-07-01` with no end date and requires independent beneficial-ownership evidence for privately held suppliers before approval; unresolved mandatory evidence requires escalation.
- PROPOSED: `POL-BO/V2` supersedes `POL-BO/V1` without rewriting decisions made while V1 was effective.
- PROPOSED: Every policy and record below uses synthetic sources and evidence.

### Decision Fixtures

- PROPOSED: `DR-001` is the original baseline decision: a privately held low-risk supplier lacked an independent registry extract, supplied an attestation, and was escalated under `POL-BO/V1`; its authority is `superseded` by `DR-004`.
- PROPOSED: `DR-002` follows `DR-001`: a second privately held supplier with materially similar missing ownership evidence was escalated under `POL-BO/V1`; it has a validated `follows` relationship to `DR-001` and is `superseded` by `DR-004`.
- PROPOSED: `DR-003` distinguishes the private-supplier baseline: a supplier owned by a publicly listed parent relied on authoritative public filings and was approved under the listed-company treatment in `POL-BO/V2`; it is `active` and has a validated `distinguishes` relationship to `DR-004`.
- PROPOSED: `DR-004` establishes the current baseline: a privately held supplier with incomplete independent beneficial-ownership evidence was escalated under `POL-BO/V2`; it is `active` and has validated `supersedes` relationships to `DR-001` and `DR-002`.
- PROPOSED: `DR-005` is highly similar but inactive: a privately held medium-risk supplier with incomplete independent evidence and only a self-attestation was approved, then the record was `withdrawn` after the supporting attestation was found unreliable.
- PROPOSED: `DR-006` is less similar but active: a privately held supplier had complete ownership evidence but an unresolved control-chain risk and was escalated under `POL-BO/V2`; it remains `active`.

### Current Matter Fixture

- PROPOSED: `MAT-001` concerns a privately held medium-risk supplier seeking urgent onboarding with a self-attestation, a partial registry extract, and one beneficial owner whose identity remains unverified.
- PROPOSED: `MAT-001` has no outcome when submitted to Finné Memory.
- CONFIRMED: The expected packet retrieves `DR-005` because of its high factual similarity, visibly marks it `withdrawn`, and excludes it from active authority.
- CONFIRMED: The expected packet presents `DR-004` as the active current baseline and explains its material factual and policy relevance.
- CONFIRMED: The expected packet uses `DR-003` to explain why the listed-company exception does not apply and includes `DR-006` only as lower-similarity active context.
- CONFIRMED: The expected packet does not approve, reject, or escalate `MAT-001`.
- UNRESOLVED: Exact fact, evidence, source, citation, and rationale fixture contents must be completed after Arko approves the corpus design.

## 12. Deterministic Invariants

- PROPOSED: Every persisted identifier referenced by a record, packet, citation, relationship, or state event resolves to an existing record of the declared type.
- PROPOSED: Every `DecisionRecord` represents a completed external outcome and contains authorized human confirmation.
- PROPOSED: Every `DecisionRecord` begins in `draft`; no write-back begins as `active`.
- PROPOSED: Only `active` records are eligible to be represented as active authority.
- PROPOSED: `draft`, `questioned`, `superseded`, and `withdrawn` records remain visible but are ineligible as active authority.
- PROPOSED: Similarity score, similarity rank, precedent relationship, and outcome never determine authority state by themselves.
- PROPOSED: Authority state never determines factual similarity or supplier outcome.
- PROPOSED: A `superseded` record has at least one existing successor and validated `supersedes` relationship.
- PROPOSED: A valid `supersedes` operation updates the relationship and target authority state as one logical operation.
- PROPOSED: Terminal authority states cannot transition to another state; corrections create new immutable versions.
- PROPOSED: Policy date ranges for one policy do not overlap, and historical decisions retain their original policy-version references.
- PROPOSED: A model-generated fact retains `model_extracted` provenance and cannot be marked confirmed by the model.
- PROPOSED: An active decision may display unverified or disputed facts for context, but only supported or confirmed facts may support its authoritative rationale or precedent relationships.
- CONFIRMED: A model cannot create a valid source ID, valid citation, persisted precedent relationship, authority transition, human confirmation, or final outcome.
- PROPOSED: A final packet contains only resolvable citations marked valid by deterministic validation.
- PROPOSED: Invalid or unresolved citations are surfaced as failures or limitations and never rendered as supporting authority.
- PROPOSED: Every mutation of confirmation, record version, citation relationship, precedent relationship, or authority state is attributable to an actor and time.
- CONFIRMED: No record or workflow contains payment, x402, escrow, refund, settlement, transaction-performance verification, or dispute-resolution behavior.

## 13. Decision Package Resolution

- CONFIRMED: `P2-01` is approved as amended in `PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`.
- CONFIRMED: `P2-02` approves immutable decision-record versions and append-only authority history rather than in-place historical rewrites.
- CONFIRMED: `P2-03` approves `draft`, `active`, `questioned`, `superseded`, and `withdrawn` as the complete V1 authority vocabulary, with only `active` eligible as active authority.
- CONFIRMED: `P2-04` approves the documented authority transitions, including terminal `superseded` and `withdrawn` states and mandatory successor relationships for supersession.
- CONFIRMED: `P2-05` approves that unverified or disputed facts remain visible with status and provenance but cannot support an authoritative conclusion.
- CONFIRMED: `P2-06` approves citations and precedent-treatment relationships as separate validated objects, with human confirmation required before a suggested precedent relationship is persisted.
- CONFIRMED: `P2-07` approves one explicit `DecisionMatter.relevant_at` date for policy selection, inclusive `effective_from`, exclusive `effective_to`, non-overlapping versions, and separate record `created_at` and `decided_at` values.
- CONFIRMED: `P2-08` approves that a new policy version does not automatically alter decision authority; an Authority Steward must act explicitly.
- CONFIRMED: `P2-09` approves the role permissions and permits one demo user to hold Decision Reviewer and Authority Steward roles while requiring separate timestamped audit events and prohibiting implicit activation.
- CONFIRMED: `P2-10` approves human-confirmed write-back as an immutable `draft` version followed by a separately recorded Authority Steward event that does not overwrite draft history.
- CONFIRMED: `P2-11` is approved as amended in `PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`.
- CONFIRMED: `P2-12` approves retrieval of similar-but-withdrawn `DR-005` with visible exclusion from active authority, presentation of `DR-004` as active baseline, and no Finné Memory-generated supplier outcome.
- CONFIRMED: `P2-13` is approved as amended in the final deterministic invariants in `PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`.
- CONFIRMED: All decision packages are reconciled; this proposal remains only as chronological planning history.
