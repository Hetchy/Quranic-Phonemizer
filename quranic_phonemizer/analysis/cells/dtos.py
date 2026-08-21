"""The cell records: a column per letter unit and a sound cell per core sound.

A CellColumn draws one source unit with its role, tier, attachment, provenance,
status, silence, rules, and sounds; a CellSound spans one sound's columns.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..ids import (
    CellColumnId,
    CharacterId,
    LetterUnitId,
    OccurrenceId,
    SoundId,
    WordId,
)
from ..source_dtos import Silence
from ...model.address import KhilafId


class CellRole(StrEnum):
    """What the row draws, distinct from what the script wrote: a letter unit
    reads as a consonant or as a long-vowel carrier. A gap column stands for a
    performed sound the source spells no presenter for."""

    LETTER = "letter"
    HARAKA = "haraka"
    SUKUN = "sukun"
    TANWEEN = "tanween"
    MADD = "madd"
    GAP = "gap"


class CellTier(StrEnum):
    MAIN = "main"
    ABOVE = "above"
    BELOW = "below"


class CellStatus(StrEnum):
    PRESENT = "present"
    DROPPED = "dropped"
    GAP = "gap"


class CellSide(StrEnum):
    BEFORE = "before"
    AFTER = "after"


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
    owned_sound_ids: tuple[SoundId, ...]
    presented_sound_ids: tuple[SoundId, ...]
    anchor_unit_id: LetterUnitId | None
    side: CellSide | None


@dataclass(frozen=True, slots=True)
class CellSound:
    sound_id: SoundId
    column_ids: tuple[CellColumnId, ...]
    rule_occurrence_ids: tuple[OccurrenceId, ...]


@dataclass(frozen=True, slots=True)
class CellWord:
    word_id: WordId
    columns: tuple[CellColumn, ...]
    sounds: tuple[CellSound, ...]


__all__ = [
    "CellColumn",
    "CellRole",
    "CellSide",
    "CellSound",
    "CellStatus",
    "CellTier",
    "CellWord",
]
