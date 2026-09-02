# PREREQ-002 Review Packet

## Review Status

- CONFIRMED: This packet exposes the exact contents incorporated by decision packages `P2-01`, `P2-11`, and `P2-13` for review.
- CONFIRMED: Review is complete and all detected issues are resolved in `PREREQ-002_DECISION_RECORD_AND_PRECEDENT_CORPUS.md`, `PREREQ-002_SYNTHETIC_SEED_DATA_APPENDIX.md`, and `PREREQ-002_TRACEABILITY_REVIEW.md`.
- CONFIRMED: Tables and `UNRESOLVED` labels below preserve the pre-resolution review snapshot and are not the current authoritative contract.
- CONFIRMED: Previously approved amendments to `P2-05`, `P2-07`, `P2-09`, `P2-10`, and `P2-12` are incorporated.
- CONFIRMED: Arko approved the object model, fixture design, and invariant set with the ten specified resolutions.
- CONFIRMED: This packet does not authorize implementation; `PREREQ-003` remains the next planning gate.

## Complete Object And Field Table

| Object | Field | Type | Requirement | Purpose | Classification |
| --- | --- | --- | --- | --- | --- |
| `DecisionMatter` | `matter_id` | ID | Required | Stable matter identity | PROPOSED |
| `DecisionMatter` | `domain` | Enum | Required | `supplier_onboarding` in V1 | PROPOSED |
| `DecisionMatter` | `question` | String | Required | Decision question presented downstream | PROPOSED |
| `DecisionMatter` | `submitted_by` | Actor ID | Required | Human or automated submitter provenance | PROPOSED |
| `DecisionMatter` | `submitted_at` | Timestamp | Required | Time Sybill received the matter | PROPOSED |
| `DecisionMatter` | `relevant_at` | Date | Required | Sole date used to select policy version and authority snapshot | CONFIRMED |
| `DecisionMatter` | `fact_ids` | List of Fact IDs | Required, non-empty | Facts considered for retrieval and comparison | PROPOSED |
| `DecisionMatter` | `evidence_ids` | List of Evidence IDs | Optional | Evidence supplied with the matter | PROPOSED |
| `DecisionMatter` | `source_ids` | List of Source IDs | Optional | Sources supplied with the matter | PROPOSED |
| `DecisionMatter` | `policy_version_ids` | List of PolicyVersion IDs | Required after policy selection | Policies effective at `relevant_at` | PROPOSED |
| `DecisionMatter` | `status` | Enum: `open`, `packet_generated`, `closed` | Required | Matter lifecycle, separate from authority | PROPOSED |
| `DecisionMatter` | `packet_ids` | List of Packet IDs | Optional | Packets generated without implying an outcome | PROPOSED |
| `DecisionRecord` | `decision_id` | ID | Required | Stable decision identity | PROPOSED |
| `DecisionRecord` | `record_version` | Positive integer | Required | Immutable version number | CONFIRMED |
| `DecisionRecord` | `previous_version_id` | Decision-version reference | Conditional | Prior version when correcting a record | PROPOSED |
| `DecisionRecord` | `matter_id` | Matter ID | Required | Originating matter | PROPOSED |
| `DecisionRecord` | `domain` | Enum | Required | `supplier_onboarding` in V1 | PROPOSED |
| `DecisionRecord` | `question` | String | Required | Question answered by the downstream decision | PROPOSED |
| `DecisionRecord` | `relevant_at` | Date | Required | Immutable copy of originating matter's policy-selection date | PROPOSED |
| `DecisionRecord` | `created_at` | Timestamp | Required | Creation time of this immutable record version | CONFIRMED |
| `DecisionRecord` | `decided_at` | Timestamp | Required | Time the downstream decision was made | CONFIRMED |
| `DecisionRecord` | `fact_ids` | List of Fact IDs | Required, non-empty | Facts preserved with the decision | PROPOSED |
| `DecisionRecord` | `evidence_ids` | List of Evidence IDs | Required | Evidence considered | PROPOSED |
| `DecisionRecord` | `source_ids` | List of Source IDs | Required | Direct source references | PROPOSED |
| `DecisionRecord` | `policy_version_ids` | List of PolicyVersion IDs | Required, non-empty | Policies selected using matter `relevant_at` | PROPOSED |
| `DecisionRecord` | `outcome` | `DecisionOutcome` | Required | External outcome, separate from authority | PROPOSED |
| `DecisionRecord` | `precedent_packet_id` | Packet ID | Optional | Packet used by the downstream decision-maker | PROPOSED |
| `DecisionRecord` | `authority_state` | Derived `AuthorityState` | Derived, not canonical storage | Current state from latest valid authority event | PROPOSED |
| `DecisionRecord` | `authority_history` | List of AuthorityEvent IDs | Derived, non-empty | Append-only state history | CONFIRMED |
| `DecisionRecord` | `citation_edge_ids` | List of CitationEdge IDs | Optional | Validated citations made by this version | PROPOSED |
| `DecisionRecord` | `precedent_relationship_ids` | List of Relationship IDs | Derived | Relationships involving this decision | PROPOSED |
| `DecisionRecord` | `confirmation` | `HumanConfirmation` | Required | Human authorization for corpus entry | CONFIRMED |
| `DecisionRecord` | `provenance` | `RecordProvenance` | Required | Origin and creator attribution | PROPOSED |
| `DecisionRecord` | `is_synthetic` | Boolean | Required | Distinguishes fixtures from real records | PROPOSED |
| `DecisionOutcome` | `outcome_type` | Enum: `approved`, `rejected`, `escalated` | Required | External supplier outcome | PROPOSED |
| `DecisionOutcome` | `rationale_summary` | String | Required | Downstream rationale, not Sybill authority | PROPOSED |
| `DecisionOutcome` | `decided_by` | Actor or external-system ID | Required | Accountable downstream decision-maker | PROPOSED |
| `HumanConfirmation` | `confirmed_by` | Human actor ID | Required | Authorized Decision Reviewer | CONFIRMED |
| `HumanConfirmation` | `confirmed_at` | Timestamp | Required | Separate write-back confirmation event time | CONFIRMED |
| `HumanConfirmation` | `attestation` | String or fixed acknowledgement | Required | Confirms accurate representation of external decision | PROPOSED |
| `RecordProvenance` | `created_by` | Actor ID | Required | Actor preparing the record version | PROPOSED |
| `RecordProvenance` | `origin` | Enum: `human_entry`, `automated_client`, `imported`, `synthetic_seed` | Required | Record origin | PROPOSED |
| `RecordProvenance` | `source_system_reference` | String | Optional | External system-of-record reference | PROPOSED |
| `Fact` | `fact_id` | ID | Required | Stable fact identity | PROPOSED |
| `Fact` | `subject` | String or entity ID | Required | Entity or matter described | PROPOSED |
| `Fact` | `predicate` | String or controlled key | Required | Property asserted | PROPOSED |
| `Fact` | `value` | Typed value | Required | Asserted value | PROPOSED |
| `Fact` | `value_type` | Enum: `text`, `boolean`, `number`, `date`, `category` | Required | Interpretation of `value` | PROPOSED |
| `Fact` | `evidence_ids` | List of Evidence IDs | Required, may be empty while unverified | Supporting or conflicting evidence | PROPOSED |
| `Fact` | `source_ids` | List of Source IDs | Required, may be empty while unverified | Source provenance | PROPOSED |
| `Fact` | `origin` | Enum: `human_supplied`, `system_supplied`, `model_extracted` | Required | Creation provenance | PROPOSED |
| `Fact` | `verification_status` | Enum: `unverified`, `supported`, `disputed`, `confirmed` | Required | Evidence/confirmation state | PROPOSED |
| `Fact` | `extraction_confidence` | Decimal from 0 to 1 | Conditional: model-extracted only | Model confidence, never authority | PROPOSED |
| `Fact` | `recorded_at` | Timestamp | Required | Fact creation time | PROPOSED |
| `Fact` | `recorded_by` | Actor ID | Required | Actor or system recording the fact | PROPOSED |
| `Evidence` | `evidence_id` | ID | Required | Stable evidence identity | PROPOSED |
| `Evidence` | `source_id` | Source ID | Required | Exactly one originating source | PROPOSED |
| `Evidence` | `description` | String | Required | Bounded description of relevant content | PROPOSED |
| `Evidence` | `locator` | String | Optional | Reproducible page, section, or field location | PROPOSED |
| `Evidence` | `supports_fact_ids` | List of Fact IDs | Optional | Facts supported | PROPOSED |
| `Evidence` | `contradicts_fact_ids` | List of Fact IDs | Optional | Facts contradicted | PROPOSED |
| `Evidence` | `observed_at` | Timestamp | Optional | Evidence capture or observation time | PROPOSED |
| `Evidence` | `added_by` | Actor ID | Required | Supplying actor | PROPOSED |
| `Source` | `source_id` | ID | Required | Deterministic source identity | PROPOSED |
| `Source` | `source_type` | Enum: `policy`, `registry_record`, `supplier_document`, `attestation`, `risk_assessment`, `decision_record`, `other` | Required | Source category | PROPOSED |
| `Source` | `title` | String | Required | Human-readable source name | PROPOSED |
| `Source` | `issuer` | String | Optional | Originating organization or person | PROPOSED |
| `Source` | `reference` | URI or fixture reference | Required | Reproducible source location | PROPOSED |
| `Source` | `issued_at` | Timestamp | Optional | Source issuance time | PROPOSED |
| `Source` | `retrieved_at` | Timestamp | Optional | Source retrieval time | PROPOSED |
| `Source` | `content_fingerprint` | String | Optional in V1 | Detects substituted content without choosing algorithm | PROPOSED |
| `Source` | `is_synthetic` | Boolean | Required | Marks demo fixtures | PROPOSED |
| `AuthorityState` | `status` | Authority enum | Required | Derived current eligibility state | CONFIRMED |
| `AuthorityState` | `effective_at` | Timestamp | Required | Effective time of latest authority event | CONFIRMED |
| `AuthorityState` | `reason` | String | Required after initial draft | Human-readable transition reason | CONFIRMED |
| `AuthorityState` | `changed_by` | Human actor ID | Required | Authority Steward responsible | CONFIRMED |
| `AuthorityState` | `successor_decision_ids` | List of Decision IDs | Required only when superseded | Validated successors | CONFIRMED |
| `AuthorityState` | `previous_status` | Authority enum | Optional for initial draft | Prior state | CONFIRMED |
| `AuthorityEvent` | `authority_event_id` | ID | Required | Stable audit-event identity | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `decision_id` | Decision ID | Required | Decision whose authority changed | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `previous_status` | Authority enum | Optional for initial draft | State before event | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `new_status` | Authority enum | Required | State after event | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `effective_at` | Timestamp | Required | When the state change takes effect | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `recorded_at` | Timestamp | Required | When the event was recorded | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `changed_by` | Human actor ID | Required | Authority Steward responsible | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `reason` | String | Required | Reason for change | UNRESOLVED: missing from original object model |
| `AuthorityEvent` | `successor_decision_ids` | List of Decision IDs | Required only for superseded | Validated successor records | UNRESOLVED: missing from original object model |
| `CitationEdge` | `citation_id` | ID | Required | Stable citation identity | PROPOSED |
| `CitationEdge` | `from_id` | Decision or Packet ID | Required | Artifact making the cited claim | PROPOSED |
| `CitationEdge` | `target_type` | Enum: `decision`, `policy_version`, `source`, `evidence` | Required | Target category | PROPOSED |
| `CitationEdge` | `target_id` | Typed target ID | Required | Existing deterministic target | PROPOSED |
| `CitationEdge` | `claim` | String | Required | Proposition supported | PROPOSED |
| `CitationEdge` | `created_by` | Actor ID | Required | Citation creator provenance | PROPOSED |
| `CitationEdge` | `created_at` | Timestamp | Required | Citation creation time | PROPOSED |
| `CitationEdge` | `validation_status` | Enum: `valid`, `invalid` | Required | Referential and eligibility validation result | UNRESOLVED: invalid-edge persistence unclear |
| `PrecedentRelationship` | `relationship_id` | ID | Required | Stable relationship identity | PROPOSED |
| `PrecedentRelationship` | `from_decision_id` | Decision ID | Required | Later decision applying treatment | PROPOSED |
| `PrecedentRelationship` | `to_decision_id` | Decision ID | Required | Earlier decision being treated | PROPOSED |
| `PrecedentRelationship` | `relationship_type` | Enum: `follows`, `distinguishes`, `questions`, `supersedes` | Required | Treatment of prior decision | CONFIRMED |
| `PrecedentRelationship` | `rationale` | String | Required | Why the treatment applies | PROPOSED |
| `PrecedentRelationship` | `fact_ids` | List of Fact IDs | Required, non-empty | Material facts supporting treatment | PROPOSED |
| `PrecedentRelationship` | `citation_ids` | List of Citation IDs | Required, non-empty | Validated supporting citations | PROPOSED |
| `PrecedentRelationship` | `confirmed_by` | Human actor ID | Required | Human confirmation before persistence | CONFIRMED |
| `PrecedentRelationship` | `confirmed_at` | Timestamp | Required | Confirmation event time | CONFIRMED |
| `PolicyVersion` | `policy_id` | ID | Required | Stable policy-family identity | PROPOSED |
| `PolicyVersion` | `version_id` | ID | Required | Immutable policy-version identity | PROPOSED |
| `PolicyVersion` | `title` | String | Required | Policy name | PROPOSED |
| `PolicyVersion` | `source_id` | Source ID | Required | Authoritative policy source | PROPOSED |
| `PolicyVersion` | `issued_at` | Timestamp | Required | Publication time | PROPOSED |
| `PolicyVersion` | `effective_from` | Date | Required | Inclusive start date | CONFIRMED |
| `PolicyVersion` | `effective_to` | Date | Optional | Exclusive end date | CONFIRMED |
| `PolicyVersion` | `supersedes_version_id` | PolicyVersion ID | Optional | Immediately prior policy version | PROPOSED |
| `PolicyVersion` | `authority_rank` | Integer | Required in current proposal | Resolves hierarchy among policies | UNRESOLVED: hierarchy meaning undefined |

## Complete Fixture Table

| ID | Kind and `relevant_at`/effective dates | Core rule or facts | Outcome | Authority | Relationships and demo purpose | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| `POL-BO/V1` | Policy; `[2025-01-01, 2025-07-01)` | Original rule permits escalation while incomplete beneficial-ownership evidence is resolved | N/A | Policy version, not decision authority | Prior policy context; superseded by V2 without rewriting history | PROPOSED |
| `POL-BO/V2` | Policy; `[2025-07-01, open)` | Independent beneficial-ownership evidence required before approving privately held suppliers; unresolved mandatory evidence requires escalation | N/A | Policy version, not decision authority | Current policy context; supersedes V1 | PROPOSED |
| `DR-001` | Decision; `2025-02-10` | Private; low risk; attestation present; independent registry extract missing | Escalated | `superseded` | Original baseline; successor `DR-004` | PROPOSED |
| `DR-002` | Decision; `2025-04-22` | Private; low risk; ownership evidence materially similar to DR-001 and incomplete | Escalated | `superseded` | `follows DR-001`; successor `DR-004` | PROPOSED |
| `DR-003` | Decision; `2025-08-14` | Publicly listed parent; authoritative public filings available; private-company form absent | Approved | `active` | `distinguishes DR-004`; demonstrates exception | PROPOSED |
| `DR-004` | Decision; `2025-07-15` | Private; independent beneficial-ownership evidence incomplete under V2 | Escalated | `active` | `supersedes DR-001` and `DR-002`; current baseline | PROPOSED |
| `DR-005` | Decision; `2025-08-02` | Private; medium risk; only self-attestation; independent evidence missing; attestation later found unreliable | Approved | `withdrawn` | Highly similar to MAT-001; retrievable but visibly excluded from active authority | PROPOSED corpus / CONFIRMED packet treatment |
| `DR-006` | Decision; `2025-09-03` | Private; ownership evidence complete; separate control-chain risk unresolved | Escalated | `active` | Less similar active context | PROPOSED |
| `MAT-001` | Current matter; `2025-10-01` | Private; medium risk; urgent onboarding; self-attestation; partial registry extract; one beneficial owner unverified | None; Sybill must not produce one | N/A | Retrieve DR-005 but exclude it from authority; present DR-004 as active baseline | PROPOSED fixture / CONFIRMED packet treatment |

## Complete Authority-Transition Table

| From | To | Permitted | Required conditions | Classification |
| --- | --- | --- | --- | --- |
| No prior state | `draft` | Yes | Decision Reviewer confirmation creates immutable draft version and initial authority event | CONFIRMED |
| `draft` | `active` | Yes | Separate Authority Steward event; required sources, policy, citations, provenance, confirmation, and material facts validated | CONFIRMED |
| `draft` | `withdrawn` | Yes | Separate Authority Steward event with reason | CONFIRMED |
| `active` | `questioned` | Yes | Separate Authority Steward event identifying material concern | CONFIRMED |
| `active` | `superseded` | Yes | At least one validated successor and atomic `supersedes` relationship | CONFIRMED |
| `active` | `withdrawn` | Yes | Separate Authority Steward event with reason | CONFIRMED |
| `questioned` | `active` | Yes | Concern resolution recorded and validation passes | CONFIRMED |
| `questioned` | `superseded` | Yes | At least one validated successor and atomic `supersedes` relationship | CONFIRMED |
| `questioned` | `withdrawn` | Yes | Separate Authority Steward event with reason | CONFIRMED |
| `superseded` | Any state | No | Terminal; correction requires a new immutable record version | CONFIRMED |
| `withdrawn` | Any state | No | Terminal; correction requires a new immutable record version | CONFIRMED |
| Any unlisted pair | Any state | No | No-op updates are not transitions | CONFIRMED |

## Deterministic Invariants Verbatim

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

## Resolved Review Findings

The following findings were unresolved when first detected. Every proposed resolution shown below was subsequently approved and incorporated into the authoritative `PREREQ-002` outputs.

| Issue | Why it matters | Proposed resolution | Classification |
| --- | --- | --- | --- |
| `previous_version_id` had no standalone version identifier to target | A version number alone is ambiguous without its decision | Added immutable `decision_version_id`; exact-version references use it | CONFIRMED / RESOLVED |
| Immutable `DecisionRecord` previously embedded mutable current authority and relationship lists | Hidden mutation would violate the approved history rule | Kept immutable decision content canonical; current authority and relationships are derived from append-only objects | CONFIRMED / RESOLVED |
| The amendment required timestamped authority audit events, but `AuthorityEvent` was not defined | Confirmation and activation cannot be independently audited without an event object | Added the required `AuthorityEvent` object and approved fields | CONFIRMED / RESOLVED |
| `DecisionMatter.relevant_at` selected policy, but matter mutability was unspecified | Editing `relevant_at` after packet generation could change policy context silently | Added immutable matter versions; packets bind one exact version and records preserve `relevant_at` | CONFIRMED / RESOLVED |
| Fact-to-evidence links were stored on both `Fact` and `Evidence` | Divergent bidirectional lists could contradict each other | Added canonical `FactEvidenceLink`; reverse collections are derived views | CONFIRMED / RESOLVED |
| `CitationEdge.validation_status` permitted persisted invalid edges while final artifacts permitted only valid citations | It was unclear whether invalid attempts belonged in the domain model or only an audit log | Persist only validated citation edges; audit rejected or unresolved attempts separately | CONFIRMED / RESOLVED |
| `PolicyVersion.authority_rank` was required but the V1 hierarchy was undefined | An unexplained rank would create hidden authority behavior | Removed `authority_rank` from V1 | CONFIRMED / RESOLVED |
| Exact fixture facts, evidence IDs, source IDs, citations, and rationale text were not enumerated | The fixture table defined scenarios but not complete seed records | Added and validated the complete synthetic seed-data appendix | CONFIRMED / RESOLVED |
| No `draft` or `questioned` decision appeared in the six-record demo corpus | Those approved states would lack an end-to-end fixture | Added two non-primary lifecycle fixtures without changing the six-record demo story | CONFIRMED / RESOLVED |
| Source fingerprint behavior and identifier/timestamp encodings were not selected | These affect implementation but not current product semantics | Deferred algorithms and physical encodings to `PREREQ-003` while preserving semantic requirements | CONFIRMED / DEFERRED |
