"""The nine public edge types.

Every field is an index into `assemble.Assembled`'s node arrays, never a
model-layer id: an edge here outlives the `Session` that produced it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from ..model.performance import Length


class Fact(StrEnum):
    """What a spelling glyph supplies. Sakt has no member: nothing
    evidences it."""

    LETTER = "letter"
    CONSONANT = "consonant"
    VOWEL_QUALITY = "vowel_quality"
    VOWEL_LENGTH = "vowel_length"
    VOWEL_ABSENCE = "vowel_absence"
    TAJWEED_MARK = "tajweed_mark"


@dataclass(frozen=True, slots=True)
class Supplies:
    glyph: int
    unit: int
    fact: Fact


@dataclass(frozen=True, slots=True)
class Witnesses:
    glyph: int
    unit: int


@dataclass(frozen=True, slots=True)
class Decorates:
    glyph: int
    unit: int


@dataclass(frozen=True, slots=True)
class Structural:
    glyph: int


SpellingEdge: TypeAlias = Supplies | Witnesses | Decorates | Structural


class Part(StrEnum):
    CONSONANT = "consonant"
    VOWEL = "vowel"


@dataclass(frozen=True, slots=True)
class Hosts:
    unit: int
    part: Part
    sound: int
    by: int | None


@dataclass(frozen=True, slots=True)
class MergedInto:
    unit: int
    part: Part
    sound: int
    by: int | None


@dataclass(frozen=True, slots=True)
class Silent:
    unit: int
    part: Part
    by: int | None


AttributionEdge: TypeAlias = Hosts | MergedInto | Silent


@dataclass(frozen=True, slots=True)
class Recolours:
    sound: int
    by: int


@dataclass(frozen=True, slots=True)
class SetsLength:
    sound: int
    by: int
    length: Length


@dataclass(frozen=True, slots=True)
class Classifies:
    sound: int
    by: int


ModifierEdge: TypeAlias = Recolours | SetsLength | Classifies


__all__ = [
    "AttributionEdge",
    "Classifies",
    "Decorates",
    "Fact",
    "Hosts",
    "MergedInto",
    "ModifierEdge",
    "Part",
    "Recolours",
    "SetsLength",
    "Silent",
    "SpellingEdge",
    "Structural",
    "Supplies",
    "Witnesses",
]
