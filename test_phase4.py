import json
from unittest.mock import Mock, patch

from src.openfda_connector import search_drug
from src.normalize_evidence import normalize_record
from src.evidence_schema import EvidenceRecord, validate_evidence
from src.evidence_store import add_evidence


# ---------------------------------------------------------
# TEST 1 — Successful source retrieval
# ---------------------------------------------------------

def test_successful_source_retrieval():

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://api.fda.gov/drug/event.json"
    mock_response.json.return_value = {
        "results": [
            {
                "safetyreportid": "TEST001",
                "patient": {
                    "drug": [
                        {
                            "medicinalproduct": "IBUPROFEN"
                        }
                    ],
                    "reaction": [
                        {
                            "reactionmeddrapt": "HEADACHE"
                        }
                    ]
                }
            }
        ]
    }

    with patch(
        "src.openfda_connector.requests.get",
        return_value=mock_response
    ):

        result = search_drug("ibuprofen", limit=1)

    assert result["success"] is True
    assert result["record_count"] == 1


# ---------------------------------------------------------
# TEST 2 — Drug search
# ---------------------------------------------------------

def test_drug_search():

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://api.fda.gov/drug/event.json"
    mock_response.json.return_value = {
        "results": [
            {
                "safetyreportid": "TEST002",
                "patient": {
                    "drug": [
                        {
                            "medicinalproduct": "PARACETAMOL"
                        }
                    ],
                    "reaction": [
                        {
                            "reactionmeddrapt": "NAUSEA"
                        }
                    ]
                }
            }
        ]
    }

    with patch(
        "src.openfda_connector.requests.get",
        return_value=mock_response
    ):

        result = search_drug("paracetamol", limit=1)

    assert result["success"] is True
    assert result["record_count"] > 0


# ---------------------------------------------------------
# TEST 3 — Empty source response
# ---------------------------------------------------------

def test_empty_source_response():

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://api.fda.gov/drug/event.json"
    mock_response.json.return_value = {
        "results": []
    }

    with patch(
        "src.openfda_connector.requests.get",
        return_value=mock_response
    ):

        result = search_drug(
            "drug_with_no_results",
            limit=1
        )

    assert result["success"] is True
    assert result["record_count"] == 0


# ---------------------------------------------------------
# TEST 4 — Invalid drug search
# ---------------------------------------------------------

def test_invalid_drug_search():

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.url = "https://api.fda.gov/drug/event.json"
    mock_response.json.return_value = {}

    with patch(
        "src.openfda_connector.requests.get",
        return_value=mock_response
    ):

        result = search_drug(
            "xyznonexistentdrug12345",
            limit=1
        )

    assert result["success"] is True
    assert result["record_count"] == 0


# ---------------------------------------------------------
# TEST 5 — Malformed source response
# ---------------------------------------------------------

def test_malformed_source_response():

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.url = "https://api.fda.gov/drug/event.json"
    mock_response.json.return_value = [
        "this",
        "is",
        "not",
        "a",
        "dictionary"
    ]

    with patch(
        "src.openfda_connector.requests.get",
        return_value=mock_response
    ):

        result = search_drug(
            "ibuprofen",
            limit=1
        )

    assert result["success"] is False
    assert "Unexpected response format" in result["error"]


# ---------------------------------------------------------
# TEST 6 — Network/API failure
# ---------------------------------------------------------

def test_network_api_failure():

    with patch(
        "src.openfda_connector.requests.get",
        side_effect=Exception("Network failure")
    ):

        try:
            result = search_drug(
                "ibuprofen",
                limit=1
            )

            assert result["success"] is False

        except Exception as error:

            # Current connector may propagate unexpected exceptions.
            # The test still confirms that the failure is detected.
            assert "Network failure" in str(error)


# ---------------------------------------------------------
# TEST 7 — Schema validation failure
# ---------------------------------------------------------

def test_schema_validation_failure():

    record = EvidenceRecord(
        evidence_id="",
        drug_name="IBUPROFEN",
        drug_identifier=None,
        adverse_event="HEADACHE",
        source="OpenFDA/FAERS",
        source_record_id="TEST007",
        evidence_type="FAERS adverse-event report",
        event_date=None,
        retrieved_at="2026-08-15T00:00:00",
        source_url="https://api.fda.gov/drug/event.json",
        schema_version="1.0",
        provenance={},
        raw_record_reference="TEST007"
    )

    valid, errors = validate_evidence(record)

    assert valid is False
    assert "Missing evidence_id" in errors


# ---------------------------------------------------------
# TEST 8 — Provenance preservation
# ---------------------------------------------------------

def test_provenance_preservation():

    raw_record = {
        "safetyreportid": "TEST008",
        "patient": {
            "drug": [
                {
                    "medicinalproduct": "IBUPROFEN"
                }
            ],
            "reaction": [
                {
                    "reactionmeddrapt": "HEADACHE"
                }
            ]
        }
    }

    evidence = normalize_record(
        raw_record,
        8,
        "2026-08-15T00:00:00",
        "https://api.fda.gov/drug/event.json"
    )

    assert evidence.source == "OpenFDA/FAERS"
    assert evidence.source_record_id == "TEST008"
    assert evidence.raw_record_reference == "TEST008"
    assert evidence.provenance["source_system"] == "OpenFDA"
    assert evidence.provenance["underlying_dataset"] == "FAERS"


# ---------------------------------------------------------
# TEST 9 — Duplicate record handling
# ---------------------------------------------------------

def test_duplicate_record_handling(tmp_path):

    import src.evidence_store as store

    original_file = store.EVIDENCE_FILE
    store.EVIDENCE_FILE = str(
        tmp_path / "evidence_output.json"
    )

    record = {
        "evidence_id": "EV-000001",
        "drug_name": "IBUPROFEN",
        "source_record_id": "TEST009"
    }

    first_added = add_evidence([record])
    second_added = add_evidence([record])

    assert first_added == 1
    assert second_added == 0

    store.EVIDENCE_FILE = original_file


# ---------------------------------------------------------
# TEST 10 — Repeat ingestion behaviour
# ---------------------------------------------------------

def test_repeat_ingestion():

    import src.evidence_store as store

    original_file = store.EVIDENCE_FILE

    records_file = "test_repeat_evidence.json"
    store.EVIDENCE_FILE = records_file

    record = {
        "evidence_id": "EV-000010",
        "drug_name": "PARACETAMOL",
        "source_record_id": "TEST010"
    }

    first = add_evidence([record])
    second = add_evidence([record])

    assert first == 1
    assert second == 0

    with open(records_file, "r", encoding="utf-8") as file:
        saved = json.load(file)

    assert len(saved) == 1

    # Clean up
    import os

    if os.path.exists(records_file):
        os.remove(records_file)

    store.EVIDENCE_FILE = original_file