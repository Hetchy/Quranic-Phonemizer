"""Addresses, identities and the request-scoped selections that key on them.

Every stable reference is a `SlotId`, never a `SoundId` (request-local),
a byte offset, or "the nth occurrence of glyph X".
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Riwayah(StrEnum):
    """Closed. Supporting a riwayah needs code, fixtures and packaged data."""

    HAFS = "hafs"


class UnknownRiwayah(ValueError):
    """Named rather than a bare KeyError, so the message lists what ships."""


def check_riwayah(riwayah: str) -> Riwayah:
    """The membership gate: `Riwayah` is closed, so a member is shipped."""
    try:
        return Riwayah(riwayah)
    except ValueError:
        raise UnknownRiwayah(
            f"{riwayah!r} is not a riwayah; this build ships "
            f"{[r.value for r in Riwayah]}"
        ) from None


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

    def __hash__(self) -> int:
        return self.verse.surah << 48 | self.verse.ayah << 32 | self.ordinal


@dataclass(frozen=True, slots=True, order=True)
class GraphemeId:
    """Position-ordered: `offset` is the codepoint index within the verse."""

    verse: VerseRef
    offset: int

    def __str__(self) -> str:
        return f"{self.verse}@{self.offset}"

    def __hash__(self) -> int:
        return self.verse.surah << 48 | self.verse.ayah << 32 | self.offset


@dataclass(frozen=True, slots=True, order=True)
class SoundId:
    """Request-local. Valid only inside the `Performance` that produced it."""

    verse: VerseRef
    seq: int

    def __str__(self) -> str:
        return f"{self.verse}~{self.seq}"

    def __hash__(self) -> int:
        return self.verse.surah << 48 | self.verse.ayah << 32 | self.seq


@dataclass(frozen=True, slots=True, order=True)
class OccurrenceId:
    verse: VerseRef
    seq: int

    def __str__(self) -> str:
        return f"{self.verse}!{self.seq}"

    def __hash__(self) -> int:
        return self.verse.surah << 48 | self.verse.ayah << 32 | self.seq


class Junction(StrEnum):
    """What happens after a word."""

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
    """Named points of legitimate disagreement within one riwayah: token
    choice or per-location lexical only. Grows with `variants.yaml`, not code.
    """

    SEEN_SAD_YABSUT = "seen_sad_yabsut"
    SEEN_SAD_BASTAH = "seen_sad_bastah"
    SEEN_SAD_AL_MUSAYTIRUN = "seen_sad_al_musaytirun"
    SEEN_SAD_BIMUSAYTIR = "seen_sad_bimusaytir"
    IQLAB_NASAL = "iqlab_nasal"
    IKHFAA_SHAFAWI_NASAL = "ikhfaa_shafawi_nasal"
    RAA_FIRQ_WASL = "raa_firq_wasl"
    RAA_ALQITR_WAQF = "raa_alqitr_waqf"
    RAA_MISR_WAQF = "raa_misr_waqf"
    RAA_NUTHUR_WAQF = "raa_nuthur_waqf"
    RAA_YASR_WAQF = "raa_yasr_waqf"
    RAA_ASR_WAQF = "raa_asr_waqf"
    DAAF_HARAKA = "daaf_haraka"
    YAA_AATANI_WAQF = "yaa_aatani_waqf"
    NOON_YASEEN_WASL = "noon_yaseen_wasl"
    MADD_LAZIM_TASHEEL = "madd_lazim_tasheel"


@dataclass(frozen=True, slots=True)
class Option:
    """One legal reading of one khilaf point."""

    khilaf: KhilafId
    name: str


@dataclass(frozen=True, slots=True)
class VariantSelection:
    """Which option is taken at each khilaf point. Part of the Score's identity."""

    options: tuple[Option, ...] = ()

    def chosen(self, khilaf: KhilafId) -> str | None:
        """Return the one scalar choice made for a khilaf point."""
        found = [option.name for option in self.options if option.khilaf is khilaf]
        if len(found) > 1:
            raise ValueError(f"{khilaf.value}: more than one option was selected")
        return found[0] if found else None
