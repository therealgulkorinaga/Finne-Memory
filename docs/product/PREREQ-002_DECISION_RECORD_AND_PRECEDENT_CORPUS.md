# PREREQ-002: Decision Record And Precedent Corpus

## Status

- CONFIRMED: This product and data-contract specification is approved for planning purposes.
- CONFIRMED: The synthetic seed-data appendix and traceability review are present and valid; this specification closes `PREREQ-002`.
- CONFIRMED: This specification does not authorize implementation; `PREREQ-003` remains the next planning gate.

## Goal

- CONFIRMED: Define immutable matter and decision versions, supporting facts and evidence, policy selection, authority history, citations, precedent relationships, permissions, and a complete synthetic supplier-onboarding corpus.
- CONFIRMED: Preserve strict separation among factual similarity, recorded authority, and downstream outcome.

## Actors

- CONFIRMED: `Matter Submitter` may create matter versions, provide facts and evidence, request analysis, and view packets.
- CONFIRMED: `Decision Reviewer` may record an external outcome and explicitly confirm creation of an immutable draft decision version.
- CONFIRMED: `Authority Steward` may create authority events and confirm persisted precedent relationships.
- CONFIRMED: `Automated Client` may submit matters and consume packets but may not confirm write-back, persist precedent relationships, or create authority events.
- CONFIRMED: `Read-Only Auditor` may inspect all records and events but may not mutate them.
- CONFIRMED: One demo user may hold both Decision Reviewer and Authority Steward roles, but confirmation and authority actions remain separate timestamped events.
- CONFIRMED: Models are not actors and receive no mutation permission.

## Field Notation

- CONFIRMED: `R` means required, `O` means optional, and `C` means conditionally required.
- CONFIRMED: `ID` values are immutable identifiers; exact encoding is deferred to `PREREQ-003`.
- CONFIRMED: Dates select policy applicability, while timestamps preserve event chronology.

## Authoritative Object Dictionary

| Object | Fields with type and requirement | Purpose |
| --- | --- | --- |
| `DecisionMatter` | `matter_id: ID [R]`; `matter_version_id: ID [R]`; `matter_version: positive integer [R]`; `previous_matter_version_id: ID [O]`; `domain: enum [R]`; `question: string [R]`; `submitted_by: ActorID [R]`; `submitted_at: timestamp [R]`; `relevant_at: date [R]`; `fact_ids: list<FactID> [R, non-empty]`; `policy_version_ids: list<PolicyVersionID> [R after selection, non-empty]`; `is_synthetic: boolean [R]` | One immutable version of a matter before an external outcome exists |
| `DecisionRecord` | `decision_id: ID [R]`; `decision_version_id: globally unique ID [R]`; `record_version: positive integer [R]`; `previous_decision_version_id: DecisionVersionID [O]`; `matter_version_id: MatterVersionID [R]`; `domain: enum [R]`; `question: string [R]`; `relevant_at: date [R]`; `created_at: timestamp [R]`; `decided_at: timestamp [R]`; `fact_ids: list<FactID> [R, non-empty]`; `policy_version_ids: list<PolicyVersionID> [R, non-empty]`; `outcome: DecisionOutcome [R]`; `precedent_packet_id: PacketID [O]`; `confirmation: HumanConfirmation [R]`; `provenance: RecordProvenance [R]`; `is_synthetic: boolean [R]` | Immutable version of a completed downstream decision admitted to the corpus |
| `DecisionOutcome` | `outcome_type: enum(approved,rejected,escalated) [R]`; `rationale_summary: string [R]`; `decided_by: ActorID or ExternalSystemID [R]` | External supplier outcome, never Finné Memory's decision |
| `HumanConfirmation` | `confirmation_id: ID [R]`; `decision_version_id: DecisionVersionID [R]`; `confirmed_by: HumanActorID [R]`; `confirmed_at: timestamp [R]`; `attestation: string [R]` | Separate human write-back confirmation event |
| `RecordProvenance` | `created_by: ActorID [R]`; `origin: enum(human_entry,automated_client,imported,synthetic_seed) [R]`; `source_system_reference: string [O]` | Record-version origin and attribution |
| `Fact` | `fact_id: ID [R]`; `applies_to_version_id: MatterVersionID or DecisionVersionID [R]`; `subject: string or EntityID [R]`; `predicate: controlled string [R]`; `value: typed value [R]`; `value_type: enum(text,boolean,number,date,category) [R]`; `origin: enum(human_supplied,system_supplied,model_extracted) [R]`; `verification_status: enum(unverified,supported,disputed,confirmed) [R]`; `extraction_confidence: decimal 0..1 [C for model_extracted]`; `recorded_at: timestamp [R]`; `recorded_by: ActorID [R]` | Immutable structured assertion with provenance and verification status |
| `Evidence` | `evidence_id: ID [R]`; `source_id: SourceID [R]`; `description: string [R]`; `locator: string [O]`; `observed_at: timestamp [O]`; `added_by: ActorID [R]` | Bounded evidence item from exactly one source |
| `FactEvidenceLink` | `fact_evidence_link_id: ID [R]`; `fact_id: FactID [R]`; `evidence_id: EvidenceID [R]`; `relationship_type: enum(supports,contradicts) [R]`; `created_by: ActorID [R]`; `created_at: timestamp [R]` | Canonical fact-to-evidence relationship; reverse collections are derived only |
| `Source` | `source_id: ID [R]`; `source_type: enum(policy,registry_record,supplier_document,attestation,risk_assessment,decision_record,other) [R]`; `title: string [R]`; `issuer: string [O]`; `reference: URI or fixture reference [R]`; `issued_at: timestamp [O]`; `retrieved_at: timestamp [O]`; `content_fingerprint: string [O]`; `is_synthetic: boolean [R]` | Deterministic source identity and provenance |
| `PolicyVersion` | `policy_id: ID [R]`; `policy_version_id: globally unique ID [R]`; `title: string [R]`; `source_id: SourceID [R]`; `issued_at: timestamp [R]`; `effective_from: date [R, inclusive]`; `effective_to: date [O, exclusive]`; `supersedes_policy_version_id: PolicyVersionID [O]` | Immutable policy version selected using matter `relevant_at`; V1 has no authority rank |
| `AuthorityEvent` | `authority_event_id: ID [R]`; `decision_version_id: DecisionVersionID [R]`; `previous_status: AuthorityStatus [O for initial draft]`; `new_status: AuthorityStatus [R]`; `effective_at: timestamp [R]`; `recorded_at: timestamp [R]`; `changed_by: AuthorityStewardID [R]`; `reason: string [R]`; `successor_decision_version_ids: list<DecisionVersionID> [C for superseded, otherwise empty]` | Canonical append-only authority history for one exact decision version |
| `AuthorityState` | `status: AuthorityStatus [R]`; `effective_at: timestamp [R]`; `reason: string [R]`; `changed_by: AuthorityStewardID [R]`; `successor_decision_version_ids: list<DecisionVersionID> [C]`; `previous_status: AuthorityStatus [O]` | Derived current view from the latest valid `AuthorityEvent`; never canonical mutable record content |
| `CitationEdge` | `citation_id: ID [R]`; `from_type: enum(packet,decision_version,precedent_relationship) [R]`; `from_id: typed ID [R]`; `target_type: enum(decision_version,policy_version,source,evidence) [R]`; `target_id: typed ID [R]`; `claim: string [R]`; `created_by: ActorID [R]`; `created_at: timestamp [R]`; `validated_at: timestamp [R]` | Successfully validated citation only |
| `CitationAttemptAuditEvent` | `citation_attempt_event_id: ID [R]`; `from_type: enum(packet,decision_version,precedent_relationship) [R]`; `from_id: typed ID [R]`; `attempted_target_type: string [R]`; `attempted_target_id: string [R]`; `claim: string [R]`; `result: enum(rejected,unresolved) [R]`; `reason: string [R]`; `recorded_at: timestamp [R]`; `actor_id: ActorID [R]` | Audit record for a citation attempt that does not enter the domain citation graph |
| `PrecedentRelationship` | `relationship_id: ID [R]`; `from_decision_version_id: DecisionVersionID [R]`; `to_decision_version_id: DecisionVersionID [R]`; `relationship_type: enum(follows,distinguishes,questions,supersedes) [R]`; `rationale: string [R]`; `fact_ids: list<FactID> [R, non-empty]`; `citation_ids: list<CitationID> [R, non-empty]`; `confirmed_by: HumanActorID [R]`; `confirmed_at: timestamp [R]` | Canonical human-confirmed treatment between exact decision versions |

## Versioning Rules

- CONFIRMED: `matter_id` is stable across matter versions; `matter_version_id` identifies one globally unique immutable version; `matter_version` is its human-readable sequence number.
- CONFIRMED: Once a packet references a matter version, edits create a new matter version and cannot change its `relevant_at`, facts, or policy selection retrospectively.
- CONFIRMED: Every generated packet references exactly one `matter_version_id`.
- CONFIRMED: `decision_id` is stable across decision versions; `decision_version_id` identifies one globally unique immutable version; `record_version` is its human-readable sequence number.
- CONFIRMED: Every exact-version reference uses `decision_version_id`, including prior-version references, citations, precedent relationships, authority events, and successor references.
- CONFIRMED: A decision correction creates a new version with `previous_decision_version_id`; it does not overwrite prior content or history.
- CONFIRMED: A decision record copies `relevant_at` from its originating matter version and separately preserves `created_at` and `decided_at`.

## Fact And Evidence Rules

- CONFIRMED: `FactEvidenceLink` is the only canonical fact-to-evidence relation.
- CONFIRMED: Fact and evidence reverse collections, if exposed, are derived and cannot be edited independently.
- CONFIRMED: Unverified or disputed facts remain visible with status and provenance but cannot support an authoritative conclusion.
- CONFIRMED: Only supported or confirmed facts may support active authority or a persisted precedent relationship.
- CONFIRMED: A model-extracted fact must cite evidence, retain `model_extracted` provenance, and cannot be confirmed by the model.

## Authority Vocabulary

- CONFIRMED: `draft` is visible but ineligible as active authority.
- CONFIRMED: `active` is eligible as authority, subject to `relevant_at` and policy checks.
- CONFIRMED: `questioned` is visible but ineligible pending resolution.
- CONFIRMED: `superseded` is visible but ineligible because a validated successor replaced it.
- CONFIRMED: `withdrawn` is visible but ineligible without requiring a successor.
- CONFIRMED: Only `active` is eligible as active authority.

## Authority Transitions

| From | To | Required conditions |
| --- | --- | --- |
| No prior state | `draft` | Decision Reviewer confirmation creates immutable draft and initial `AuthorityEvent` |
| `draft` | `active` | Separate Authority Steward event; required provenance, policy, citations, confirmation, and material facts validate |
| `draft` | `withdrawn` | Separate Authority Steward event with reason |
| `active` | `questioned` | Separate event identifying material concern |
| `active` | `superseded` | Validated successor version and atomic `supersedes` relationship |
| `active` | `withdrawn` | Separate event with reason |
| `questioned` | `active` | Resolution recorded and validation passes |
| `questioned` | `superseded` | Validated successor version and atomic `supersedes` relationship |
| `questioned` | `withdrawn` | Separate event with reason |
| `superseded` | Any | Forbidden; terminal |
| `withdrawn` | Any | Forbidden; terminal |
| Any unlisted pair | Any | Forbidden |

## Citation And Relationship Rules

- CONFIRMED: Only successfully validated `CitationEdge` objects enter the domain citation graph.
- CONFIRMED: Rejected or unresolved attempts create `CitationAttemptAuditEvent` objects and never appear as supporting citations.
- CONFIRMED: A citation to a decision version may remain valid for historical context even when that decision is not active; authority eligibility must be displayed separately.
- CONFIRMED: Models may suggest citations or relationships but may not create valid IDs, persist relationships, or confirm them.
- CONFIRMED: A persisted `PrecedentRelationship` requires deterministic reference validation and authorized human confirmation.
- CONFIRMED: `follows`, `distinguishes`, and `questions` do not automatically change authority.
- CONFIRMED: Creating a `supersedes` relationship and its target `superseded` authority event is one logical operation.

## Policy-Version Rules

- CONFIRMED: `DecisionMatter.relevant_at` is the sole date used to select applicable policy versions and the authority snapshot for analysis.
- CONFIRMED: `effective_from` is inclusive; `effective_to` is exclusive; date ranges for one policy do not overlap.
- CONFIRMED: A new policy version does not rewrite historical decisions or automatically alter their authority.
- CONFIRMED: An Authority Steward must explicitly question, supersede, or withdraw affected decisions.
- CONFIRMED: V1 contains no policy hierarchy and no `authority_rank` field.

## Human-Confirmation Workflow

1. CONFIRMED: Finné Memory generates a cited packet for one immutable matter version and does not generate the final supplier outcome.
2. CONFIRMED: A downstream actor makes the approval, rejection, or escalation decision outside Finné Memory.
3. CONFIRMED: A Decision Reviewer records the external outcome, rationale, actor, `decided_at`, selected policy versions, facts, and packet reference.
4. CONFIRMED: Deterministic validation checks all IDs, policy dates, sources, citations, provenance, and outcome completeness.
5. CONFIRMED: The reviewer performs an explicit timestamped confirmation.
6. CONFIRMED: Confirmation creates one immutable draft `DecisionRecord` version and its initial draft `AuthorityEvent`.
7. CONFIRMED: Activation or withdrawal requires a later, separate, timestamped Authority Steward event.
8. CONFIRMED: Activation never occurs implicitly during confirmation, even when one human holds both roles.
9. CONFIRMED: Validation failure creates no decision record and leaves the proposed write-back available for correction.

## Deterministic Invariants

1. CONFIRMED: Every persisted reference resolves to an existing object of the declared type and exact version where versioned.
2. CONFIRMED: Every `DecisionRecord` represents a completed external outcome and contains authorized human confirmation.
3. CONFIRMED: Matter and decision versions are immutable; corrections create new globally unique version IDs and sequential version numbers.
4. CONFIRMED: Every decision version begins with a `draft` `AuthorityEvent`; no write-back begins as `active`.
5. CONFIRMED: Only `active` decision versions are eligible to be represented as active authority.
6. CONFIRMED: `draft`, `questioned`, `superseded`, and `withdrawn` versions remain visible but are ineligible as active authority.
7. CONFIRMED: Similarity, authority, precedent treatment, and outcome never determine one another automatically.
8. CONFIRMED: A superseded version has at least one existing successor `decision_version_id` and validated `supersedes` relationship.
9. CONFIRMED: Supersession relationship creation and the target authority event occur as one logical operation.
10. CONFIRMED: `superseded` and `withdrawn` are terminal; corrections create new versions rather than state reversal.
11. CONFIRMED: Policy ranges do not overlap, and historical decisions retain their original policy-version references.
12. CONFIRMED: `DecisionMatter.relevant_at` alone selects policy applicability; record `created_at` and `decided_at` remain distinct.
13. CONFIRMED: Every packet references one immutable `matter_version_id`.
14. CONFIRMED: A model-generated fact retains provenance and cannot be marked confirmed by a model.
15. CONFIRMED: Unverified or disputed facts remain visible but cannot support an authoritative conclusion or persisted precedent relationship.
16. CONFIRMED: Only valid citations enter the citation graph; invalid attempts remain separate audit events.
17. CONFIRMED: Every confirmation, version, citation, relationship, and authority event is attributable to an actor and time.
18. CONFIRMED: A model cannot create valid IDs, citations, persisted precedent relationships, authority events, human confirmations, or final outcomes.
19. CONFIRMED: Confirmation and activation are separate timestamped events; neither overwrites immutable decision content or prior history.
20. CONFIRMED: No object or workflow contains payment, x402, escrow, refund, settlement, transaction-performance verification, or dispute-resolution behavior.

## Synthetic Corpus

- CONFIRMED: The complete authoritative fixture definitions are in `PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`.
- CONFIRMED: The primary demo uses six decision fixtures, two policy versions, and `MAT-001`.
- CONFIRMED: Two additional non-primary lifecycle fixtures cover `draft` and `questioned` behavior without changing the six-record demo story.

## Acceptance Criteria

- CONFIRMED: The data dictionary contains every required object, field, type, and conditionality needed to instantiate the approved corpus.
- CONFIRMED: Every seed identifier and cross-reference validates against the dictionary.
- CONFIRMED: Every decision version has an external outcome, human confirmation, initial draft event, policy selected by `relevant_at`, facts, evidence links, sources, and valid citations.
- CONFIRMED: The six primary decisions demonstrate baseline, following, distinguishing, supersession, withdrawn-but-similar, and active-but-less-similar behavior.
- CONFIRMED: `MAT-001` retrieves `DR-005` because of similarity but excludes it from active authority, presents `DR-004` as active baseline, and has no Finné Memory-generated outcome.
- CONFIRMED: Lifecycle fixtures and transition cases cover every authority state and permitted transition.
- CONFIRMED: The traceability review maps this specification to the PRD and reports no dangling references or unresolved product decisions.

## Explicit Exclusions

- CONFIRMED: Physical serialization, database, runtime, API, framework, identity provider, deployment, identifier encoding, timestamp encoding, and fingerprint algorithm are deferred to `PREREQ-003`.
- CONFIRMED: Retrieval scoring, packet schema beyond exact matter-version reference, model provider, and UI behavior are outside the `PREREQ-002` data contract.
- CONFIRMED: Production data, multi-tenant behavior, and non-supplier domains are outside V1.
- CONFIRMED: Payments, x402, escrow, refunds, settlement, transaction verification, and disputes are excluded.
