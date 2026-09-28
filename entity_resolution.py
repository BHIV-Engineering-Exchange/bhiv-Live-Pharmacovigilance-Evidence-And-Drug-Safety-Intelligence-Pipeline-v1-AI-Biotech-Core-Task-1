"""
Deterministic entity resolution for pharmacovigilance evidence.

This module intentionally uses conservative matching rules.
It does not attempt to create a complete drug ontology.

Resolution outcomes:
    MATCHED
    AMBIGUOUS
    UNRESOLVED
"""

from dataclasses import dataclass
from typing import List, Optional


MATCHED = "MATCHED"
AMBIGUOUS = "AMBIGUOUS"
UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EntityCandidate:
    """A candidate entity that may match the input."""

    canonical_name: str
    identifier: Optional[str] = None
    aliases: tuple = ()


@dataclass(frozen=True)
class ResolutionResult:
    """Deterministic result of entity resolution."""

    input_name: str
    normalized_name: str
    status: str
    canonical_name: Optional[str]
    identifier: Optional[str]
    candidates: tuple


def normalize_entity_name(name: Optional[str]) -> str:
    """
    Normalize an entity name for deterministic comparison.

    Rules:
    - None/empty input becomes an empty string.
    - Leading/trailing whitespace is removed.
    - Text is converted to lowercase.
    - Repeated internal whitespace is collapsed.
    """

    if name is None:
        return ""

    return " ".join(str(name).strip().lower().split())


def resolve_entity(
    name: Optional[str],
    candidates: List[EntityCandidate],
) -> ResolutionResult:
    """
    Resolve an input entity name using conservative deterministic rules.

    Matching order:
    1. Exact canonical-name match.
    2. Exact alias match.
    3. No match -> UNRESOLVED.
    4. More than one exact candidate -> AMBIGUOUS.

    The function never selects a candidate arbitrarily.
    """

    normalized_name = normalize_entity_name(name)

    if not normalized_name:
        return ResolutionResult(
            input_name=name or "",
            normalized_name="",
            status=UNRESOLVED,
            canonical_name=None,
            identifier=None,
            candidates=(),
        )

    exact_matches = []

    for candidate in candidates:
        canonical = normalize_entity_name(candidate.canonical_name)

        aliases = {
            normalize_entity_name(alias)
            for alias in candidate.aliases
        }

        if normalized_name == canonical or normalized_name in aliases:
            exact_matches.append(candidate)

    # No deterministic match.
    if not exact_matches:
        return ResolutionResult(
            input_name=str(name),
            normalized_name=normalized_name,
            status=UNRESOLVED,
            canonical_name=None,
            identifier=None,
            candidates=(),
        )

    # More than one valid candidate means the input is ambiguous.
    if len(exact_matches) > 1:
        return ResolutionResult(
            input_name=str(name),
            normalized_name=normalized_name,
            status=AMBIGUOUS,
            canonical_name=None,
            identifier=None,
            candidates=tuple(
                candidate.canonical_name
                for candidate in exact_matches
            ),
        )

    # Exactly one deterministic match.
    match = exact_matches[0]

    return ResolutionResult(
        input_name=str(name),
        normalized_name=normalized_name,
        status=MATCHED,
        canonical_name=match.canonical_name,
        identifier=match.identifier,
        candidates=(match.canonical_name,),
    )