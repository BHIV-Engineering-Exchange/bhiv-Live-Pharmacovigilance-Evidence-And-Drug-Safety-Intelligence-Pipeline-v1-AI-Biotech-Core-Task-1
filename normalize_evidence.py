from src.evidence_schema import EvidenceRecord, generate_evidence_id
from src.entity_resolution import (
    EntityCandidate,
    resolve_entity,
)


def normalize_record(
    raw_record,
    index,
    retrieved_at,
    source_url,
    requested_drug_name=None,
):
    """
    Convert one OpenFDA/FAERS record into our standard EvidenceRecord.

    Entity resolution is conservative:
    - An exact normalized match is MATCHED.
    - Multiple exact candidates are AMBIGUOUS.
    - No match is UNRESOLVED.

    The function does not infer causality.
    A FAERS record is represented as a reported association.
    """

    if not isinstance(raw_record, dict):
        raise ValueError("raw_record must be a dictionary")

    patient = raw_record.get("patient", {})

    if not isinstance(patient, dict):
        patient = {}

    drugs = patient.get("drug", [])
    reactions = patient.get("reaction", [])

    if not isinstance(drugs, list):
        drugs = []

    if not isinstance(reactions, list):
        reactions = []

    # ---------------------------------------------------------
    # Extract first reported drug
    # ---------------------------------------------------------

    drug_name = None
    drug_identifier = None

    if drugs:
        first_drug = drugs[0]

        if isinstance(first_drug, dict):

            drug_name = first_drug.get("medicinalproduct")

            openfda = first_drug.get("openfda", {})

            if isinstance(openfda, dict):

                identifiers = openfda.get(
                    "application_number",
                    []
                )

                if isinstance(identifiers, list) and identifiers:
                    drug_identifier = identifiers[0]

    # ---------------------------------------------------------
    # Extract first reported reaction
    # ---------------------------------------------------------

    adverse_event = None

    if reactions:

        first_reaction = reactions[0]

        if isinstance(first_reaction, dict):
            adverse_event = first_reaction.get(
                "reactionmeddrapt"
            )

    # ---------------------------------------------------------
    # Original OpenFDA/FAERS report ID
    # ---------------------------------------------------------

    source_record_id = raw_record.get(
        "safetyreportid"
    )

    # ---------------------------------------------------------
    # Deterministic entity resolution
    # ---------------------------------------------------------

    entity_resolution_status = "UNRESOLVED"
    canonical_entity_name = None
    canonical_entity_identifier = None

    if requested_drug_name and drug_name:

        candidate = EntityCandidate(
            canonical_name=str(drug_name),
            identifier=(
                str(drug_identifier)
                if drug_identifier
                else None
            ),
        )

        resolution = resolve_entity(
            requested_drug_name,
            [candidate],
        )

        entity_resolution_status = resolution.status
        canonical_entity_name = resolution.canonical_name
        canonical_entity_identifier = resolution.identifier

    # ---------------------------------------------------------
    # Provenance
    # ---------------------------------------------------------

    provenance = {
        "source_system": "OpenFDA",
        "underlying_dataset": "FAERS",
        "retrieval_method": "REST API",
        "transformation": (
            "raw JSON -> normalized evidence"
        ),
        "source_record_id": source_record_id,
    }

    # ---------------------------------------------------------
    # Create normalized evidence record
    # ---------------------------------------------------------

    record = EvidenceRecord(
        evidence_id=generate_evidence_id(index),
        drug_name=drug_name,
        drug_identifier=drug_identifier,
        adverse_event=adverse_event,
        source="OpenFDA/FAERS",
        source_record_id=source_record_id,
        evidence_type="FAERS adverse-event report",
        event_date=None,
        retrieved_at=retrieved_at,
        source_url=source_url,
        schema_version="1.1",
        provenance=provenance,
        raw_record_reference=source_record_id,

        entity_resolution_status=entity_resolution_status,
        canonical_entity_name=canonical_entity_name,
        canonical_entity_identifier=(
            canonical_entity_identifier
        ),

        association_type="REPORTED_ASSOCIATION",
    )

    return record