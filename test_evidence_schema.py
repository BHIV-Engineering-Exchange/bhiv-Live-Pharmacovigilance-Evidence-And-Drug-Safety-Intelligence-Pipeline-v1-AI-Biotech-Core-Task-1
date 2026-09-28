from src.evidence_schema import (
    EvidenceRecord,
    validate_evidence,
)


def make_valid_record(provenance=None):
    """Create a valid EvidenceRecord for schema testing."""

    if provenance is None:
        provenance = {
            "source_system": "OpenFDA",
            "underlying_dataset": "FAERS",
            "retrieval_method": "REST API",
            "transformation": "raw JSON -> normalized evidence",
        }

    return EvidenceRecord(
        evidence_id="EV-123456",
        drug_name="IBUPROFEN",
        drug_identifier="NDA123456",
        adverse_event="NAUSEA",
        source="OpenFDA/FAERS",
        source_record_id="FAERS-123456",
        evidence_type="FAERS adverse-event report",
        event_date=None,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        schema_version="1.1",
        provenance=provenance,
        raw_record_reference="FAERS-123456",
        entity_resolution_status="MATCHED",
        canonical_entity_name="IBUPROFEN",
        canonical_entity_identifier="NDA123456",
        association_type="REPORTED_ASSOCIATION",
    )


def test_valid_evidence_passes_validation():
    record = make_valid_record()

    valid, errors = validate_evidence(record)

    assert valid
    assert errors == []


def test_empty_provenance_fails_validation():
    record = make_valid_record(provenance={})

    valid, errors = validate_evidence(record)

    assert not valid
    assert "Missing provenance field: source_system" in errors
    assert "Missing provenance field: underlying_dataset" in errors
    assert "Missing provenance field: retrieval_method" in errors
    assert "Missing provenance field: transformation" in errors


def test_incomplete_provenance_fails_validation():
    record = make_valid_record(
        provenance={
            "source_system": "OpenFDA",
            "underlying_dataset": "FAERS",
        }
    )

    valid, errors = validate_evidence(record)

    assert not valid
    assert "Missing provenance field: retrieval_method" in errors
    assert "Missing provenance field: transformation" in errors


def test_invalid_provenance_type_fails_validation():
    record = make_valid_record(
        provenance="invalid provenance"
    )

    valid, errors = validate_evidence(record)

    assert not valid
    assert "Provenance must be a dictionary" in errors


def test_invalid_entity_resolution_status_fails_validation():
    record = make_valid_record()
    record.entity_resolution_status = "GUESS"

    valid, errors = validate_evidence(record)

    assert not valid
    assert any(
        "Invalid entity_resolution_status" in error
        for error in errors
    )


def test_invalid_association_type_fails_validation():
    record = make_valid_record()
    record.association_type = "CAUSAL"

    valid, errors = validate_evidence(record)

    assert not valid
    assert any(
        "Invalid association_type" in error
        for error in errors
    )