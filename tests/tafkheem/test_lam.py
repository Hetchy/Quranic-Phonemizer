from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

QALA_ALLAHU = Site(hafs=("5:119", (1, 2)))
NASRU_ALLAHI = Site(hafs=("110:1", (3, 4)))
BISMI_ALLAHI = Site(hafs=("1:1", (1, 2)))
LAALLAKUM = Site(hafs=("2:21", (10,)))
ALALAMIN = Site(hafs=("1:2", (4,)))

#: Every shape the divine name is written in, read on its own. The lam is
#: heavy unless a kasra reaches it, and the prefix is what decides.
HEAVY = [
    ("1:1", 2, "ʔalˤlˤaˤ:h"),        # ٱللَّهِ
    ("10:59", 14, "ʔa:lˤlˤaˤ:h"),    # ءَآللَّهُ
    ("2:19", 17, "walˤlˤaˤ:h"),      # وَٱللَّهُ
    ("2:113", 23, "falˤlˤaˤ:h"),     # فَٱللَّهُ
    ("12:73", 2, "talˤlˤaˤ:h"),      # تَٱللَّهِ
    ("21:57", 1, "watalˤlˤaˤ:h"),    # وَتَٱللَّهِ
    ("3:26", 2, "ʔalˤlˤaˤ:hum̃"),    # ٱللَّهُمَّ
]

LIGHT = [
    ("1:2", 2, "lilla:h"),           # لِلَّهِ
    ("2:115", 1, "walilla:h"),       # وَلِلَّهِ
    ("6:149", 2, "falilla:h"),       # فَلِلَّهِ
    ("2:8", 6, "billa:h"),           # بِٱللَّهِ
    ("9:65", 9, "ʔabilla:h"),        # أَبِٱللَّهِ
]


@pytest.mark.parametrize(("ref", "word", "expected"), HEAVY)
def test_the_divine_name_is_heavy_in_every_shape_a_kasra_misses(
    ref, word, expected
):
    site = Site(hafs=(ref, (word,)))
    r = reading(site, isolated=word)
    assert r.phonemes(word) == expected
    assert "tafkheem" in r.rules_on_char(word, "ل")
    assert "tafkheem" in r.rules_on_sound(word, "lˤlˤ")


@pytest.mark.parametrize(("ref", "word", "expected"), LIGHT)
def test_a_kasra_in_the_prefix_makes_that_same_lam_light(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    r = reading(site, isolated=word)
    assert r.phonemes(word) == expected
    assert "tafkheem" not in r.rules_on_char(word, "ل")
    assert "tafkheem" not in r.rules_on_sound(word, "ll")


@for_each_riwayah(QALA_ALLAHU, ibtidaa=1, waqf=2)
def test_the_divine_name_after_a_fatha_is_heavy(r):
    # قَالَ ٱللَّهُ
    assert r.phonemes(2) == "lˤlˤaˤ:h"
    assert "tafkheem" in r.rules_on_char(2, "ل")
    assert "tafkheem" in r.rules_on_sound(2, "lˤlˤ")


@for_each_riwayah(NASRU_ALLAHI, ibtidaa=3, waqf=4)
def test_the_divine_name_after_a_damma_is_heavy(r):
    # نَصْرُ ٱللَّهِ
    assert r.phonemes(4) == "lˤlˤaˤ:h"
    assert "tafkheem" in r.rules_on_char(4, "ل")
    assert "tafkheem" in r.rules_on_sound(4, "lˤlˤ")


@for_each_riwayah(BISMI_ALLAHI, ibtidaa=1, waqf=2)
def test_the_divine_name_joined_after_a_kasra_is_light(r):
    # بِسْمِ ٱللَّهِ
    assert r.phonemes(1) == "bismi"
    assert r.phonemes(2) == "lla:h"
    assert "tafkheem" not in r.rules_on_char(2, "ل")
    assert "tafkheem" not in r.rules_on_sound(2, "ll")


@for_each_riwayah(LAALLAKUM, isolated=10)
def test_an_ordinary_doubled_lam_after_a_fatha_stays_light(r):
    # لَعَلَّكُمْ
    assert r.phonemes(10) == "laʕallakum"
    assert "tafkheem" not in r.rules_on_char(10, "ل")


@for_each_riwayah(ALALAMIN, isolated=4)
def test_an_ordinary_lam_of_the_article_stays_light(r):
    # ٱلْعَـٰلَمِينَ
    assert r.phonemes(4) == "ʔalʕa:lami:n"
    assert "tafkheem" not in r.rules_on_char(4, "ل")
