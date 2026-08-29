"""Result-local identities for the native result.

Each is its own type, distinct from a model id: a validator rejects a
wrong-kind id even where the same integer names something in another space.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Bumped when a DTO field or a role, status, state, or tier value is added,
#: removed, or changes meaning. A rule joining or leaving the catalogue does
#: not bump it.
SCHEMA_VERSION = 3


@dataclass(frozen=True, slots=True, order=True)
class WordId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class BoundaryId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class SoundId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class OccurrenceId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class MergerId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class CharacterId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class LetterUnitId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class HighlightId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class CellColumnId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class CellRunId:
    value: int


@dataclass(frozen=True, slots=True, order=True)
class CanonicalSlotId:
    value: str


@dataclass(frozen=True, slots=True, order=True)
class RuleId:
    """The stable rule identifier a `RuleDefinition` and every occurrence that
    cites it share. Its value is the model rule name."""

    value: str


__all__ = [
    "SCHEMA_VERSION",
    "BoundaryId",
    "CellColumnId",
    "CellRunId",
    "CanonicalSlotId",
    "CharacterId",
    "HighlightId",
    "LetterUnitId",
    "MergerId",
    "OccurrenceId",
    "RuleId",
    "SoundId",
    "WordId",
]
