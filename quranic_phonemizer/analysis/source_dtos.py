"""The source view's records: the exact characters and the units over them.

A Character is one scalar; a LetterUnit is the token the script wrote, with the
sounds it owns or presents, the rules placed on it, and why it is silent.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .ids import (
    BoundaryId,
    CharacterId,
    LetterUnitId,
    MergerId,
    OccurrenceId,
    SoundId,
    WordId,
)


class CharacterKind(StrEnum):
    LEXICAL = "lexical"
    SEPARATOR = "separator"
    STOP_SIGN = "stop_sign"


class LetterUnitKind(StrEnum):
    """What the script wrote at a unit, not what the cell row draws. A carrier
    the rasm leaves out and writes small is still a letter."""

    LETTER = "letter"
    HARAKA = "haraka"
    SUKUN = "sukun"
    TANWEEN = "tanween"


class LiteralSilence(StrEnum):
    """A written letter left unsaid without a performance rule."""

    ORTHOGRAPHIC = "orthographic_silence"
    VARIANT = "variant_silence"


#: A unit is silent for a reason, and the reason is either the occurrence that
#: silenced it or a literal source/variant reason; never both, never invented.
Silence = OccurrenceId | LiteralSilence | None


@dataclass(frozen=True, slots=True)
class Character:
    id: CharacterId
    index: int
    text: str
    kind: CharacterKind
    word_id: WordId | None
    boundary_id: BoundaryId | None
    letter_unit_id: LetterUnitId | None


@dataclass(frozen=True, slots=True)
class LetterUnit:
    id: LetterUnitId
    word_id: WordId
    character_ids: tuple[CharacterId, ...]
    ranges: tuple[tuple[int, int], ...]
    text: str
    kind: LetterUnitKind
    written_on_unit_id: LetterUnitId | None
    owned_sound_ids: tuple[SoundId, ...]
    presented_sound_ids: tuple[SoundId, ...]
    rule_occurrence_ids: tuple[OccurrenceId, ...]
    silence: Silence


@dataclass(frozen=True, slots=True)
class RulePlacement:
    rule_occurrence_id: OccurrenceId
    unit_ids: tuple[LetterUnitId, ...]


@dataclass(frozen=True, slots=True)
class MergerPlacement:
    merger_id: MergerId
    before_unit_ids: tuple[LetterUnitId, ...]
    after_unit_ids: tuple[LetterUnitId, ...]


@dataclass(frozen=True, slots=True)
class SourceView:
    """One request's exact source: its characters, the units over them, and the
    rule and merger placements on the visible units."""

    text: str
    characters: tuple[Character, ...]
    units: tuple[LetterUnit, ...]
    rule_placements: tuple[RulePlacement, ...]
    merger_placements: tuple[MergerPlacement, ...]


__all__ = [
    "Character",
    "CharacterKind",
    "LetterUnit",
    "LetterUnitKind",
    "LiteralSilence",
    "MergerPlacement",
    "RulePlacement",
    "Silence",
    "SourceView",
]
