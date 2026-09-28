from src.entity_resolution import (
    AMBIGUOUS,
    MATCHED,
    UNRESOLVED,
    EntityCandidate,
    normalize_entity_name,
    resolve_entity,
)


def test_normalize_entity_name():
    assert normalize_entity_name("  Ibuprofen  ") == "ibuprofen"
    assert normalize_entity_name("IBUPROFEN") == "ibuprofen"
    assert normalize_entity_name("Ibuprofen   Tablet") == "ibuprofen tablet"
    assert normalize_entity_name(None) == ""


def test_exact_canonical_match():
    candidates = [
        EntityCandidate(
            canonical_name="Ibuprofen",
            identifier="TEST-IBU-001",
        )
    ]

    result = resolve_entity("ibuprofen", candidates)

    assert result.status == MATCHED
    assert result.canonical_name == "Ibuprofen"
    assert result.identifier == "TEST-IBU-001"


def test_exact_alias_match():
    candidates = [
        EntityCandidate(
            canonical_name="Ibuprofen",
            identifier="TEST-IBU-001",
            aliases=("ibu",),
        )
    ]

    result = resolve_entity("IBU", candidates)

    assert result.status == MATCHED
    assert result.canonical_name == "Ibuprofen"


def test_unknown_entity_is_unresolved():
    candidates = [
        EntityCandidate(
            canonical_name="Ibuprofen",
            identifier="TEST-IBU-001",
        )
    ]

    result = resolve_entity("Unknown Drug", candidates)

    assert result.status == UNRESOLVED
    assert result.canonical_name is None
    assert result.identifier is None


def test_ambiguous_entity_is_not_selected_arbitrarily():
    candidates = [
        EntityCandidate(
            canonical_name="Drug Alpha",
            identifier="ID-001",
            aliases=("shared-name",),
        ),
        EntityCandidate(
            canonical_name="Drug Beta",
            identifier="ID-002",
            aliases=("shared-name",),
        ),
    ]

    result = resolve_entity("shared-name", candidates)

    assert result.status == AMBIGUOUS
    assert result.canonical_name is None
    assert result.identifier is None
    assert set(result.candidates) == {"Drug Alpha", "Drug Beta"}


def test_empty_entity_is_unresolved():
    result = resolve_entity("", [])

    assert result.status == UNRESOLVED
    assert result.canonical_name is None