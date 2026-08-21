"""The source cell records: a column per letter unit, nested into words.

A CellColumn is what a row draws for one source unit: its role and tier, the
main column a riding mark attaches to, its provenance, status, silence and rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..ids import CellColumnId, CharacterId, LetterUnitId, OccurrenceId, WordId
from ..source_dtos import Silence
from ...model.address import KhilafId


class CellRole(StrEnum):
    """What the row draws, distinct from what the script wrote: a letter unit
    reads as a consonant or as a long-vowel carrier."""

    LETTER = "letter"
    HARAKA = "haraka"
    SUKUN = "sukun"
    TANWEEN = "tanween"
    MADD = "madd"


class CellTier(StrEnum):
    MAIN = "main"
    ABOVE = "above"
    BELOW = "below"


class CellStatus(StrEnum):
    PRESENT = "present"
    DROPPED = "dropped"


@dataclass(frozen=True, slots=True)
class CellColumn:
    id: CellColumnId
    role: CellRole
    text: str
    source_character_ids: tuple[CharacterId, ...]
    source_unit_ids: tuple[LetterUnitId, ...]
    tier: CellTier
    attached_to_column_id: CellColumnId | None
    status: CellStatus
    rule_occurrence_ids: tuple[OccurrenceId, ...]
    silence: Silence
    variant_id: KhilafId | None
    variant_choice: str | None


@dataclass(frozen=True, slots=True)
class CellWord:
    word_id: WordId
    columns: tuple[CellColumn, ...]


__all__ = [
    "CellColumn",
    "CellRole",
    "CellStatus",
    "CellTier",
    "CellWord",
]
