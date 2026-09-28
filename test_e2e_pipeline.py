"""
End-to-end integration tests for the pharmacovigilance pipeline.

Phase 2:
Advanced Integration & Security Hardening

These tests verify the complete processing path:

Raw source record
    -> Normalization
    -> Evidence validation
    -> Evidence storage
"""

from src.normalize_evidence import normalize_record
from src.evidence_schema import validate_evidence
from src.evidence_store import add_evidence


def make_raw_record(record_id="E2E001"):
    """Create a deterministic OpenFDA-style safety record."""

    return {
        "safetyreportid": record_id,
        "patient": {
            "drug": [
                {
                    "medicinalproduct": "IBUPROFEN",
                    "openfda": {
                        "application_number": [
                            "NDA000001"
                        ]
                    },
                }
            ],
            "reaction": [
                {
                    "reactionmeddrapt": "HEADACHE"
                }
            ],
        },
    }


def test_e2e_raw_record_to_validated_evidence():
    """Verify raw source data becomes valid EvidenceRecord."""

    raw_record = make_raw_record()

    evidence = normalize_record(
        raw_record,
        1,
        "2026-09-11T10:00:00+00:00",
        "https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen",
    )

    valid, errors = validate_evidence(evidence)

    assert valid is True
    assert errors == []

    assert evidence.drug_name == "IBUPROFEN"
    assert evidence.adverse_event == "HEADACHE"
    assert evidence.source == "OpenFDA/FAERS"
    assert evidence.source_record_id == "E2E001"


def test_e2e_evidence_can_be_stored(tmp_path):
    """Verify validated evidence reaches the storage layer."""

    import src.evidence_store as store

    original_file = store.EVIDENCE_FILE
    store.EVIDENCE_FILE = str(tmp_path / "evidence_output.json")

    try:
        raw_record = make_raw_record("E2E002")

        evidence = normalize_record(
            raw_record,
            1,
            "2026-09-11T10:00:00+00:00",
            "https://api.fda.gov/drug/event.json",
            requested_drug_name="ibuprofen",
        )

        valid, errors = validate_evidence(evidence)

        assert valid is True
        assert errors == []

        added = add_evidence([evidence.to_dict()])

        assert added == 1

    finally:
        store.EVIDENCE_FILE = original_file


def test_e2e_duplicate_is_not_stored_twice(tmp_path):
    """Verify the complete pipeline protects against duplicate evidence."""

    import src.evidence_store as store

    original_file = store.EVIDENCE_FILE
    store.EVIDENCE_FILE = str(tmp_path / "evidence_output.json")

    try:
        raw_record = make_raw_record("E2E003")

        evidence = normalize_record(
            raw_record,
            1,
            "2026-09-11T10:00:00+00:00",
            "https://api.fda.gov/drug/event.json",
            requested_drug_name="ibuprofen",
        )

        valid, errors = validate_evidence(evidence)

        assert valid is True
        assert errors == []

        first = add_evidence([evidence.to_dict()])
        second = add_evidence([evidence.to_dict()])

        assert first == 1
        assert second == 0

    finally:
        store.EVIDENCE_FILE = original_file


def test_e2e_invalid_record_is_rejected_by_validation():
    """Verify invalid evidence does not pass the schema boundary."""

    raw_record = make_raw_record("E2E004")

    evidence = normalize_record(
        raw_record,
        1,
        "2026-09-11T10:00:00+00:00",
        "https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen",
    )

    evidence.evidence_id = ""

    valid, errors = validate_evidence(evidence)

    assert valid is False
    assert len(errors) > 0