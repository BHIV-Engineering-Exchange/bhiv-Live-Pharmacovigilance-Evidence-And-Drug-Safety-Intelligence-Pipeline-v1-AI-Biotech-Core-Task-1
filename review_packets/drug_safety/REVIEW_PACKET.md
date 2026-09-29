# Review Packet: Drug Safety Evidence Integration

**Audited repository:** This cloned repository  
**Audit date:** 2026-09-29  
**Decision state:** No Day 3 decision issued. Local tests are green after an import-path repair; shared integration remains blocked.

## 1. Entry Point

`app.py` is the interactive CLI entry point. It asks for a drug name, searches OpenFDA, normalizes each result, validates it, and stores valid records. The audit added `src/__init__.py` so existing `src.*` imports resolve to the root-level modules.

## 2. Core Execution Flow

`app.py` -> `openfda_connector.search_drug` -> `normalize_evidence.normalize_record` (including `entity_resolution.resolve_entity`) -> `evidence_schema.validate_evidence` -> `evidence_store.add_evidence` -> `evidence_output.json`. Events are logged through `monitoring.log_event`; unexpected CLI exceptions are converted by `error_handler.handle_application_error`.

Core review files: `openfda_connector.py`, `normalize_evidence.py`, `evidence_schema.py`.

## 3. Runtime Flow

The CLI prompts for a drug name. An empty value is rejected before retrieval. Non-empty values are sent to the OpenFDA Drug Event endpoint; successful results are normalized and validated individually. Valid records are sent to local JSON storage. Retrieval uses a 30-second request timeout. This audit did not make a live API request.

## 4. Real Output

Observed audit runtime output for empty input:

```text
PHARMACOVIGILANCE DRUG SAFETY SEARCH
Enter drug name: Please enter a drug name.
WARNING | pharmacovigilance_pipeline | EMPTY_DRUG_INPUT
```

The existing committed `evidence_output.json` contains structured records, but their real-vs-synthetic origin and current reproducibility were not established. Do not use them as verified fresh real-world evidence.

## 5. What Changed

Added a minimal `src` package path bridge to repair the package layout expected by the existing application and tests. No scientific/domain logic was changed.

## 6. Failure Cases

- Empty CLI query: executed; rejected safely before network access.
- Empty API result, malformed response shape, mocked request failure: covered by tests.
- Missing/invalid evidence values and invalid enum values: covered in part by schema tests.
- Duplicate/repeated source IDs, same-batch duplicates, and missing-ID fingerprint: covered by storage tests.
- Conflicting payload with same source ID: not surfaced distinctly by current store.
- Missing required raw source fields and invalid JSON bytes: no explicit test located.
- Live upstream failure: not exercised in this audit.

## 7. Test Results

Command: `c:/python313/python.exe -m pytest -q`  
Result: **47 passed**, no warnings, exit code 0. During the audit, `pytest.ini` was aligned to the actual root-level tests. The unmodified baseline previously failed collection in all eight test modules because `src` could not be imported.

## 8. Integration Contract

- Input: OpenFDA/FAERS JSON response; `normalize_record(raw_record, index, retrieved_at, source_url, requested_drug_name=None)`.
- Normalized value: `EvidenceRecord`, schema version `1.1`, serialized via `to_dict()`.
- Validation: `validate_evidence(record) -> (bool, list[str])`.
- Persistence: `add_evidence(list[dict]) -> int`, local file `evidence_output.json`.
- Semantics: association is `REPORTED_ASSOCIATION`; entity status is `MATCHED`, `AMBIGUOUS`, or `UNRESOLVED`.

This is the observed local API only. It is not yet an agreed Biotech-wide contract.

## 9. Known Limitations

No declared dependency manifest; no explicit synthetic/real origin field; no general field-type validation; conflicts sharing one source ID are silently skipped; live API behavior was not verified; output has no documented cross-module versioning or transport. The pipeline organizes reported evidence and must not be used to infer causality or make medical/regulatory decisions.

## 10. Evidence

- Executed test result and empty-input runtime result are recorded in [evidence_packet/verification.md](../../evidence_packet/verification.md).
- Source implementation and automated tests are in the repository root.
- No screenshot, live API sample capture, or deployment proof was generated in this audit.
