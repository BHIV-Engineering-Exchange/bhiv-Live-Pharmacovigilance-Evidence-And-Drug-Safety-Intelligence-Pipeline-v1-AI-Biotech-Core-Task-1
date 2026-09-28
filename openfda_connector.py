import requests
from datetime import datetime, timezone


OPENFDA_URL = "https://api.fda.gov/drug/event.json"


def search_drug(drug_name, limit=10):
    """Retrieve adverse-event records from OpenFDA."""

    retrieved_at = datetime.now(timezone.utc).isoformat()

    params = {
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "limit": limit
    }

    try:
        response = requests.get(
            OPENFDA_URL,
            params=params,
            timeout=30
        )

        # OpenFDA returns 404 when no matching records are found
        if response.status_code == 404:
            return {
                "success": True,
                "source": "OpenFDA/FAERS",
                "retrieved_at": retrieved_at,
                "source_url": response.url,
                "record_count": 0,
                "raw_response": {
                    "results": []
                }
            }

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            return {
                "success": False,
                "error": "Unexpected response format.",
                "retrieved_at": retrieved_at
            }

        results = data.get("results", [])

        return {
            "success": True,
            "source": "OpenFDA/FAERS",
            "retrieved_at": retrieved_at,
            "source_url": response.url,
            "record_count": len(results),
            "raw_response": data
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": f"API request failed: {error}",
            "retrieved_at": retrieved_at
        }

    except ValueError as error:
        return {
            "success": False,
            "error": f"Invalid JSON response: {error}",
            "retrieved_at": retrieved_at
        }