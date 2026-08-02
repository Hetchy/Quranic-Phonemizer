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
    ("1:6", 2, "ʔasˤsˤirˤaˤ:tˤQ"),    # ٱلصِّرَٰطَ
    ("2:16", 4, "ʔadˤdˤaˤla:lah"),    # ٱلضَّلَـٰلَةَ
    ("2:63", 6, "ʔatˤtˤu:rˤ"),        # ٱلطُّورَ
    ("2:35", 18, "ʔaðˤðˤaˤ:limi:n"),  # ٱلظَّـٰلِمِينَ
    ("2:164", 7, "ʔallajl"),          # ٱلَّيْلِ
    ("2:24", 7, "ʔaña:rˤ"),           # ٱلنَّارَ
]


@pytest.mark.parametrize(("ref", "word", "expected"), SUN_LETTERS)
def test_the_article_lam_merges_into_each_sun_letter(ref, word, expected):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == expected


@for_each_riwayah(ARRAHMAN, ibtidaa=2, waqf=3)
def test_the_merged_lam_writes_nothing_when_the_word_before_joins(r):
    # ٱللَّهِ ٱلرَّحْمَـٰنِ
    assert r.phonemes(2) == "ʔalˤlˤaˤ:hi"
    assert r.phonemes(3) == "rˤrˤaˤħma:n"
    assert r.silent(3) == {"ِ", "ٱ"}
