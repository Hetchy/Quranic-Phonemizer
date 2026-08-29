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
    WARSH = "warsh"


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
    """Closed script styles; each riwayah packages only the styles it owns."""

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
class SourceLocation:
    """A word address in one pinned source artifact, never a public ref."""

    artifact: str
    surah: int
    ayah: int
    word: int

    def __str__(self) -> str:
        return f"{self.artifact}:{self.surah}:{self.ayah}:{self.word}"


@dataclass(frozen=True, slots=True, order=True)
class SourceGraphemeRef:
    """One scalar's offset inside its exact selected-source word."""

    location: SourceLocation
    offset: int


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
class SpellingRunId:
    """A named-letter run within one Quran word."""

    location: Location
    ordinal: int

    def __str__(self) -> str:
        return f"{self.location}~{self.ordinal}"


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


class KhilafId(str):
    """One ASCII selector ID declared by a riwayah's khilaf catalogue."""

    def __new__(cls, value: str):
        if not isinstance(value, str) or not value or any(
            not (char.isascii() and (char.islower() or char.isdigit() or char == "_"))
            for char in value
        ):
            raise ValueError(f"invalid variant ID {value!r}")
        return super().__new__(cls, value)

    @property
    def value(self) -> str:
        return str(self)


KhilafId.YABSUT = KhilafId("yabsut")
KhilafId.BASTAH = KhilafId("bastah")
KhilafId.ALMUSAYTIRUN = KhilafId("almusaytirun")
KhilafId.BIMUSAYTIR = KhilafId("bimusaytir")
KhilafId.IQLAB_NASAL = KhilafId("iqlab_nasal")
KhilafId.IKHFAA_SHAFAWI_NASAL = KhilafId("ikhfaa_shafawi_nasal")
KhilafId.RAA_FIRQ = KhilafId("raa_firq")
KhilafId.RAA_ALQITR_WAQF = KhilafId("raa_alqitr_waqf")
KhilafId.RAA_MISR_WAQF = KhilafId("raa_misr_waqf")
KhilafId.RAA_WANUTHUR_WAQF = KhilafId("raa_wanuthur_waqf")
KhilafId.RAA_YASR_WAQF = KhilafId("raa_yasr_waqf")
KhilafId.RAA_ASR_WAQF = KhilafId("raa_asr_waqf")
KhilafId.DAAF_HARAKA = KhilafId("daaf_haraka")
KhilafId.YAA_AATANI_WAQF = KhilafId("yaa_aatani_waqf")
KhilafId.NOON_WASL = KhilafId("noon_wasl")
KhilafId.YASEEN_WASL = KhilafId("yaseen_wasl")
KhilafId.ISTIFHAM_ARTICLE = KhilafId("istifham_article")
KhilafId.TAMANNA_NOON = KhilafId("tamanna_noon")
KhilafId.MALIYAH_HALAK = KhilafId("maliyah_halak")
KhilafId.SALASILA_WAQF = KhilafId("salasila_waqf")
KhilafId.ALISM_IBTIDAA = KhilafId("alism_ibtidaa")
KhilafId.IRKAB_MAANA = KhilafId("irkab_maana")
KhilafId.YALHATH_DHALIK = KhilafId("yalhath_dhalik")
KhilafId.IWAJA_QAYYIMA = KhilafId("iwaja_qayyima")
KhilafId.MAN_RAQ = KhilafId("man_raq")
KhilafId.BAL_RAN = KhilafId("bal_ran")


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
        found = [option.name for option in self.options if option.khilaf == khilaf]
        if len(found) > 1:
            raise ValueError(f"{khilaf.value}: more than one option was selected")
        return found[0] if found else None
