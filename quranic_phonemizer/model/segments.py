from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from .orthography import Letter, VowelQuality


@dataclass(frozen=True, slots=True)
class Consonant:
    letter: Letter
    geminated: bool = False
    emphatic: bool = False
    nasalized: bool = False


@dataclass(frozen=True, slots=True)
class Vowel:
    quality: VowelQuality
    long: bool = False
    emphatic: bool = False


@dataclass(frozen=True, slots=True)
class Nasal:
    emphatic: bool = False


class Release(StrEnum):
    QALQALA = "qalqala"


Segment: TypeAlias = Consonant | Vowel | Nasal | Release
