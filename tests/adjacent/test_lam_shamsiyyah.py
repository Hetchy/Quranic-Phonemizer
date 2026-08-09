from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

ARRAHMAN = Site(hafs=("1:1", (2, 3)))

SUN_LETTERS = [
    ("2:37", 10, "ʔattawwa:bQ"),      # ٱلتَّوَّابُ
    ("2:22", 15, "ʔaθθamarˤaˤ:t"),    # ٱلثَّمَرَٰتِ
    ("1:4", 3, "ʔaddi:n"),            # ٱلدِّينِ
    ("3:14", 11, "ʔaððahabQ"),        # ٱلذَّهَبِ
    ("1:1", 4, "ʔarˤrˤaˤħi:m"),       # ٱلرَّحِيمِ
    ("2:197", 25, "ʔazza:dQ"),        # ٱلزَّادِ
    ("2:19", 4, "ʔassama:ʔ"),         # ٱلسَّمَآءِ
    ("2:35", 15, "ʔaʃʃaʒarˤaˤh"),     # ٱلشَّجَرَةَ
    ("2:25", 5, "ʔasˤsˤaˤ:liħa:t"),   # ٱلصَّـٰلِحَـٰتِ
    ("2:16", 4, "ʔadˤdˤaˤla:lah"),    # ٱلضَّلَـٰلَةَ
    ("2:63", 6, "ʔatˤtˤu:rˤ"),        # ٱلطُّورَ
    ("2:35", 18, "ʔaðˤðˤaˤ:limi:n"),  # ٱلظَّـٰلِمِينَ
    ("2:24", 7, "ʔaña:rˤ"),           # ٱلنَّارَ
]


@pytest.mark.parametrize(("ref", "word", "expected"), SUN_LETTERS)
def test_the_article_lam_merges_into_each_sun_letter(ref, word, expected):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == expected
    assert "lam_shamsiyyah" in r.rules_on_char(word, "ل")
    # the prosthetic hamza and its fatha come first, then the doubled letter
    merged = r.sounds(word)[2]
    assert "lam_shamsiyyah" in r.rules_on_sound(word, merged)


LAYL = Site(hafs=("2:164", (7,)))


@for_each_riwayah(LAYL, isolated=7)
def test_the_rasm_writes_one_lam_where_the_article_meets_a_lam(r):
    """ٱلَّيْلِ. Both scripts draw the article's lam and the sun lam as one
    lam under a shadda, so there is none to merge and none to colour: the
    doubling is canonical and no rule names it. ٱللَّغْوِ draws both."""
    assert r.phonemes(7) == "ʔallajl"
    assert r.rules_on_char(7, "ل") == {"pausal_sukun"}
    assert r.rules_on_sound(7, "ll") == frozenset()


@for_each_riwayah(ARRAHMAN, ibtidaa=2, waqf=3)
def test_the_merged_lam_writes_nothing_when_the_word_before_joins(r):
    # ٱللَّهِ ٱلرَّحْمَـٰنِ
    assert r.phonemes(2) == "ʔalˤlˤaˤ:hi"
    assert r.phonemes(3) == "rˤrˤaˤħma:n"
    assert r.silent(3) == {"ِ", "ٱ"}
    assert "lam_shamsiyyah" in r.rules_on_char(3, "ل")
    assert "lam_shamsiyyah" in r.rules_on_sound(3, "rˤrˤ")
