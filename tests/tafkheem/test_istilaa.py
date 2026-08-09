from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

HEAVY = [
    ("2:29", 3, "خ", "xaˤlaqQ"),        # خَلَقَ
    ("11:11", 3, "ص", "sˤaˤbarˤu:"),    # صَبَرُوا۟
    ("30:28", 1, "ض", "dˤaˤrˤaˤbQ"),    # ضَرَبَ
    ("2:173", 24, "غ", "ɣaˤfu:rˤ"),     # غَفُورٌ
    ("16:108", 3, "ط", "tˤaˤbaʕ"),      # طَبَعَ
    ("2:33", 1, "ق", "qaˤ:l"),          # قَالَ
    ("2:231", 19, "ظ", "ðˤaˤlam"),      # ظَلَمَ
]

LIGHT = [
    ("5:83", 2, "س", "samiʕu:"),        # سَمِعُوا۟
    ("2:38", 10, "ت", "tabiʕ"),         # تَبِعَ
    ("3:38", 2, "د", "daʕa:"),          # دَعَا
    ("2:17", 10, "ذ", "ðahabQ"),        # ذَهَبَ
    ("2:97", 3, "ك", "ka:n"),           # كَانَ
]

ADDALLIN = Site(hafs=("1:7", (9,)))
DAKHALA = Site(hafs=("3:37", (11,)))
QUL = Site(hafs=("2:80", (8,)))
KHUDHU = Site(hafs=("2:63", (7,)))
GHUFRANAK = Site(hafs=("2:285", (24,)))
SUDURUHUM = Site(hafs=("3:118", (22,)))


@pytest.mark.parametrize(("ref", "word", "letter", "expected"), HEAVY)
def test_every_istilaa_letter_is_heavy(ref, word, letter, expected):
    site = Site(hafs=(ref, (word,)))
    r = reading(site, isolated=word)
    assert r.phonemes(word) == expected
    assert "tafkheem" in r.rules_on_char(word, letter)


@pytest.mark.parametrize(("ref", "word", "letter", "expected"), LIGHT)
def test_the_light_counterpart_letters_stay_light(ref, word, letter, expected):
    site = Site(hafs=(ref, (word,)))
    r = reading(site, isolated=word)
    assert r.phonemes(word) == expected
    assert "tafkheem" not in r.rules_on_char(word, letter)


@for_each_riwayah(ADDALLIN, isolated=9)
def test_a_daad_is_heavy_and_carries_its_alif_with_it(r):
    # ٱلضَّآلِّينَ
    assert r.phonemes(9) == "ʔadˤdˤaˤ:lli:n"
    assert "tafkheem" in r.rules_on_char(9, "ض")


@for_each_riwayah(DAKHALA, isolated=11)
def test_one_word_can_hold_a_light_dal_and_a_heavy_khaa(r):
    # دَخَلَ
    assert r.phonemes(11) == "daxaˤl"
    assert "tafkheem" not in r.rules_on_char(11, "د")
    assert "tafkheem" in r.rules_on_char(11, "خ")


@for_each_riwayah(QUL, isolated=8)
def test_a_heavy_qaf_over_a_damma_leaves_the_vowel_alone(r):
    # قُلْ
    assert r.phonemes(8) == "qul"
    assert "tafkheem" in r.rules_on_char(8, "ق")


@for_each_riwayah(KHUDHU, isolated=7)
def test_a_khaa_over_a_damma_leaves_the_vowel_alone(r):
    # خُذُوا۟
    assert r.phonemes(7) == "xuðu:"
    assert "tafkheem" in r.rules_on_char(7, "خ")


@for_each_riwayah(GHUFRANAK, isolated=24)
def test_a_ghayn_over_a_damma_leaves_its_own_vowel_alone(r):
    # غُفْرَانَكَ
    assert r.phonemes(24) == "ɣufrˤaˤ:nak"
    assert "tafkheem" in r.rules_on_char(24, "غ")


@for_each_riwayah(SUDURUHUM, isolated=22)
def test_a_sad_over_a_damma_leaves_the_vowel_alone(r):
    # صُدُورُهُمْ
    assert r.phonemes(22) == "sˤudu:rˤuhum"
    assert "tafkheem" in r.rules_on_char(22, "ص")


KHALAQA = Site(hafs=("2:29", (3,)))


def test_the_heavy_fatha_toggle_defaults_off():
    # خَلَقَ -- the khaa's heaviness spreads onto its own fatha.
    off = reading(KHALAQA, extra_phonemes=(), isolated=3)
    on = reading(KHALAQA, extra_phonemes=("emphatic_fatha",), isolated=3)
    assert off.phonemes(3) == "xalaqQ"
    assert on.phonemes(3) == "xaˤlaqQ"
