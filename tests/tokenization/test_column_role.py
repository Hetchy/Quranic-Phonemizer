"""A letter unit reads as a consonant where it supplies a letter and as a
long-vowel carrier where it supplies length. The written scalar does not
decide which; the canonical fact does."""
from __future__ import annotations

import pytest

from quranic_phonemizer.phonemize import edges as ed

from .support import built, only, supplies

# The same waw, read as a consonant in one word and a carrier in another.
CONSONANT_WAW = ("2:255:5", "و")       # هُوَ
CARRIER_WAW = ("2:255:7", "و")         # ٱلْقَيُّومُ

# Letters read as consonants: a base and the mini noon.
LETTER_ROLE = (("2:255:5", "و"), ("21:88:7", "ۨ"))

# Letters read as carriers: full and small waw and yaa, and the dagger.
MADD_ROLE = (
    ("2:255:7", "و"), ("2:255:9", "ۥ"), ("2:22:13", "ۦ"), ("1:1:3", "ٰ"),
)


def test_the_same_waw_takes_a_different_role_by_its_canonical_fact():
    """Read the codepoint alone and both waws look identical; the fact splits
    the consonant from the carrier."""
    consonant = built(CONSONANT_WAW[0])
    carrier = built(CARRIER_WAW[0])
    cg = only(consonant, char=CONSONANT_WAW[1], word=0)
    kg = only(carrier, char=CARRIER_WAW[1], word=0)
    assert consonant.glyphs[cg].char == carrier.glyphs[kg].char
    assert ed.Fact.LETTER in supplies(consonant, cg)
    assert ed.Fact.VOWEL_LENGTH in supplies(carrier, kg)
    assert ed.Fact.VOWEL_LENGTH not in supplies(consonant, cg)
    assert ed.Fact.LETTER not in supplies(carrier, kg)


@pytest.mark.parametrize(("ref", "char"), LETTER_ROLE)
def test_a_consonant_letter_supplies_its_letter(ref, char):
    # و ۨ
    a = built(ref)
    glyph = only(a, char=char, word=0)
    assert ed.Fact.LETTER in supplies(a, glyph)
    assert ed.Fact.VOWEL_LENGTH not in supplies(a, glyph)


@pytest.mark.parametrize(("ref", "char"), MADD_ROLE)
def test_a_carrier_letter_supplies_the_vowel_length(ref, char):
    # و ۥ ۦ ٰ
    a = built(ref)
    glyph = only(a, char=char, word=0)
    assert ed.Fact.VOWEL_LENGTH in supplies(a, glyph)
    assert ed.Fact.LETTER not in supplies(a, glyph)
