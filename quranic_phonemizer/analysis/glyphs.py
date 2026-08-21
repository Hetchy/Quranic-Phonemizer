"""The native glyph kind vocabulary and the source glyph record.

`GlyphKind` is finer than the model's `GraphemeClass`: it splits a sukun from
a haraka and a tatweel seat from a structural scalar.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..model.inscription import GraphemeClass


class GlyphKind(StrEnum):
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


__all__ = ["Glyph", "GlyphKind", "glyph_kind_of"]
