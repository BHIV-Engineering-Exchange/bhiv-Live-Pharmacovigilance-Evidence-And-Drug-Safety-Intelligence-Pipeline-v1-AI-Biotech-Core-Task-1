"""
Live Pharmacovigilance Evidence and Drug Safety Intelligence Pipeline v1

Phase 2:
Advanced Integration & Security Hardening

Application entry point with:
- OpenFDA integration
- Evidence normalization
- Evidence validation
- Evidence storage
- Production monitoring
- Application-level error boundary
"""

from src.openfda_connector import search_drug
from src.normalize_evidence import normalize_record
from src.evidence_schema import validate_evidence
from src.evidence_store import add_evidence
from src.error_handler import handle_application_error
from src.monitoring import log_event


print("=" * 50)
print("PHARMACOVIGILANCE DRUG SAFETY SEARCH")
print("=" * 50)

try:
    drug_name = input("Enter drug name: ").strip()

    if not drug_name:
        print("Please enter a drug name.")
        log_event(
            "EMPTY_DRUG_INPUT",
            level="WARNING",
        )
    else:
        log_event(
            "DRUG_SEARCH_STARTED",
            drug=drug_name,
        )

        print()
        print("Searching OpenFDA...")
        print()

        result = search_drug(drug_name, limit=5)

        log_event(
            "OPENFDA_SEARCH_COMPLETED",
            drug=drug_name,
            success=result.get("success"),
            record_count=result.get("record_count", 0),
        )

        if not result["success"]:
            print("ERROR:")
            print(result["error"])

            log_event(
                "OPENFDA_SEARCH_FAILED",
                level="ERROR",
                drug=drug_name,
                error=result.get("error"),
            )

        elif result["record_count"] == 0:
            print("No safety records found for:", drug_name)

            log_event(
                "NO_EVIDENCE_FOUND",
                level="WARNING",
                drug=drug_name,
            )

        else:
            print("Records found:", result["record_count"])
            print()

            new_evidence = []

            for index, raw_record in enumerate(
                result["raw_response"].get("results", []),
                start=1,
            ):
                evidence = normalize_record(
                    raw_record,
                    index,
                    result["retrieved_at"],
                    result["source_url"],
                    requested_drug_name=drug_name,
                )

                valid, errors = validate_evidence(evidence)

                if valid:
                    new_evidence.append(evidence.to_dict())

                    print("-" * 50)
                    print("Evidence ID:", evidence.evidence_id)
                    print("Drug:", evidence.drug_name)

                    print(
                        "Entity Resolution:",
                        evidence.entity_resolution_status,
                    )

                    print(
                        "Canonical Entity:",
                        evidence.canonical_entity_name,
                    )

                    print(
                        "Adverse Event:",
                        evidence.adverse_event,
                    )

                    print(
                        "Association Type:",
                        evidence.association_type,
                    )

                    print("Source:", evidence.source)

                    print(
                        "Source Record ID:",
                        evidence.source_record_id,
                    )

                    print(
                        "Evidence Type:",
                        evidence.evidence_type,
                    )

                    print(
                        "Retrieved At:",
                        evidence.retrieved_at,
                    )

                    print("-" * 50)
                    print()

                else:
                    print("Validation failed:")
                    print(errors)

                    log_event(
                        "EVIDENCE_VALIDATION_FAILED",
                        level="WARNING",
                        drug=drug_name,
                        errors=errors,
                    )

            log_event(
                "EVIDENCE_VALIDATED",
                drug=drug_name,
                record_count=len(new_evidence),
            )

            added = add_evidence(new_evidence)

            log_event(
                "EVIDENCE_STORAGE_COMPLETED",
                drug=drug_name,
                records_added=added,
            )

            print("=" * 50)
            print("New evidence records saved:", added)
            print("=" * 50)

except Exception as error:
    result = handle_application_error(error)

    log_event(
        "APPLICATION_ERROR",
        level="ERROR",
        error_type=result["error_type"],
    )

    print()
    print("APPLICATION ERROR")
    print(result["error"])
    print()
    print("The pipeline stopped safely.")