import hashlib
import json
import os


EVIDENCE_FILE = "evidence_output.json"


def load_evidence():
    """Load existing evidence records."""

    if not os.path.exists(EVIDENCE_FILE):
        return []

    try:
        with open(EVIDENCE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_evidence(records):
    """Save evidence records."""

    with open(EVIDENCE_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)


def _record_fingerprint(record):
    """
    Create a deterministic fingerprint for an evidence record.

    The fingerprint is used when source_record_id is missing.
    """

    fingerprint_data = {
        "drug_name": record.get("drug_name"),
        "drug_identifier": record.get("drug_identifier"),
        "adverse_event": record.get("adverse_event"),
        "source": record.get("source"),
        "evidence_type": record.get("evidence_type"),
        "event_date": record.get("event_date"),
        "association_type": record.get("association_type"),
    }

    canonical_data = json.dumps(
        fingerprint_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()


def _record_identity(record):
    """
    Return the deterministic identity of an evidence record.

    Source record ID is preferred because it represents the original
    source identity.

    If unavailable, a deterministic content fingerprint is used.
    """

    source_id = record.get("source_record_id")

    if source_id:
        return ("source_record_id", str(source_id).strip())

    return ("fingerprint", _record_fingerprint(record))


def add_evidence(new_records):
    """
    Add only evidence records that are not already stored.

    Duplicate detection uses:
    1. source_record_id when available;
    2. deterministic content fingerprint otherwise.
    """

    existing_records = load_evidence()

    existing_identities = {
        _record_identity(record)
        for record in existing_records
        if isinstance(record, dict)
    }

    added = 0

    for record in new_records:

        if not isinstance(record, dict):
            continue

        identity = _record_identity(record)

        if identity in existing_identities:
            continue

        existing_records.append(record)
        existing_identities.add(identity)
        added += 1

    save_evidence(existing_records)

    return added