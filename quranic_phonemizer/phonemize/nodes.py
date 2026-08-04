"""The six public node arrays of 01-contract section 4.

Each node is a plain record over an index space `assemble.py` assigns.
Model enums are reused directly where the value space already matches.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..model.address import Location
from ..model.canon import CanonLetter, Nucleus, Onset, Quality, Rule, SlotOrigin
from ..model.inscription import GraphemeClass, StopAdvice
from ..model.performance import Degree


class ConsonantSounds(StrEnum):
    """Whether a unit's consonant is there at all."""

    ALWAYS = "always"
    WHEN_STARTED_ON = "when_started_on"
    WHEN_JOINED = "when_joined"


#: `Onset.PLAIN`, `GEMINATE` and `TASHIL` all sound unconditionally; only
#: `WASL` and `GLIDE` are boundary-conditional, and are exact mirrors.
_SOUNDS_OF_ONSET = {
    Onset.WASL: ConsonantSounds.WHEN_STARTED_ON,
    Onset.GLIDE: ConsonantSounds.WHEN_JOINED,
}


class UnitOrigin(StrEnum):
    WRITTEN = "written"
    MUQATTAAT = "muqattaat"
    TANWEEN = "tanween"


_ORIGIN_OF_SLOT_ORIGIN = {
    SlotOrigin.WRITTEN: UnitOrigin.WRITTEN,
    SlotOrigin.SPELLED: UnitOrigin.MUQATTAAT,
    SlotOrigin.NUNATION: UnitOrigin.TANWEEN,
}


@dataclass(frozen=True, slots=True)
class ConsonantFact:
    geminate: bool
    sounds: ConsonantSounds


@dataclass(frozen=True, slots=True)
class Unit:
    """One letter with the vowel state that follows it -- 01-contract 4.2."""

    word: int
    letter: CanonLetter
    consonant: ConsonantFact
    vowel: Nucleus
    origin: UnitOrigin


def unit_of(word_index: int, slot) -> Unit:
    return Unit(
        word=word_index,
        letter=slot.letter,
        consonant=ConsonantFact(
            geminate=slot.onset is Onset.GEMINATE,
            sounds=_SOUNDS_OF_ONSET.get(slot.onset, ConsonantSounds.ALWAYS),
        ),
        vowel=slot.nucleus,
        origin=_ORIGIN_OF_SLOT_ORIGIN[slot.origin],
    )


@dataclass(frozen=True, slots=True)
class Word:
    location: Location
    text: str
    is_started_on: bool
    is_stopped_on: bool
    sakt_after: bool
    stop_sign: StopAdvice | None


class SoundKind(StrEnum):
    CONSONANT = "consonant"
    VOWEL = "vowel"
    QALQALA = "qalqala"


@dataclass(frozen=True, slots=True)
class Sound:
    """`kind` decides which of the fields below are meaningful -- 01-contract
    4.4."""

    token: str
    kind: SoundKind
    letter: CanonLetter | None = None
    geminate: bool | None = None
    emphatic: bool | None = None
    ghunnah: bool | None = None
    eased: bool | None = None
    quality: Quality | None = None
    long: bool | None = None
    degree: Degree | None = None


@dataclass(frozen=True, slots=True)
class RuleInstance:
    rule: Rule
    source: int | None
    host: int | None
    labels: tuple[str, ...] = ()
    """Populated once `phonemize/labels.py` exists; empty is not yet derived."""


class GlyphKind(StrEnum):
    """01-contract 4.3's own `kind` vocabulary -- distinct from the model's
    `GraphemeClass`, which folds a sukun into `haraka`, has no
    `vowel_letter`, and calls a tajweed mark `annotation`."""

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
    STRUCTURAL = "structural"


#: `GraphemeClass` members with a single `GlyphKind` regardless of what fact
#: the grapheme evidences. `HARAKA` is not here: a sukun and an ordinary
#: haraka share a `GraphemeClass` and split only on `SlotFact.VOWEL_ABSENCE`
#: -- `glyph_kind_of` below reads that separately.
_KIND_OF_GRAPHEME_CLASS = {
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


def glyph_kind_of(cls: GraphemeClass, *, vowel_absent: bool = False) -> GlyphKind:
    """`vowel_absent` is `SlotFact.VOWEL_ABSENCE` evidenced at this
    grapheme -- the one fact `GraphemeClass.HARAKA` does not already say."""
    if cls is GraphemeClass.HARAKA:
        return GlyphKind.SUKUN if vowel_absent else GlyphKind.HARAKA
    return _KIND_OF_GRAPHEME_CLASS[cls]


@dataclass(frozen=True, slots=True)
class Glyph:
    """One source scalar -- 01-contract 4.3. `word`/`word_index` are absent
    for a glyph carrying the `Structural` spelling edge."""

    word: int | None
    char: str
    kind: GlyphKind
    word_index: int | None
    source_index: int


@dataclass(frozen=True, slots=True)
class RenderGlyph(Glyph):
    """`from_glyphs` names the source `Glyph` indices it renders; empty is an
    insertion, more than one is a merge."""

    from_glyphs: tuple[int, ...] = ()


__all__ = [
    "ConsonantFact",
    "ConsonantSounds",
    "Glyph",
    "GlyphKind",
    "RenderGlyph",
    "RuleInstance",
    "Sound",
    "SoundKind",
    "Unit",
    "UnitOrigin",
    "Word",
    "glyph_kind_of",
    "unit_of",
]
