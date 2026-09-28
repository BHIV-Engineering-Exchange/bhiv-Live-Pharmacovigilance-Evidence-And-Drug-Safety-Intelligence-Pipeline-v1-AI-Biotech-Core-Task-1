# REVIEW INDEX
## Pharmacovigilance Evidence Pipeline Repair
### BHIV Biotech — Evidence Integrity Sprint

---

## 1. Review Objective

This review covers the repair and hardening of the existing
pharmacovigilance evidence pipeline.

The repair focuses on:

- deterministic drug/entity matching
- provenance preservation
- explicit association semantics
- malformed-record handling
- deterministic repeated-ingestion behavior
- regression testing
- structured evidence output

The objective is to ensure that an ingested safety/evidence record
can reliably answer:

1. What entity was involved?
2. What happened?
3. Where did the evidence come from?
4. How strongly does the system support the association?

---

## 2. Integration Context

| Role | Responsibility |
|---|---|
| Sarvesh | Pipeline repair and evidence-model implementation |
| Shravni | Scientific safety and quality evidence-validation framework |
| Shyamal | Biosimilarity and preclinical evidence structuring |
| BHEX | Repository, evidence and engineering archive |
| MDU | Schema, provenance, version and semantic continuity requirements |
| Parikshak | Future evidence-based engineering assurance |

---

## 3. Execution Flow

The repaired runtime flow is:

Safety / Evidence Record
        ↓
OpenFDA / FAERS ingestion
        ↓
Deterministic entity resolution
        ↓
Explicit association classification
        ↓
Provenance capture
        ↓
Evidence validation
        ↓
Duplicate / repeated-ingestion protection
        ↓
Structured evidence output
        ↓
Downstream scientific review

---

## 4. Core Repairs

### 4.1 Deterministic Entity Resolution

The pipeline explicitly represents entity-resolution status using:

- MATCHED
- AMBIGUOUS
- UNRESOLVED

When a deterministic match is available, canonical entity information
is retained.

The system does not silently convert an uncertain entity into a
confirmed match.

---

### 4.2 Provenance Capture

Evidence records retain provenance information including:

- source system
- underlying dataset
- retrieval method
- transformation
- source record identity
- source URL
- retrieval timestamp

Required provenance fields include:

- source_system
- underlying_dataset
- retrieval_method
- transformation

Missing, incomplete or incorrectly typed provenance is rejected by
validation.

---

### 4.3 Explicit Association Semantics

The normalized evidence model explicitly represents:

REPORTED_ASSOCIATION

This describes the association reported by the source evidence.

It does not convert a reported adverse event into a clinical causal
conclusion.

The pipeline therefore preserves the distinction between:

reported evidence

and

clinical causality

---

### 4.4 Deterministic Evidence Identity

Evidence identity is based primarily on:

source_record_id

when the source provides one.

When the source record ID is unavailable, a deterministic content
fingerprint is used.

This prevents the same underlying evidence from being treated as new
solely because retrieval metadata changed.

---

### 4.5 Duplicate and Repeated-Ingestion Protection

The storage layer checks incoming evidence against previously stored
evidence.

The duplicate strategy is:

source_record_id available
        ↓
use source identity

source_record_id unavailable
        ↓
use deterministic content fingerprint

Therefore:

First ingestion
      ↓
record saved

Repeated ingestion
      ↓
same evidence identity detected
      ↓
record not saved again

Duplicate records within the same ingestion batch are also prevented
from being stored multiple times.

---

## 5. Evidence Schema

The repaired evidence schema uses version:

1.1

The EvidenceRecord model contains fields for:

- evidence_id
- drug_name
- drug_identifier
- adverse_event
- source
- source_record_id
- evidence_type
- event_date
- retrieved_at
- source_url
- schema_version
- provenance
- raw_record_reference
- entity_resolution_status
- canonical_entity_name
- canonical_entity_identifier
- association_type

The schema preserves:

- entity identity
- event information
- source identity
- provenance
- association meaning
- schema version

---

## 6. Runtime Processing

The runtime pipeline is implemented through the following flow:

User drug query
      ↓
OpenFDA / FAERS connector
      ↓
Raw safety records
      ↓
normalize_record()
      ↓
Deterministic entity resolution
      ↓
EvidenceRecord creation
      ↓
Evidence validation
      ↓
Duplicate-aware evidence storage
      ↓
evidence_output.json

---

## 7. Validation and Regression Evidence

The current automated regression suite contains:

33 tests passed
0 failures

The test suite covers the repaired behavior across multiple layers.

### Entity Resolution

Tests cover:

- deterministic matching
- alias matching
- ambiguous names
- unresolved names
- canonical entity handling

### Normalization

Tests cover:

- drug extraction
- reaction extraction
- entity-resolution integration
- association semantics
- provenance preservation
- malformed OpenFDA-style records

### Evidence Schema

Tests cover:

- valid evidence records
- empty provenance
- incomplete provenance
- invalid provenance type
- invalid entity-resolution status
- invalid association type

### Evidence Storage

Tests cover:

- new record insertion
- repeated source records
- records without source IDs
- deterministic fingerprinting
- different records
- duplicate records within the same batch

---

## 8. Runtime Verification

Live runtime verification was performed using the OpenFDA/FAERS
adverse-event API.

Example test input:

ibuprofen

Observed runtime behavior included:

Records found: 5

The runtime output demonstrated:

- OpenFDA/FAERS ingestion
- normalized evidence generation
- matched entity resolution
- unresolved entity handling
- canonical entity output when matched
- REPORTED_ASSOCIATION
- source record IDs
- FAERS evidence type
- retrieval timestamp
- evidence persistence

Example observed matched entity:

Drug: IBUPROFEN
Entity Resolution: MATCHED
Canonical Entity: IBUPROFEN
Association Type: REPORTED_ASSOCIATION
Source: OpenFDA/FAERS

The runtime also demonstrated that records that could not be
deterministically resolved were represented as:

Entity Resolution: UNRESOLVED
Canonical Entity: None

This prevents unsupported entity assumptions.

---

## 9. Repeated-Ingestion Verification

Repeated runtime ingestion was tested using the same drug query.

The first ingestion saved newly encountered evidence records.

The same ingestion was then repeated.

The second ingestion did not save the same source records again.

The observed behavior was:

FIRST INGESTION
       ↓
new evidence records saved

SECOND INGESTION
       ↓
existing source identities detected
       ↓
duplicate records rejected

This provides runtime evidence that repeated ingestion is
duplicate-safe.

---

## 10. Review-Critical Source Files

The review-critical implementation files are:

src/entity_resolution.py
src/evidence_schema.py
src/normalize_evidence.py
src/evidence_store.py
src/openfda_connector.py
app.py

The review-critical regression tests are:

tests/test_entity_resolution.py
tests/test_normalization.py
tests/test_evidence_schema.py
tests/test_evidence_store.py
tests/test_phase4.py

Only specific changed and review-critical files should be included in
the final code packet.

Reviewers should not need to inspect the entire repository to verify
the repair.

---

## 11. Evidence Packet

The evidence package is organized under:

evidence_packet/

Expected structure:

evidence_packet/
├── review_packet.md
├── screenshots/
├── code_packet/
├── runtime_logs/
├── api_samples/
└── deployment_proof/

### Evidence Packet Purpose

The packet should provide direct evidence of:

- repaired source code
- automated test results
- runtime execution
- API behavior
- normalized evidence output
- duplicate protection
- relevant screenshots

Architecture descriptions alone are not considered sufficient proof.

---

## 12. Daily Engineering Packet

Engineering continuity material is maintained under:

DEP/

Expected structure:

DEP/
├── metadata.md
├── tms.md
├── gc.md
├── mdu.md
├── review.md
├── next_tasks.md
├── blockers.md
├── screenshots/
└── code_packet/

The Daily Engineering Packet should allow another engineer to
understand the current state without requiring the original developer
to explain the work verbally.

---

## 13. Screenshots and Runtime Evidence

Screenshots should capture actual execution evidence.

Required evidence includes:

1. Successful automated test execution.
2. Runtime OpenFDA search.
3. Entity-resolution output.
4. Provenance-related output where visible.
5. Association classification.
6. Evidence persistence.
7. Repeated-ingestion duplicate protection.

Screenshots must represent actual pipeline execution rather than
architecture diagrams.

---

## 14. API Evidence

The pipeline uses:

OpenFDA Drug Event API

The source dataset represented by the connector is:

FAERS

The normalized evidence retains the original source record identity
where available.

API samples should be stored separately from normalized output so that
reviewers can distinguish:

raw source evidence

from

normalized pipeline evidence

---

## 15. Known Scope Boundary

This repair does not attempt to provide:

- clinical diagnosis
- clinical treatment recommendations
- clinical decision-making
- unsupported causal conclusions
- manufacturing guidance
- formulation guidance
- marketing claims
- redesign of the complete BHIV biotech platform
- unsupported biomedical canon

The system structures reported safety evidence for downstream
scientific and safety review.

---

## 16. Assumptions

The current implementation assumes:

1. OpenFDA/FAERS records follow the expected JSON structure.
2. safetyreportid represents the source-level report identity when
   available.
3. Drug names can sometimes be ambiguous or inconsistent in source
   records.
4. Entity resolution should remain deterministic.
5. A reported association must not automatically be interpreted as
   causality.
6. Provenance must remain attached to normalized evidence.
7. Repeated ingestion must not create duplicate evidence records.
8. Missing source identity requires deterministic fallback handling.

---

## 17. Unresolved / Future Cases

The following cases remain outside the current repair scope or may
require future scientific review:

- complex multi-ingredient products
- highly ambiguous drug names requiring external authoritative
  reference mapping
- advanced ontology-based entity resolution
- clinical causality assessment
- cross-database evidence reconciliation
- automated scientific interpretation
- production-scale distributed ingestion

These cases should not be silently treated as resolved.

---

## 18. Quality Gates

| Quality Gate | Status |
|---|---|
| Entity resolution implemented | PASS |
| Deterministic matching | PASS |
| Ambiguous handling | PASS |
| Unresolved handling | PASS |
| Provenance captured | PASS |
| Provenance validated | PASS |
| Association semantics explicit | PASS |
| Malformed record handling | PASS |
| Duplicate protection | PASS |
| Repeated ingestion protection | PASS |
| Automated regression tests | PASS |
| Runtime verification | PASS |
| Structured evidence output | PASS |

---

## 19. Current Test Result

The current regression suite has been verified with:

33 tests passed
0 failures

This result should be reproduced before final submission.

Recommended command:

python -m pytest -q

---

## 20. Current Runtime Result

The repaired application has been executed successfully using:

python app.py

with:

ibuprofen

as the test query.

The runtime successfully:

- connected to OpenFDA
- retrieved safety records
- normalized records
- resolved entities
- classified associations
- validated evidence
- stored new evidence
- prevented repeated duplicates

---

## 21. Handover Summary

The repaired pipeline is now capable of producing structured evidence
that preserves:

WHO / WHAT
    ↓
Entity involved

WHAT HAPPENED
    ↓
Reported adverse event

WHERE FROM
    ↓
Source + source record + provenance

WHAT DOES THE SYSTEM CLAIM
    ↓
Explicit reported association semantics

HOW CERTAIN IS ENTITY IDENTITY
    ↓
MATCHED / AMBIGUOUS / UNRESOLVED

HAS THIS EVIDENCE ALREADY BEEN INGESTED
    ↓
Deterministic duplicate protection

---

## 22. Final Status

PHARMACOVIGILANCE EVIDENCE PIPELINE REPAIR

Entity Resolution              PASS
Provenance Capture             PASS
Provenance Validation          PASS
Association Semantics          PASS
Normalization Integration      PASS
Malformed Record Handling      PASS
Duplicate Protection           PASS
Repeated Ingestion             PASS
Automated Regression Suite     PASS
Runtime Verification           PASS
Structured Evidence Output      PASS

Regression Tests:
33 PASSED
0 FAILED

---

## 23. Remaining Submission Work

The remaining work is evidence packaging and handover documentation:

- finalize review_packet.md
- capture and organize screenshots
- capture runtime logs
- store representative API samples
- prepare the review-critical code packet
- complete Daily Engineering Packet files
- verify REVIEW_INDEX.md
- perform final regression run
- perform final runtime verification
- prepare zero-context handover

---

## 24. Review Conclusion

The existing pharmacovigilance evidence pipeline has been repaired and
hardened around deterministic entity resolution, provenance
preservation, explicit association semantics and deterministic
repeated-ingestion behavior.

The implementation is supported by automated regression testing and
live runtime verification.

The repaired pipeline therefore provides a reproducible path from:

source safety evidence
        ↓
entity resolution
        ↓
association semantics
        ↓
provenance
        ↓
validation
        ↓
duplicate-safe storage
        ↓
structured evidence

The resulting evidence can be passed to downstream scientific review
without silently changing entity identity, provenance or the meaning of
the reported association.