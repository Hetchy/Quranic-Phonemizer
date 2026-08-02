from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

HEAVY = [
    ("2:29", 3, "xaˤlaqQ"),        # خَلَقَ
    ("11:11", 3, "sˤaˤbarˤu:"),    # صَبَرُوا۟
    ("30:28", 1, "dˤaˤrˤaˤbQ"),    # ضَرَبَ
    ("2:173", 24, "ɣaˤfu:rˤ"),     # غَفُورٌ
    ("16:108", 3, "tˤaˤbaʕ"),      # طَبَعَ
    ("2:33", 1, "qaˤ:l"),          # قَالَ
    ("2:231", 19, "ðˤaˤlam"),      # ظَلَمَ
]

LIGHT = [
    ("5:83", 2, "samiʕu:"),        # سَمِعُوا۟
    ("2:38", 10, "tabiʕ"),         # تَبِعَ
    ("3:38", 2, "daʕa:"),          # دَعَا
    ("2:17", 10, "ðahabQ"),        # ذَهَبَ
    ("2:97", 3, "ka:n"),           # كَانَ
]

ADDALLIN = Site(hafs=("1:7", (9,)))
DAKHALA = Site(hafs=("3:37", (11,)))
QUL = Site(hafs=("2:80", (8,)))
KHUDHU = Site(hafs=("2:63", (7,)))
GHUFRANAK = Site(hafs=("2:285", (24,)))
SUDURUHUM = Site(hafs=("3:118", (22,)))


@pytest.mark.parametrize(("ref", "word", "expected"), HEAVY)
def test_every_istilaa_letter_is_heavy(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@pytest.mark.parametrize(("ref", "word", "expected"), LIGHT)
def test_the_light_counterpart_letters_stay_light(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@for_each_riwayah(ADDALLIN, isolated=9)
def test_a_daad_is_heavy_and_carries_its_alif_with_it(r):
    # ٱلضَّآلِّينَ
    assert r.phonemes(9) == "ʔadˤdˤaˤ:lli:n"


@for_each_riwayah(DAKHALA, isolated=11)
def test_one_word_can_hold_a_light_dal_and_a_heavy_khaa(r):
    # دَخَلَ
    assert r.phonemes(11) == "daxaˤl"


@for_each_riwayah(QUL, isolated=8)
def test_a_heavy_qaf_over_a_damma_leaves_the_vowel_alone(r):
    # قُلْ
    assert r.phonemes(8) == "qul"


@for_each_riwayah(KHUDHU, isolated=7)
def test_a_khaa_over_a_damma_leaves_the_vowel_alone(r):
    # خُذُوا۟
    assert r.phonemes(7) == "xuðu:"


@for_each_riwayah(GHUFRANAK, isolated=24)
def test_a_ghayn_over_a_damma_leaves_its_own_vowel_alone(r):
    # غُفْرَانَكَ
    assert r.phonemes(24) == "ɣufrˤaˤ:nak"


@for_each_riwayah(SUDURUHUM, isolated=22)
def test_a_sad_over_a_damma_leaves_the_vowel_alone(r):
    # صُدُورُهُمْ
    assert r.phonemes(22) == "sˤudu:rˤuhum"
