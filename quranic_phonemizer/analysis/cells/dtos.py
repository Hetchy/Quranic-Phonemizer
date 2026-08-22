"""The cell records: a column per letter unit and a sound cell per core sound.

A CellColumn draws one source unit with its role, tier, attachment, provenance,
status, silence, rules, and sounds; a CellSound spans one sound's columns.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..ids import (
    BoundaryId,
    CellColumnId,
    CharacterId,
    LetterUnitId,
    MergerId,
    OccurrenceId,
    SoundId,
    WordId,
)
from ..source_dtos import Silence
from ...model.address import KhilafId


class CellRole(StrEnum):
    """What the row draws, distinct from what the script wrote: a consonant or
    long-vowel carrier for a letter unit, a boundary's written pause sign for a
    stop_sign column, a source-less performed sound for a gap column."""

    LETTER = "letter"
    HARAKA = "haraka"
    SUKUN = "sukun"
    TANWEEN = "tanween"
    MADD = "madd"
    STOP_SIGN = "stop_sign"
    GAP = "gap"


class CellTier(StrEnum):
    MAIN = "main"
    ABOVE = "above"
    BELOW = "below"


class CellStatus(StrEnum):
    PRESENT = "present"
    INSERTED = "inserted"
    REPLACED = "replaced"
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


@dataclass(frozen=True, slots=True)
class CellBridge:
    """A cross-word merger's shared sound, rendered once between the words. Its
    endpoints are the contributor's presenter columns and the host's owner
    columns, so a renderer co-highlights both sides of the join."""

    merger_id: MergerId
    before_column_ids: tuple[CellColumnId, ...]
    after_column_ids: tuple[CellColumnId, ...]
    sound: CellSound


@dataclass(frozen=True, slots=True)
class CellBoundary:
    """The between-word junction: its stop-sign pause column and a bridge per
    cross-word merger."""

    boundary_id: BoundaryId
    columns: tuple[CellColumn, ...]
    bridges: tuple[CellBridge, ...]


@dataclass(frozen=True, slots=True)
class CellView:
    words: tuple[CellWord, ...]
    boundaries: tuple[CellBoundary, ...]


__all__ = [
    "CellBoundary",
    "CellBridge",
    "CellColumn",
    "CellRole",
    "CellSide",
    "CellSound",
    "CellStatus",
    "CellTier",
    "CellView",
    "CellWord",
]
