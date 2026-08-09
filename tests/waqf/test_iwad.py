from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUDAN = Site(hafs=("2:5", (3,)))
HUDAN_MIN = Site(hafs=("2:5", (3, 4)))
ITHMAN = Site(hafs=("4:48", (19,)))
ITHMAN_AZIMA = Site(hafs=("4:48", (19, 20)))
GHAFURUN = Site(hafs=("2:225", (13,)))
GHAFURUN_HALIM = Site(hafs=("2:225", (13, 14)))
LIQAWMIN = Site(hafs=("5:41", (23,)))
LIQAWMIN_AAKHARIN = Site(hafs=("5:41", (23, 24)))


@for_each_riwayah(HUDAN, isolated=3)
def test_a_fathatan_lengthens_the_letter_before_it_at_a_stop(r):
    # هُدًى
    assert r.phonemes(3) == "huda:"
    assert r.silent(3) == {"ً", "ى"}
    assert "iwad" in r.rules_on_char(3, "ً")
    assert "iwad" in r.rules_on_sound(3, "a:")


@for_each_riwayah(HUDAN_MIN, ibtidaa=3, waqf=4)
def test_that_fathatan_stays_a_short_vowel_when_joined_forward(r):
    # هُدًى مِّن
    assert r.phonemes(3) == "huda"
    assert r.silent(3) == frozenset()
    assert r.phonemes(4) == "m̃in"
    assert "iwad" not in r.rules_on_char(3, "ً")


@for_each_riwayah(ITHMAN, isolated=19)
def test_a_fathatan_written_on_an_alif_lengthens_at_a_stop(r):
    # إِثْمًا
    assert r.phonemes(19) == "ʔiθma:"
    assert r.silent(19) == {"ً"}
    assert "iwad" in r.rules_on_char(19, "ً")
    assert "iwad" in r.rules_on_sound(19, "a:")


@for_each_riwayah(ITHMAN_AZIMA, ibtidaa=19, waqf=20)
def test_that_alif_carries_a_sounded_noon_when_joined_forward(r):
    # إِثْمًا عَظِيمًا
    assert r.phonemes(19) == "ʔiθman"
    assert r.silent(19) == frozenset()
    assert r.phonemes(20) == "ʕaðˤi:ma:"
    assert "iwad" not in r.rules_on_char(19, "ً")


@for_each_riwayah(GHAFURUN, isolated=13)
def test_a_dammatan_is_simply_dropped_at_a_stop(r):
    # غَفُورٌ
    assert r.phonemes(13) == "ɣaˤfu:rˤ"
    assert r.silent(13) == {"ٌ"}
    # only a fathatan is exchanged for length; the other two are dropped
    assert "iwad" not in r.rules_on_char(13, "ٌ")


@for_each_riwayah(GHAFURUN_HALIM, ibtidaa=13, waqf=14)
def test_that_dammatan_is_sounded_in_full_when_joined_forward(r):
    # غَفُورٌ حَلِيمٌ
    assert r.phonemes(13) == "ɣaˤfu:rˤun"
    assert r.silent(13) == frozenset()
    assert r.phonemes(14) == "ħali:m"


@for_each_riwayah(LIQAWMIN, isolated=23)
def test_a_kasratan_is_simply_dropped_at_a_stop(r):
    # لِقَوْمٍ
    assert r.phonemes(23) == "liqaˤwm"
    assert r.silent(23) == {"ٍ"}
    assert "iwad" not in r.rules_on_char(23, "ٍ")


@for_each_riwayah(LIQAWMIN_AAKHARIN, ibtidaa=23, waqf=24)
def test_that_kasratan_is_sounded_in_full_when_joined_forward(r):
    # لِقَوْمٍ ءَاخَرِينَ
    assert r.phonemes(23) == "liqaˤwmin"
    assert r.silent(23) == frozenset()
    assert r.phonemes(24) == "ʔa:xaˤri:n"
