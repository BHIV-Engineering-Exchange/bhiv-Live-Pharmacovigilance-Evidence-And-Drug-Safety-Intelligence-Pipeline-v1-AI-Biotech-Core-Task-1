# Biotech Integration Readiness

**As of:** 2026-09-29  
**Decision:** Pharmacovigilance capability is locally testable; cross-capability integration is **BLOCKED**. No shared-system integration is authorized by this audit alone.

## Ready Now

- Run this repository's test suite using `c:/python313/python.exe -m pytest -q` (47 passing after the checked-in `src` import bridge and pytest discovery fix; no warnings).
- Consume pharmacovigilance evidence as JSON serialized from `EvidenceRecord` schema version `1.1`.
- Use `validate_evidence` as the current repository validation function and `add_evidence` for local duplicate-aware JSON persistence.
- Preserve `REPORTED_ASSOCIATION` and unresolved entity status; this pipeline is evidence organization, not scientific adjudication.

## Not Ready for Shared Integration

- No interface, versioning policy, transport, persistence service, or canonical evidence contract has been agreed across capabilities.
- The formulation/stability, TB discovery, and biosimilarity/QC repositories and Test 3 submissions are absent from this clone.
- Live OpenFDA execution was not performed during the audit; external service availability and response behavior remain unverified here.
- Synthetic-vs-real evidence labeling is not explicit in the current record contract, and the existing output's origin was not established.
- Conflict handling for different payloads with a shared source ID and structural field-type validation require review before treating this as a shared ingestion boundary.

## Integration Sequence

1. Obtain the other three candidate repositories and their exact run/test instructions; record revision identifiers and classify evidence as documented, implemented, executable, tested, reproducible, or blocked.
2. Run each repository independently and retain raw command output, test results, and sample inputs/outputs; do not blend claims across repos.
3. Compare evidence schemas, provenance, synthetic-data labeling, identifiers, error semantics, and review states. Propose the smallest shared contract only after the comparison.
4. Agree ownership and versioning for the shared contract and adapters; keep domain-specific transformations in their owning capability.
5. Add cross-capability contract tests using explicitly labeled fixtures, including missing, invalid, duplicate, conflicting, empty, and malformed inputs.
6. Integrate behind the agreed interface, rerun each module's regression suite and system tests, capture runtime evidence, then conduct human scientific review where applicable.

## Readiness by Capability

| Capability                       | Local implementation | Execution evidence                           | Shared integration                                                                    |
| -------------------------------- | -------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------- |
| Drug Safety Evidence Integration | Implemented          | 47 tests pass; empty-input CLI path observed | Blocked pending contract, live-source verification, and common provenance/data labels |
| Formulation & Stability          | Not in clone         | None                                         | Blocked: repository/submission required                                               |
| TB Drug-Discovery Candidates     | Not in clone         | None                                         | Blocked: repository/submission required                                               |
| Biosimilarity & Preclinical QC   | Not in clone         | None                                         | Blocked: repository/submission required                                               |

No APPROVED/APPROVED WITH FIXES/REVISION REQUIRED/REJECTED Day 3 decision is issued: the required candidate submissions and staged functional review are not present.
