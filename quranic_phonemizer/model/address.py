"""Addresses, identities and the request-scoped selections that key on them.

Every stable reference in the system is a `SlotId` (ADR-001 §5). Never a
`SoundId`, which is request-local; never a byte offset; never "the nth
occurrence of glyph X".
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Riwayah(StrEnum):
    """Closed. Supporting a riwayah needs code, fixtures and packaged data."""

    HAFS = "hafs"


class Script(StrEnum):
    """Closed per riwayah. Both members below are *Hafs* scripts."""

    UTHMANI = "uthmani"
    INDOPAK = "indopak"


@dataclass(frozen=True, slots=True, order=True)
class VerseRef:
    surah: int
    ayah: int

    def __str__(self) -> str:
        return f"{self.surah}:{self.ayah}"


@dataclass(frozen=True, slots=True, order=True)
class Location:
    """A word address. `word` is 1-based within the verse."""

    surah: int
    ayah: int
    word: int

    @property
    def verse(self) -> VerseRef:
        return VerseRef(self.surah, self.ayah)

    def __str__(self) -> str:
        return f"{self.surah}:{self.ayah}:{self.word}"


@dataclass(frozen=True, slots=True, order=True)
class SlotId:
    """A canonical position. The ordinal counts slots across the *verse*."""

    verse: VerseRef
    ordinal: int

    def __str__(self) -> str:
        return f"{self.verse}#{self.ordinal}"


@dataclass(frozen=True, slots=True, order=True)
class GraphemeId:
    """Position-ordered: `offset` is the codepoint index within the verse."""

    verse: VerseRef
    offset: int

    def __str__(self) -> str:
        return f"{self.verse}@{self.offset}"


@dataclass(frozen=True, slots=True, order=True)
class SoundId:
    """Request-local. Valid only inside the `Performance` that produced it."""

    verse: VerseRef
    seq: int

    def __str__(self) -> str:
        return f"{self.verse}~{self.seq}"


@dataclass(frozen=True, slots=True, order=True)
class OccurrenceId:
    verse: VerseRef
    seq: int

    def __str__(self) -> str:
        return f"{self.verse}!{self.seq}"


class Junction(StrEnum):
    """What happens after a word (ADR-004 §5)."""

    JOIN = "join"
    SAKT = "sakt"
    STOP = "stop"
    EDGE = "edge"


@dataclass(frozen=True, slots=True)
class BoundaryPlan:
    """One junction per word: the junction *after* it."""

    junctions: tuple[Junction, ...]

    def after(self, index: int) -> Junction:
        return self.junctions[index]

    def before(self, index: int) -> Junction | None:
        return self.junctions[index - 1] if index else None

    def started_on(self, index: int) -> bool:
        before = self.before(index)
        return before is None or before in (Junction.STOP, Junction.EDGE)

    def stopped_on(self, index: int) -> bool:
        return self.after(index) in (Junction.STOP, Junction.EDGE)


class KhilafId(StrEnum):
    """Named points of legitimate disagreement within one riwayah.

    Kind 1 (token choice) and kind 2 (per-location lexical) only; see
    ADR-006. The set grows with `variants.yaml`, never with code.
    """

    SEEN_SAD = "seen_sad"
    IQLAB_NASAL = "iqlab_nasal"
    IKHFAA_SHAFAWI_NASAL = "ikhfaa_shafawi_nasal"


@dataclass(frozen=True, slots=True)
class Option:
    """One legal reading of one khilāf point."""

    khilaf: KhilafId
    name: str


@dataclass(frozen=True, slots=True)
class VariantSelection:
    """Which option is taken at each khilāf point. Part of the Score's identity."""

    options: tuple[Option, ...] = ()

    def chosen(self, khilaf: KhilafId) -> str | None:
        for option in self.options:
            if option.khilaf is khilaf:
                return option.name
        return None
