"""The cell records: a column per letter unit and a sound cell per core sound.

A CellColumn draws one source unit with its role, tier, attachment, provenance,
status, silence, rules, and sounds; a CellSound spans one sound's columns.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..dtos import BoundaryState
from ..ids import (
    BoundaryId,
    CellColumnId,
    CellRunId,
    CanonicalSlotId,
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


class CellGroupKind(StrEnum):
    """The visual relation that makes several columns one rendered group."""

    BASE = "base"
    VOWEL = "vowel"


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
    slot_ids: tuple[CanonicalSlotId, ...] = ()


@dataclass(frozen=True, slots=True)
class CellSound:
    sound_id: SoundId
    column_ids: tuple[CellColumnId, ...]
    rule_occurrence_ids: tuple[OccurrenceId, ...]


@dataclass(frozen=True, slots=True)
class CellGroup:
    """One producer-decided grapheme group, keyed by its main column."""

    key: CellColumnId
    kind: CellGroupKind
    column_ids: tuple[CellColumnId, ...]
    sound_ids: tuple[SoundId, ...]


@dataclass(frozen=True, slots=True)
class CellRun:
    """One named-letter span over a flat word cell row."""

    id: CellRunId
    source_unit_id: LetterUnitId
    column_ids: tuple[CellColumnId, ...]


@dataclass(frozen=True, slots=True)
class CellBridge:
    """A merger's shared sound, rendered once across its two endpoints."""

    merger_id: MergerId
    before_column_ids: tuple[CellColumnId, ...]
    after_column_ids: tuple[CellColumnId, ...]
    sound: CellSound


@dataclass(frozen=True, slots=True)
class CellWord:
    word_id: WordId
    columns: tuple[CellColumn, ...]
    sounds: tuple[CellSound, ...]
    groups: tuple[CellGroup, ...] = ()
    runs: tuple[CellRun, ...] = ()
    bridges: tuple[CellBridge, ...] = ()


@dataclass(frozen=True, slots=True)
class CellBoundary:
    """The between-word junction: its stop-sign pause column and a bridge per
    cross-word merger."""

    boundary_id: BoundaryId
    columns: tuple[CellColumn, ...]
    bridges: tuple[CellBridge, ...]
    sounds: tuple[CellSound, ...] = ()
    state: BoundaryState | None = None
    verse_end: int | None = None
    exclusive_group: int | None = None


@dataclass(frozen=True, slots=True)
class CellView:
    words: tuple[CellWord, ...]
    boundaries: tuple[CellBoundary, ...]


__all__ = [
    "CellBoundary",
    "CellBridge",
    "CellColumn",
    "CellGroup",
    "CellGroupKind",
    "CellRole",
    "CellRun",
    "CellSide",
    "CellSound",
    "CellStatus",
    "CellTier",
    "CellView",
    "CellWord",
]
