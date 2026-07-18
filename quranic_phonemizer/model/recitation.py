from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .segments import Segment
from .orthography import Location, SourceWord


class Riwayah(StrEnum):
    HAFS = "hafs"
    WARSH = "warsh"


class BoundaryMode(StrEnum):
    JOIN = "join"
    STOP = "stop"
    EDGE = "edge"


@dataclass(frozen=True, slots=True)
class WordRealization:
    source: SourceWord
    segments: tuple[Segment, ...]
    phonemes: tuple[str, ...]
    boundary_after: BoundaryMode

    @property
    def location(self) -> Location:
        return self.source.location


@dataclass(frozen=True, slots=True)
class Recitation:
    riwayah: Riwayah
    ref: str
    stop_signs: tuple[str, ...]
    stop_refs: tuple[str, ...]
    words: tuple[WordRealization, ...]
