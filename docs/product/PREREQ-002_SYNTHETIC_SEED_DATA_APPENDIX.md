# PREREQ-002 Synthetic Seed-Data Appendix

## Status And Conventions

- CONFIRMED: Every item in this appendix is synthetic and exists only to instantiate and test the approved V1 precedent corpus.
- CONFIRMED: This validated appendix is an authoritative output of the completed `PREREQ-002` planning gate.
- CONFIRMED: All dates use `YYYY-MM-DD`; all timestamps use UTC ISO-8601 notation.
- CONFIRMED: `PV-BO-001` and `PV-BO-002` are exact policy-version identifiers.
- CONFIRMED: `MV-*` identifiers are immutable matter versions and `DV-*` identifiers are immutable decision versions.
- CONFIRMED: The six primary demo decisions are `DV-001-V1` through `DV-006-V1`; `DV-007-V1` and `DV-008-V1` are non-primary lifecycle fixtures.

## Actors

| Actor ID | Role | Purpose |
| --- | --- | --- |
| `ACT-SEED` | Synthetic seed system | Creates fixture objects only |
| `ACT-REVIEWER` | Decision Reviewer | Records external outcomes and confirms write-back |
| `ACT-STEWARD` | Authority Steward | Creates authority events and confirms relationships |
| `ACT-AUDITOR` | Read-Only Auditor | Reviews corpus and history without mutation |

## Policy Versions

| Policy version | Policy ID | Source | Issued | Effective interval | Supersedes | Rule summary |
| --- | --- | --- | --- | --- | --- | --- |
| `PV-BO-001` | `POL-BO` | `SRC-POL-001` | `2024-12-15T09:00:00Z` | `[2025-01-01, 2025-07-01)` | None | `BO-1A`: incomplete independent beneficial-ownership evidence requires escalation; `BO-1B`: an attestation may support review but cannot alone support approval |
| `PV-BO-002` | `POL-BO` | `SRC-POL-002` | `2025-06-15T09:00:00Z` | `[2025-07-01, open)` | `PV-BO-001` | `BO-2A`: privately held suppliers require independent beneficial-ownership evidence before approval; `BO-2B`: verified public filings satisfy the listed-parent exception; `BO-2C`: unresolved control-chain risk requires escalation |

## Matter Versions

| Matter | Immutable version | Seq. | Previous | `relevant_at` | Facts | Policy | Submitted at |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `MTR-001` | `MV-001-V1` | 1 | None | `2025-02-10` | `F-001..F-004` | `PV-BO-001` | `2025-02-10T09:00:00Z` |
| `MTR-002` | `MV-002-V1` | 1 | None | `2025-04-22` | `F-005..F-008` | `PV-BO-001` | `2025-04-22T09:00:00Z` |
| `MTR-003` | `MV-003-V1` | 1 | None | `2025-08-14` | `F-009..F-012` | `PV-BO-002` | `2025-08-14T09:00:00Z` |
| `MTR-004` | `MV-004-V1` | 1 | None | `2025-07-15` | `F-013..F-016` | `PV-BO-002` | `2025-07-15T09:00:00Z` |
| `MTR-005` | `MV-005-V1` | 1 | None | `2025-08-02` | `F-017..F-020` | `PV-BO-002` | `2025-08-02T09:00:00Z` |
| `MTR-006` | `MV-006-V1` | 1 | None | `2025-09-03` | `F-021..F-024` | `PV-BO-002` | `2025-09-03T09:00:00Z` |
| `MTR-007` | `MV-007-V1` | 1 | None | `2025-09-10` | `F-025..F-028` | `PV-BO-002` | `2025-09-10T09:00:00Z` |
| `MTR-008` | `MV-008-V1` | 1 | None | `2025-09-20` | `F-029..F-032` | `PV-BO-002` | `2025-09-20T09:00:00Z` |
| `MTR-009` | `MV-009-V1` | 1 | None | `2025-10-01` | `F-034..F-039` | `PV-BO-002` | `2025-10-01T09:00:00Z` |

- CONFIRMED: Every matter version has `domain=supplier_onboarding`, the representative beneficial-ownership question, `submitted_by=ACT-SEED`, and `is_synthetic=true`.
- CONFIRMED: The exact question on every matter version is `Should this supplier be approved, rejected, or escalated given the available beneficial-ownership evidence?`
- CONFIRMED: `F-033` is a later contextual fact attached to `DV-008-V1`; it was not considered in `MV-008-V1` or the original decision content.

## Decision Records, Outcomes, Confirmations, And Provenance

| Decision | Immutable version | Seq. | Matter version | `created_at` / `decided_at` | Outcome and rationale | Confirmation | Packet | Policy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `D-001` | `DV-001-V1` | 1 | `MV-001-V1` | `2025-02-10T11:05:00Z` / `2025-02-10T10:00:00Z` | Escalated; independent ownership evidence was incomplete under V1 | `HC-001`, `ACT-REVIEWER`, `2025-02-10T11:00:00Z` | None | `PV-BO-001` |
| `D-002` | `DV-002-V1` | 1 | `MV-002-V1` | `2025-04-22T11:05:00Z` / `2025-04-22T10:00:00Z` | Escalated; materially similar missing evidence followed the baseline | `HC-002`, `ACT-REVIEWER`, `2025-04-22T11:00:00Z` | None | `PV-BO-001` |
| `D-003` | `DV-003-V1` | 1 | `MV-003-V1` | `2025-08-14T11:05:00Z` / `2025-08-14T10:00:00Z` | Approved; verified public filings satisfied the listed-parent exception | `HC-003`, `ACT-REVIEWER`, `2025-08-14T11:00:00Z` | None | `PV-BO-002` |
| `D-004` | `DV-004-V1` | 1 | `MV-004-V1` | `2025-07-15T11:05:00Z` / `2025-07-15T10:00:00Z` | Escalated; V2 required independent evidence before approval | `HC-004`, `ACT-REVIEWER`, `2025-07-15T11:00:00Z` | None | `PV-BO-002` |
| `D-005` | `DV-005-V1` | 1 | `MV-005-V1` | `2025-08-02T11:05:00Z` / `2025-08-02T10:00:00Z` | Approved externally on self-attestation; later withdrawn from authority after the attestation was found unreliable | `HC-005`, `ACT-REVIEWER`, `2025-08-02T11:00:00Z` | None | `PV-BO-002` |
| `D-006` | `DV-006-V1` | 1 | `MV-006-V1` | `2025-09-03T11:05:00Z` / `2025-09-03T10:00:00Z` | Escalated; ownership evidence was complete but control-chain risk remained unresolved | `HC-006`, `ACT-REVIEWER`, `2025-09-03T11:00:00Z` | None | `PV-BO-002` |
| `D-007` | `DV-007-V1` | 1 | `MV-007-V1` | `2025-09-10T11:05:00Z` / `2025-09-10T10:00:00Z` | Approved; required independent evidence was complete | `HC-007`, `ACT-REVIEWER`, `2025-09-10T11:00:00Z` | None | `PV-BO-002` |
| `D-008` | `DV-008-V1` | 1 | `MV-008-V1` | `2025-09-20T11:05:00Z` / `2025-09-20T10:00:00Z` | Approved; registry evidence appeared complete when decided | `HC-008`, `ACT-REVIEWER`, `2025-09-20T11:00:00Z` | None | `PV-BO-002` |

- CONFIRMED: Every record has `previous_decision_version_id=null`, copies `relevant_at` from its matter version, uses the matter's fact IDs, has `domain=supplier_onboarding`, `is_synthetic=true`, and provenance `{created_by: ACT-SEED, origin: synthetic_seed}`.
- CONFIRMED: Every confirmation attestation is `I confirm that this record accurately represents the completed external decision and may enter Finné Memory's precedent corpus.`

## Sources And Evidence

| Source ID | Type | Title / fixture reference | Evidence ID | Evidence description |
| --- | --- | --- | --- | --- |
| `SRC-POL-001` | policy | Beneficial Ownership Policy V1 / `fixture://policy/bo/v1` | None | Policy source for `PV-BO-001` |
| `SRC-POL-002` | policy | Beneficial Ownership Policy V2 / `fixture://policy/bo/v2` | None | Policy source for `PV-BO-002` |
| `SRC-D1-REG` | registry_record | D1 registry search / `fixture://d1/registry` | `E-D1-REG` | Independent registry extract absent |
| `SRC-D1-ATT` | attestation | D1 supplier attestation / `fixture://d1/attestation` | `E-D1-ATT` | Signed ownership attestation present |
| `SRC-D1-RISK` | risk_assessment | D1 risk assessment / `fixture://d1/risk` | `E-D1-RISK` | Supplier rated low risk |
| `SRC-D2-REG` | registry_record | D2 registry search / `fixture://d2/registry` | `E-D2-REG` | Independent registry extract absent |
| `SRC-D2-ATT` | attestation | D2 supplier attestation / `fixture://d2/attestation` | `E-D2-ATT` | Signed ownership attestation present |
| `SRC-D2-RISK` | risk_assessment | D2 risk assessment / `fixture://d2/risk` | `E-D2-RISK` | Supplier rated low risk |
| `SRC-D3-LIST` | registry_record | D3 exchange listing / `fixture://d3/listing` | `E-D3-LIST` | Public parent listing verified |
| `SRC-D3-FILE` | registry_record | D3 public ownership filing / `fixture://d3/filing` | `E-D3-FILE` | Public filing identifies beneficial owners |
| `SRC-D3-CASE` | supplier_document | D3 onboarding file / `fixture://d3/case` | `E-D3-CASE` | Private-company form not supplied |
| `SRC-D4-REG` | registry_record | D4 partial registry extract / `fixture://d4/registry` | `E-D4-REG` | Independent ownership record incomplete |
| `SRC-D4-ATT` | attestation | D4 supplier attestation / `fixture://d4/attestation` | `E-D4-ATT` | Signed ownership attestation present |
| `SRC-D4-RISK` | risk_assessment | D4 risk assessment / `fixture://d4/risk` | `E-D4-RISK` | Supplier rated medium risk |
| `SRC-D5-REG` | registry_record | D5 registry search / `fixture://d5/registry` | `E-D5-REG` | Independent evidence missing |
| `SRC-D5-ATT` | attestation | D5 supplier attestation / `fixture://d5/attestation` | `E-D5-ATT` | Self-attestation supplied |
| `SRC-D5-RISK` | risk_assessment | D5 risk assessment / `fixture://d5/risk` | `E-D5-RISK` | Supplier rated medium risk |
| `SRC-D5-REVIEW` | risk_assessment | D5 post-decision review / `fixture://d5/review` | `E-D5-REVIEW` | Attestation later found unreliable; supports withdrawal reason only |
| `SRC-D6-REG` | registry_record | D6 complete registry extract / `fixture://d6/registry` | `E-D6-REG` | Ownership evidence complete |
| `SRC-D6-CONTROL` | risk_assessment | D6 control-chain review / `fixture://d6/control` | `E-D6-CONTROL` | Control-chain risk unresolved |
| `SRC-D6-RISK` | risk_assessment | D6 risk assessment / `fixture://d6/risk` | `E-D6-RISK` | Supplier rated medium risk |
| `SRC-D7-REG` | registry_record | D7 complete registry extract / `fixture://d7/registry` | `E-D7-REG` | Ownership evidence complete |
| `SRC-D7-RISK` | risk_assessment | D7 risk assessment / `fixture://d7/risk` | `E-D7-RISK` | Supplier rated low risk with no unresolved control issue |
| `SRC-D8-REG` | registry_record | D8 registry extract / `fixture://d8/registry` | `E-D8-REG` | Ownership evidence appeared complete at decision time |
| `SRC-D8-RISK` | risk_assessment | D8 risk assessment / `fixture://d8/risk` | `E-D8-RISK` | Supplier rated low risk |
| `SRC-D8-CHALLENGE` | risk_assessment | D8 source-integrity review / `fixture://d8/challenge` | `E-D8-CHALLENGE` | Later challenge to registry-record authenticity |
| `SRC-MAT-REG` | registry_record | MAT-001 partial registry extract / `fixture://mat001/registry` | `E-MAT-REG` | Partial extract leaves one owner unverified |
| `SRC-MAT-ATT` | attestation | MAT-001 supplier attestation / `fixture://mat001/attestation` | `E-MAT-ATT` | Self-attestation supplied |
| `SRC-MAT-RISK` | risk_assessment | MAT-001 risk assessment / `fixture://mat001/risk` | `E-MAT-RISK` | Medium risk and urgent-onboarding request |

- CONFIRMED: All sources have `issuer=Synthetic Finné Memory Demo`, `is_synthetic=true`, and omitted optional content fingerprints.
- CONFIRMED: All evidence items use their listed source, the table description, `added_by=ACT-SEED`, and a fixture locator matching the source reference.

## Facts And Canonical FactEvidenceLinks

| Fact ID | Applies to | Predicate = value | Origin / verification | Evidence relation and link ID |
| --- | --- | --- | --- | --- |
| `F-001` | `MV-001-V1` | `legal_form=private` | system_supplied / supported | `FEL-001` supports via `E-D1-REG` |
| `F-002` | `MV-001-V1` | `risk_level=low` | system_supplied / supported | `FEL-002` supports via `E-D1-RISK` |
| `F-003` | `MV-001-V1` | `ownership_attestation=present` | human_supplied / supported | `FEL-003` supports via `E-D1-ATT` |
| `F-004` | `MV-001-V1` | `independent_registry_extract=missing` | system_supplied / supported | `FEL-004` supports via `E-D1-REG` |
| `F-005` | `MV-002-V1` | `legal_form=private` | system_supplied / supported | `FEL-005` supports via `E-D2-REG` |
| `F-006` | `MV-002-V1` | `risk_level=low` | system_supplied / supported | `FEL-006` supports via `E-D2-RISK` |
| `F-007` | `MV-002-V1` | `ownership_attestation=present` | human_supplied / supported | `FEL-007` supports via `E-D2-ATT` |
| `F-008` | `MV-002-V1` | `independent_registry_extract=missing` | system_supplied / supported | `FEL-008` supports via `E-D2-REG` |
| `F-009` | `MV-003-V1` | `ownership_structure=publicly_listed_parent` | system_supplied / supported | `FEL-009` supports via `E-D3-LIST` |
| `F-010` | `MV-003-V1` | `parent_listing=verified` | system_supplied / confirmed | `FEL-010` supports via `E-D3-LIST` |
| `F-011` | `MV-003-V1` | `public_ownership_filing=available` | system_supplied / confirmed | `FEL-011` supports via `E-D3-FILE` |
| `F-012` | `MV-003-V1` | `private_company_bo_form=absent` | human_supplied / supported | `FEL-012` supports via `E-D3-CASE` |
| `F-013` | `MV-004-V1` | `legal_form=private` | system_supplied / supported | `FEL-013` supports via `E-D4-REG` |
| `F-014` | `MV-004-V1` | `risk_level=medium` | system_supplied / supported | `FEL-014` supports via `E-D4-RISK` |
| `F-015` | `MV-004-V1` | `ownership_attestation=present` | human_supplied / supported | `FEL-015` supports via `E-D4-ATT` |
| `F-016` | `MV-004-V1` | `independent_ownership_evidence=incomplete` | system_supplied / supported | `FEL-016` supports via `E-D4-REG` |
| `F-017` | `MV-005-V1` | `legal_form=private` | system_supplied / supported | `FEL-017` supports via `E-D5-REG` |
| `F-018` | `MV-005-V1` | `risk_level=medium` | system_supplied / supported | `FEL-018` supports via `E-D5-RISK` |
| `F-019` | `MV-005-V1` | `ownership_attestation=present` | human_supplied / supported | `FEL-019` supports via `E-D5-ATT` |
| `F-020` | `MV-005-V1` | `independent_ownership_evidence=missing` | system_supplied / supported | `FEL-020` supports via `E-D5-REG` |
| `F-021` | `MV-006-V1` | `legal_form=private` | system_supplied / supported | `FEL-021` supports via `E-D6-REG` |
| `F-022` | `MV-006-V1` | `risk_level=medium` | system_supplied / supported | `FEL-022` supports via `E-D6-RISK` |
| `F-023` | `MV-006-V1` | `independent_ownership_evidence=complete` | system_supplied / confirmed | `FEL-023` supports via `E-D6-REG` |
| `F-024` | `MV-006-V1` | `control_chain_risk=unresolved` | human_supplied / supported | `FEL-024` supports via `E-D6-CONTROL` |
| `F-025` | `MV-007-V1` | `legal_form=private` | system_supplied / supported | `FEL-025` supports via `E-D7-REG` |
| `F-026` | `MV-007-V1` | `risk_level=low` | system_supplied / supported | `FEL-026` supports via `E-D7-RISK` |
| `F-027` | `MV-007-V1` | `independent_ownership_evidence=complete` | system_supplied / confirmed | `FEL-027` supports via `E-D7-REG` |
| `F-028` | `MV-007-V1` | `control_chain_risk=none_identified` | system_supplied / supported | `FEL-028` supports via `E-D7-RISK` |
| `F-029` | `MV-008-V1` | `legal_form=private` | system_supplied / supported | `FEL-029` supports via `E-D8-REG` |
| `F-030` | `MV-008-V1` | `risk_level=low` | system_supplied / supported | `FEL-030` supports via `E-D8-RISK` |
| `F-031` | `MV-008-V1` | `independent_ownership_evidence=complete_at_decision` | system_supplied / supported | `FEL-031` supports via `E-D8-REG` |
| `F-032` | `MV-008-V1` | `control_chain_risk=none_identified` | system_supplied / supported | `FEL-032` supports via `E-D8-RISK` |
| `F-033` | `DV-008-V1` | `registry_record_authenticity=challenged_after_decision` | human_supplied / disputed | `FEL-033` supports the existence of the challenge via `E-D8-CHALLENGE`; it cannot support active authority |
| `F-034` | `MV-009-V1` | `legal_form=private` | system_supplied / supported | `FEL-034` supports via `E-MAT-REG` |
| `F-035` | `MV-009-V1` | `risk_level=medium` | system_supplied / supported | `FEL-035` supports via `E-MAT-RISK` |
| `F-036` | `MV-009-V1` | `urgent_onboarding=true` | model_extracted / unverified | `FEL-036` supports via `E-MAT-RISK`; visible but non-authoritative |
| `F-037` | `MV-009-V1` | `ownership_attestation=present` | human_supplied / supported | `FEL-037` supports via `E-MAT-ATT` |
| `F-038` | `MV-009-V1` | `registry_extract=partial` | system_supplied / supported | `FEL-038` supports via `E-MAT-REG` |
| `F-039` | `MV-009-V1` | `beneficial_owner_identity=unverified` | system_supplied / supported | `FEL-039` supports via `E-MAT-REG` |

- CONFIRMED: Every fact has `subject` equal to its fixture supplier, a category or boolean value type matching the displayed value, `recorded_by=ACT-SEED`, and `recorded_at` equal to the owning matter's submission timestamp unless otherwise stated.
- CONFIRMED: `F-033` has `recorded_at=2025-09-25T10:00:00Z` and `recorded_by=ACT-STEWARD`; `F-036` has `origin=model_extracted` and `extraction_confidence=0.72`; all other facts omit extraction confidence.
- CONFIRMED: Every `FEL-*` object has `relationship_type=supports`, `created_by=ACT-SEED`, and `created_at` equal to its fact's `recorded_at`.
- CONFIRMED: No seed fact uses a canonical reverse evidence list; reverse collections are derived from `FactEvidenceLink` objects.

## Valid CitationEdges

| Citation | From | Target | Claim |
| --- | --- | --- | --- |
| `CIT-001` | `DV-001-V1` | `PV-BO-001` | V1 governed the matter at `relevant_at` |
| `CIT-002` | `DV-001-V1` | `E-D1-REG` | Independent evidence was missing |
| `CIT-003` | `DV-002-V1` | `PV-BO-001` | V1 governed the matter at `relevant_at` |
| `CIT-004` | `DV-002-V1` | `E-D2-REG` | Independent evidence was missing |
| `CIT-005` | `DV-002-V1` | `DV-001-V1` | DR-002 followed the original baseline |
| `CIT-006` | `DV-003-V1` | `PV-BO-002` | V2 governed the matter at `relevant_at` |
| `CIT-007` | `DV-003-V1` | `E-D3-FILE` | Verified public ownership filing was available |
| `CIT-008` | `DV-003-V1` | `DV-004-V1` | Public-parent facts distinguish the private-supplier baseline |
| `CIT-009` | `DV-004-V1` | `PV-BO-002` | V2 governed and required independent evidence |
| `CIT-010` | `DV-004-V1` | `E-D4-REG` | Independent evidence was incomplete |
| `CIT-011` | `DV-004-V1` | `DV-001-V1` | DR-004 replaced the original V1 baseline |
| `CIT-012` | `DV-004-V1` | `DV-002-V1` | DR-004 replaced the V1 following decision |
| `CIT-013` | `DV-005-V1` | `PV-BO-002` | V2 governed the matter at `relevant_at` |
| `CIT-014` | `DV-005-V1` | `E-D5-ATT` | Self-attestation was the supplied ownership support |
| `CIT-015` | `DV-006-V1` | `PV-BO-002` | V2 control-chain rule governed escalation |
| `CIT-016` | `DV-006-V1` | `E-D6-CONTROL` | Control-chain risk remained unresolved |
| `CIT-017` | `DV-007-V1` | `PV-BO-002` | V2 governed the matter at `relevant_at` |
| `CIT-018` | `DV-007-V1` | `E-D7-REG` | Independent ownership evidence was complete |
| `CIT-019` | `DV-008-V1` | `PV-BO-002` | V2 governed the matter at `relevant_at` |
| `CIT-020` | `DV-008-V1` | `E-D8-REG` | Registry evidence appeared complete when decided |

- CONFIRMED: Every citation uses `from_type=decision_version`, the target type implied by its target ID, `created_by=ACT-SEED`, `created_at` equal to its record's `created_at`, and `validated_at` exactly one minute later.
- CONFIRMED: No invalid citation is present. A rejected-attempt test fixture must use `CitationAttemptAuditEvent`, not `CitationEdge`.

## CitationAttemptAuditEvent Fixture

| Event | From | Attempted target | Claim | Result | Reason | Recorded / actor |
| --- | --- | --- | --- | --- | --- | --- |
| `CAE-001` | packet `PKT-MAT-001-001` | decision version `DV-999-V1` | Missing record should support approval | `rejected` | Target decision version does not exist | `2025-10-01T09:30:00Z` / `ACT-SEED` |

- CONFIRMED: `CAE-001` is an audit event only and never appears in the valid citation graph or as packet support.

## PrecedentRelationships

| Relationship | From version | To version | Type | Material facts | Citations | Rationale | Confirmed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `REL-001` | `DV-002-V1` | `DV-001-V1` | `follows` | `F-005`, `F-008` | `CIT-004`, `CIT-005` | Same private-supplier evidence gap under the same policy required escalation | `ACT-STEWARD`, `2025-04-22T12:30:00Z` |
| `REL-002` | `DV-003-V1` | `DV-004-V1` | `distinguishes` | `F-009`, `F-011` | `CIT-007`, `CIT-008` | Verified public-parent filings distinguish the private-supplier evidence rule | `ACT-STEWARD`, `2025-08-14T12:30:00Z` |
| `REL-003` | `DV-004-V1` | `DV-001-V1` | `supersedes` | `F-013`, `F-016` | `CIT-009`, `CIT-011` | V2 establishes the current private-supplier baseline | `ACT-STEWARD`, `2025-07-15T12:30:00Z` |
| `REL-004` | `DV-004-V1` | `DV-002-V1` | `supersedes` | `F-013`, `F-016` | `CIT-009`, `CIT-012` | V2 replaces the prior decision that followed the V1 baseline | `ACT-STEWARD`, `2025-07-15T12:30:00Z` |

## AuthorityEvents

| Event | Decision version | Previous -> new | Effective / recorded | Steward | Reason | Successors |
| --- | --- | --- | --- | --- | --- | --- |
| `AE-001-D` | `DV-001-V1` | None -> `draft` | `2025-02-10T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-001-A` | `DV-001-V1` | `draft` -> `active` | `2025-02-10T12:00:00Z` / same | `ACT-STEWARD` | Required V1 evidence and citations validated | None |
| `AE-001-S` | `DV-001-V1` | `active` -> `superseded` | `2025-07-15T12:30:00Z` / same | `ACT-STEWARD` | `REL-003` established V2 successor | `DV-004-V1` |
| `AE-002-D` | `DV-002-V1` | None -> `draft` | `2025-04-22T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-002-A` | `DV-002-V1` | `draft` -> `active` | `2025-04-22T12:00:00Z` / same | `ACT-STEWARD` | Required V1 evidence and citations validated | None |
| `AE-002-S` | `DV-002-V1` | `active` -> `superseded` | `2025-07-15T12:30:00Z` / same | `ACT-STEWARD` | `REL-004` established V2 successor | `DV-004-V1` |
| `AE-003-D` | `DV-003-V1` | None -> `draft` | `2025-08-14T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-003-A` | `DV-003-V1` | `draft` -> `active` | `2025-08-14T12:00:00Z` / same | `ACT-STEWARD` | Listed-parent evidence and citations validated | None |
| `AE-004-D` | `DV-004-V1` | None -> `draft` | `2025-07-15T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-004-A` | `DV-004-V1` | `draft` -> `active` | `2025-07-15T12:00:00Z` / same | `ACT-STEWARD` | V2 baseline evidence and citations validated | None |
| `AE-005-D` | `DV-005-V1` | None -> `draft` | `2025-08-02T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-005-A` | `DV-005-V1` | `draft` -> `active` | `2025-08-02T12:00:00Z` / same | `ACT-STEWARD` | Initial source references validated | None |
| `AE-005-W` | `DV-005-V1` | `active` -> `withdrawn` | `2025-08-20T10:00:00Z` / same | `ACT-STEWARD` | `SRC-D5-REVIEW` found the supporting attestation unreliable | None |
| `AE-006-D` | `DV-006-V1` | None -> `draft` | `2025-09-03T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-006-A` | `DV-006-V1` | `draft` -> `active` | `2025-09-03T12:00:00Z` / same | `ACT-STEWARD` | Control-chain evidence and citations validated | None |
| `AE-007-D` | `DV-007-V1` | None -> `draft` | `2025-09-10T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back; awaiting authority review | None |
| `AE-008-D` | `DV-008-V1` | None -> `draft` | `2025-09-20T11:05:00Z` / same | `ACT-STEWARD` | Human-confirmed seed write-back | None |
| `AE-008-A` | `DV-008-V1` | `draft` -> `active` | `2025-09-20T12:00:00Z` / same | `ACT-STEWARD` | Initial registry evidence validated | None |
| `AE-008-Q` | `DV-008-V1` | `active` -> `questioned` | `2025-09-25T10:00:00Z` / same | `ACT-STEWARD` | `F-033` and `SRC-D8-CHALLENGE` raise source-integrity concern | None |

## MAT-001 Expected Packet Contract

- CONFIRMED: The generated packet has `packet_id=PKT-MAT-001-001` and references exactly `matter_version_id=MV-009-V1`.
- CONFIRMED: `DV-005-V1` remains retrievable because of high factual similarity but is visibly marked `withdrawn` and excluded from active authority.
- CONFIRMED: `DV-004-V1` is presented as the active current baseline under `PV-BO-002`.
- CONFIRMED: `DV-003-V1` explains why the public-parent exception does not apply to MAT-001.
- CONFIRMED: `DV-006-V1` appears only as lower-similarity active context.
- CONFIRMED: `F-036` remains visible as an unverified model-extracted fact and cannot support an authoritative conclusion.
- CONFIRMED: The packet produces no approval, rejection, or escalation outcome.
