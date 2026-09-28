from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


SCHEMA_VERSION = "1.1"

MATCHED = "MATCHED"
AMBIGUOUS = "AMBIGUOUS"
UNRESOLVED = "UNRESOLVED"

REPORTED_ASSOCIATION = "REPORTED_ASSOCIATION"


@dataclass
class EvidenceRecord:
    evidence_id: str
    drug_name: Optional[str]
    drug_identifier: Optional[str]
    adverse_event: Optional[str]
    source: str
    source_record_id: Optional[str]
    evidence_type: str
    event_date: Optional[str]
    retrieved_at: str
    source_url: str
    schema_version: str
    provenance: Dict[str, Any]
    raw_record_reference: Optional[str]

    entity_resolution_status: str = UNRESOLVED
    canonical_entity_name: Optional[str] = None
    canonical_entity_identifier: Optional[str] = None

    association_type: str = REPORTED_ASSOCIATION

    def to_dict(self):
        return asdict(self)


def generate_evidence_id(
    index: int,
    source_record_id: Optional[str] = None
) -> str:
    """
    Generate a deterministic evidence identifier.

    A source record ID is preferred when available.
    The index is retained as a fallback.
    """

    if source_record_id:
        safe_source_id = str(source_record_id).strip()
        return f"EV-{safe_source_id}"

    return f"EV-{index:06d}"


def validate_evidence(record: EvidenceRecord):
    """Validate required evidence-integrity fields."""

    errors = []

    if not record.evidence_id:
        errors.append("Missing evidence_id")

    if not record.source:
        errors.append("Missing source")

    if not record.evidence_type:
        errors.append("Missing evidence_type")

    if not record.retrieved_at:
        errors.append("Missing retrieved_at")

    if not record.source_url:
        errors.append("Missing source_url")

    if not record.schema_version:
        errors.append("Missing schema_version")

    # ---------------------------------------------------------
    # Provenance validation
    # ---------------------------------------------------------

    if not isinstance(record.provenance, dict):
        errors.append("Provenance must be a dictionary")

    else:

        required_provenance_fields = [
            "source_system",
            "underlying_dataset",
            "retrieval_method",
            "transformation",
        ]

        for field in required_provenance_fields:

            value = record.provenance.get(field)

            if value is None or str(value).strip() == "":
                errors.append(
                    f"Missing provenance field: {field}"
                )

    # ---------------------------------------------------------
    # Entity-resolution validation
    # ---------------------------------------------------------

    if record.entity_resolution_status not in {
        MATCHED,
        AMBIGUOUS,
        UNRESOLVED,
    }:
        errors.append(
            "Invalid entity_resolution_status: "
            f"{record.entity_resolution_status}"
        )

    if record.association_type != REPORTED_ASSOCIATION:
        errors.append(
            "Invalid association_type: "
            f"{record.association_type}"
        )

    return len(errors) == 0, errors