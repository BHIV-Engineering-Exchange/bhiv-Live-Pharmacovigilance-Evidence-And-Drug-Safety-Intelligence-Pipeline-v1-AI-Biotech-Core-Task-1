from src.normalize_evidence import normalize_record
from src.evidence_schema import validate_evidence


def make_raw_record(
    drug_name="IBUPROFEN",
    reaction="NAUSEA",
    source_record_id="123456"
):
    """Create a minimal OpenFDA/FAERS-style record for testing."""

    return {
        "safetyreportid": source_record_id,
        "patient": {
            "drug": [
                {
                    "medicinalproduct": drug_name,
                    "openfda": {
                        "application_number": ["NDA123456"]
                    }
                }
            ],
            "reaction": [
                {
                    "reactionmeddrapt": reaction
                }
            ]
        }
    }


def test_normalize_record_extracts_drug_and_reaction():
    raw_record = make_raw_record()

    evidence = normalize_record(
        raw_record,
        index=1,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen"
    )

    assert evidence.drug_name == "IBUPROFEN"
    assert evidence.adverse_event == "NAUSEA"
    assert evidence.source_record_id == "123456"
    assert evidence.drug_identifier == "NDA123456"


def test_normalize_record_resolves_matching_entity():
    raw_record = make_raw_record(drug_name="IBUPROFEN")

    evidence = normalize_record(
        raw_record,
        index=1,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen"
    )

    assert evidence.entity_resolution_status == "MATCHED"
    assert evidence.canonical_entity_name == "IBUPROFEN"
    assert evidence.canonical_entity_identifier == "NDA123456"


def test_normalize_record_marks_nonmatching_entity_unresolved():
    raw_record = make_raw_record(drug_name="ASPIRIN")

    evidence = normalize_record(
        raw_record,
        index=1,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen"
    )

    assert evidence.entity_resolution_status == "UNRESOLVED"
    assert evidence.canonical_entity_name is None
    assert evidence.canonical_entity_identifier is None


def test_normalize_record_sets_reported_association():
    raw_record = make_raw_record()

    evidence = normalize_record(
        raw_record,
        index=1,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen"
    )

    assert evidence.association_type == "REPORTED_ASSOCIATION"


def test_normalize_record_contains_provenance():
    raw_record = make_raw_record()

    evidence = normalize_record(
        raw_record,
        index=1,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen"
    )

    assert evidence.provenance["source_system"] == "OpenFDA"
    assert evidence.provenance["underlying_dataset"] == "FAERS"
    assert evidence.provenance["retrieval_method"] == "REST API"
    assert evidence.provenance["source_record_id"] == "123456"


def test_normalize_record_handles_malformed_record():
    raw_record = {
        "safetyreportid": "999999",
        "patient": {
            "drug": "not-a-list",
            "reaction": "not-a-list"
        }
    }

    evidence = normalize_record(
        raw_record,
        index=1,
        retrieved_at="2026-08-31T10:00:00+00:00",
        source_url="https://api.fda.gov/drug/event.json",
        requested_drug_name="ibuprofen"
    )

    valid, errors = validate_evidence(evidence)

    assert valid
    assert errors == []
    assert evidence.drug_name is None
    assert evidence.adverse_event is None
    assert evidence.entity_resolution_status == "UNRESOLVED"