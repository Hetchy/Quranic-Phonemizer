"""The Inscription layer: what a script wrote, and what each mark is doing.

`Spelling` points *up* from a grapheme into the Score; nothing points
down at a grapheme.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from .address import (
    GraphemeId,
    Location,
    Script,
    SlotId,
    SourceGraphemeRef,
    VerseRef,
)


class GraphemeClass(StrEnum):
    """What the grapheme *is*. `Spelling` says what it *does*; the two axes
    are independent and a projection's `role` reads the second."""

    BASE = "base"
    HARAKA = "haraka"
    TANWEEN = "tanween"
    SHADDA = "shadda"
    LENGTH_CARRIER = "length_carrier"
    """No script yaml assigns this; it is for a grapheme the recited-text
    writer mints, not one any inventory reads."""
    SMALL_VOWEL = "small_vowel"
    MADD_SIGN = "madd_sign"
    SILENCE_SIGN = "silence_sign"
    ANNOTATION = "annotation"
    ADVICE = "advice"
    STRUCTURAL = "structural"


@dataclass(frozen=True, slots=True)
class Grapheme:
    id: GraphemeId
    char: str
    cls: GraphemeClass
    index: int
    """Ordinal within its word. The frozen baseline's `source_letter_index`."""
    source: SourceGraphemeRef | None = None
    """Exact external-source identity when public and source refs differ."""


class SlotFact(StrEnum):
    LETTER = "letter"
    ONSET = "onset"
    VOWEL_QUALITY = "vowel_quality"
    VOWEL_LENGTH = "vowel_length"
    VOWEL_ABSENCE = "vowel_absence"
    SAKT = "sakt"
    TAJWEED_MARK = "tajweed_mark"


#: A haraka and its carrier can each name one of these for the same slot, so
#: a lookup spanning the whole vowel needs the union rather than one member.
VOWEL_FACTS = frozenset({SlotFact.VOWEL_QUALITY, SlotFact.VOWEL_LENGTH,
                          SlotFact.VOWEL_ABSENCE})


@dataclass(frozen=True, slots=True)
class Evidences:
    """This grapheme supplies or asserts a canonical fact of a named slot."""

    grapheme: GraphemeId
    slot: SlotId
    fact: SlotFact


@dataclass(frozen=True, slots=True)
class Attests:
    """This grapheme witnesses a *performance* outcome at an anchor slot,
    naming no rule: choosing among idgham members is tajweed classification,
    not a script adapter's job.
    """

    grapheme: GraphemeId
    anchor: SlotId


@dataclass(frozen=True, slots=True)
class Decorates:
    """Supplies no canonical fact, but is bound to the slot it shows.

    The slot is mandatory: unlike `Structural`, a `Decorates` grapheme is
    tied to a slot even though it asserts nothing about it.
    """

    grapheme: GraphemeId
    slot: SlotId


@dataclass(frozen=True, slots=True)
class Structural:
    """Not part of any word: space, sajdah, hizb, verse marker, tatweel, and
    the stop-sign scalars, which reach `StopAdvice` through the inventory."""

    grapheme: GraphemeId


Spelling: TypeAlias = Evidences | Attests | Decorates | Structural


class SilenceReason(StrEnum):
    """Why a written letter is said by nobody where no tajweed rule decided
    it: the rasm keeps a letter the reading never says, or a variant leaves
    an optional one off. Either way the spelling is the whole of it."""

    ORTHOGRAPHIC = "orthographic_silence"
    VARIANT = "_variant_omission"


class StopAdvice(StrEnum):
    """A mushaf convention, legitimately script-scoped. The *class* vocabulary
    is shared; the mapping from scalars into it is per (riwayah, script)."""

    PREFERRED_CONTINUE = "preferred_continue"
    PREFERRED_STOP = "preferred_stop"
    OPTIONAL_STOP = "optional_stop"
    COMPULSORY_STOP = "compulsory_stop"
    PROHIBITED_STOP = "prohibited_stop"
    EITHER_STOP = "either_stop"
    PERMITTED_STOP = "permitted_stop"
    """A stop is allowed, class unspecified. IndoPak's `ؕ` absorbs three
    Uthmani classes; mapping it to any one would invent a distinction the
    source does not make."""


@dataclass(frozen=True, slots=True)
class Inscription:
    """One verse as one script wrote it."""

    verse: VerseRef
    script: Script
    words: tuple[Location, ...]
    graphemes: tuple[Grapheme, ...]
    spellings: tuple[Spelling, ...]
    advice: tuple[StopAdvice | None, ...]
    """One per word, in `words` order."""


class GlyphKind(StrEnum):
    """A projection's `kind` vocabulary, finer than `GraphemeClass`: it
    splits a sukun from a haraka and a tatweel seat from a structural
    scalar."""

    BASE = "base"
    HARAKA = "haraka"
    TANWEEN = "tanween"
    SHADDA = "shadda"
    VOWEL_LETTER = "vowel_letter"
    SMALL_VOWEL = "small_vowel"
    MADD_SIGN = "madd_sign"
    SUKUN = "sukun"
    SILENCE_SIGN = "silence_sign"
    TAJWEED_MARK = "tajweed_mark"
    STOP_SIGN = "stop_sign"
    TATWEEL = "tatweel"
    STRUCTURAL = "structural"


#: `GraphemeClass` members with one `GlyphKind` regardless of what they
#: evidence. `HARAKA` is absent: a sukun and an ordinary haraka share the
#: class and split only on the vowel-absent flag.
_KIND_OF_CLASS = {
    GraphemeClass.BASE: GlyphKind.BASE,
    GraphemeClass.TANWEEN: GlyphKind.TANWEEN,
    GraphemeClass.SHADDA: GlyphKind.SHADDA,
    GraphemeClass.SMALL_VOWEL: GlyphKind.SMALL_VOWEL,
    GraphemeClass.MADD_SIGN: GlyphKind.MADD_SIGN,
    GraphemeClass.SILENCE_SIGN: GlyphKind.SILENCE_SIGN,
    GraphemeClass.ANNOTATION: GlyphKind.TAJWEED_MARK,
    GraphemeClass.ADVICE: GlyphKind.STOP_SIGN,
    GraphemeClass.STRUCTURAL: GlyphKind.STRUCTURAL,
    GraphemeClass.LENGTH_CARRIER: GlyphKind.VOWEL_LETTER,
}


def glyph_kind_of(
    cls: GraphemeClass, *, vowel_absent: bool = False, structural: bool = True
) -> GlyphKind:
    """`vowel_absent` is the vowel-absence fact evidenced at this grapheme.
    `structural` says it carries the structural edge; one of that class
    without the edge is a seat a mark was written on, inside a word."""
    if cls is GraphemeClass.HARAKA:
        return GlyphKind.SUKUN if vowel_absent else GlyphKind.HARAKA
    if cls is GraphemeClass.STRUCTURAL and not structural:
        return GlyphKind.TATWEEL
    return _KIND_OF_CLASS[cls]


@dataclass(frozen=True, slots=True)
class Glyph:
    """One source scalar. `word`/`word_index` are absent for a structural
    glyph, which belongs to no word."""

    word: int | None
    char: str
    kind: GlyphKind
    word_index: int | None
    source_index: int
