"""Letters open their own units: base letters, and the ones the rasm leaves
out and writes small, alike."""
from __future__ import annotations

import pytest

from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd

from .support import built, find, opens_unit, only, supplies, units_named

# A base letter and, in the same word, a shadda that folds onto it.
TUURI = "52:1:1"

# Letters the rasm drops and writes small, each in a word that holds one.
COMBINING_HAMZA = ("2:31:10", "ٔ")
SMALL_WAW = ("2:255:9", "ۥ")
SMALL_YA = ("2:22:13", "ۦ")
MINI_NOON = ("21:88:7", "ۨ")

# A dagger alif the rasm leaves out, lengthening the vowel before it.
DAGGER = ("1:1:3", "ٰ")


def test_a_base_letter_supplies_its_letter_and_opens_a_unit():
    # وَٱلطُّورِ
    a = built(TUURI)
    taa = only(a, char="ط", word=0)
    assert ed.Fact.LETTER in supplies(a, taa)
    assert opens_unit(a, taa)


def test_a_base_letters_shadda_folds_where_the_letter_opens():
    """The discriminating half: the shadda on the same letter states ONSET,
    supplies no opening fact, and mints no unit of its own."""
    # وَٱلطُّورِ
    a = built(TUURI)
    taa = only(a, char="ط", word=0)
    shadda = only(a, char="ّ", word=0)
    assert not opens_unit(a, shadda)
    assert units_named(a, shadda) == units_named(a, taa)


@pytest.mark.parametrize(
    ("ref", "char"), (COMBINING_HAMZA, SMALL_WAW, SMALL_YA, MINI_NOON)
)
def test_an_omitted_small_letter_opens_its_own_unit(ref, char):
    # ٔ ۥ ۦ ۨ
    a = built(ref)
    glyph = only(a, char=char, word=0)
    assert a.glyphs[glyph].kind is nd.GlyphKind.BASE
    # A letter or its length, never the empty fact set a folding mark states.
    assert opens_unit(a, glyph)
    assert supplies(a, glyph) & {ed.Fact.LETTER, ed.Fact.VOWEL_LENGTH}


def test_the_mini_noon_is_a_letter_not_a_mark():
    """It supplies a consonant identity, the same fact a full noon states."""
    # نُـۨجِى
    a = built(MINI_NOON[0])
    mini = only(a, char=MINI_NOON[1], word=0)
    plain = only(a, char="ن", word=0)
    assert supplies(a, mini) == supplies(a, plain) == frozenset({ed.Fact.LETTER})


def test_a_dagger_alif_opens_a_unit_the_rasm_left_out():
    # ٱلرَّحْمَـٰنِ
    a = built(DAGGER[0])
    dagger = only(a, char=DAGGER[1], word=0)
    assert opens_unit(a, dagger)
    # It carries the length, the fact a written alif would carry in its place.
    assert supplies(a, dagger) == frozenset({ed.Fact.VOWEL_LENGTH})


def test_no_dagger_alif_stands_as_a_consonant_of_its_own():
    """Whether the dagger lengthens or stands is canonical; in this reading
    every dagger lengthens, so none supplies a letter."""
    for ref in ("1:1:3", "2:255:3", "20:5:1"):
        a = built(ref)
        for glyph in find(a, char="ٰ"):
            assert ed.Fact.LETTER not in supplies(a, glyph)
