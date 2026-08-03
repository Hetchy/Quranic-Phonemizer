from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

ALHAMDU = Site(hafs=("1:2", (1, 2)))

MOON_LETTERS = [
    ("2:11", 7, "ʔalʔarˤdˤ"),         # ٱلْأَرْضِ
    ("2:50", 4, "ʔalbaħrˤ"),          # ٱلْبَحْرَ
    ("2:35", 6, "ʔalʒañah"),          # ٱلْجَنَّةَ
    ("2:32", 12, "ʔalħaki:m"),        # ٱلْحَكِيمُ
    ("2:27", 20, "ʔalxaˤ:sirˤu:n"),   # ٱلْخَـٰسِرُونَ
    ("1:2", 4, "ʔalʕa:lami:n"),       # ٱلْعَـٰلَمِينَ
    ("2:57", 3, "ʔalɣaˤma:m"),        # ٱلْغَمَامَ
    ("2:105", 24, "ʔalfadˤl"),        # ٱلْفَضْلِ
    ("2:58", 5, "ʔalqaˤrˤjah"),       # ٱلْقَرْيَةَ
    ("2:34", 13, "ʔalka:firi:n"),     # ٱلْكَـٰفِرِينَ
    ("1:6", 3, "ʔalmustaqi:m"),       # ٱلْمُسْتَقِيمَ
    ("2:185", 11, "ʔalhuda:"),        # ٱلْهُدَىٰ
    ("2:233", 31, "ʔalwa:riθ"),       # ٱلْوَارِثِ
    ("2:113", 2, "ʔaljahu:dQ"),       # ٱلْيَهُودُ
]


@pytest.mark.parametrize(("ref", "word", "expected"), MOON_LETTERS)
def test_the_article_lam_is_said_before_each_moon_letter(ref, word, expected):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == expected


@for_each_riwayah(ALHAMDU, ibtidaa=1, waqf=2)
def test_the_said_lam_stays_when_the_word_is_joined_forward(r):
    # ٱلْحَمْدُ لِلَّهِ
    assert r.phonemes(1) == "ʔalħamdu"
    assert r.phonemes(2) == "lilla:h"
