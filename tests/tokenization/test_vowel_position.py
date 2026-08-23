"""Haraka, sukun and tanween each hold the vowel position, so each is a unit.
A sukun denotes an absent vowel; it is not a silent letter."""
from __future__ import annotations

from quranic_phonemizer.phonemize import edges as ed

from .support import built, find, only, opens_unit, supplies

BISMI = "1:1:1"          # a sukun on the siin
MAA = "2:255:14"         # a single fatha
SANATUN = "2:255:10"     # a tanween on the taa marbuta
KAFARU = "2:6:3"         # a silent alif the reading writes and never says


def test_a_haraka_occupies_the_vowel_position():
    # مَا
    a = built(MAA)
    haraka = only(a, char="َ", word=0)
    assert supplies(a, haraka) == frozenset({ed.Fact.VOWEL_QUALITY})
    assert opens_unit(a, haraka)


def test_a_sukun_occupies_the_vowel_position():
    # بِسْمِ
    a = built(BISMI)
    sukun = only(a, char="ْ", word=0)
    assert supplies(a, sukun) == frozenset({ed.Fact.VOWEL_ABSENCE})
    assert opens_unit(a, sukun)


def test_a_tanween_holds_the_vowel_and_mints_its_nunation():
    """One scalar states the vowel and, on a fresh unit, the noon it adds."""
    # سَنَةٌ
    a = built(SANATUN)
    tanween = only(a, char="ٌ", word=0)
    assert supplies(a, tanween) == frozenset({
        ed.Fact.VOWEL_QUALITY, ed.Fact.LETTER, ed.Fact.VOWEL_ABSENCE
    })


def test_a_sukun_has_no_silence_reason_where_a_silent_letter_does():
    """The distinguishing pair. The silent alif carries an orthographic
    silence; the sukun beside it carries none, owning no sound to lose."""
    a = built(KAFARU)
    silent_alif = only(a, char="ا", word=0)
    assert silent_alif in a.orthographic_silence

    sukun = built(BISMI)
    for glyph in find(sukun, char="ْ"):
        assert glyph not in sukun.orthographic_silence
