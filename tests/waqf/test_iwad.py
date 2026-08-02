from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUDAN = Site(hafs=("2:5", (3,)))
ITHMAN = Site(hafs=("4:48", (19,)))
GHAFURUN = Site(hafs=("2:225", (13,)))
LIQAWMIN = Site(hafs=("5:41", (23,)))


@for_each_riwayah(HUDAN, isolated=3)
def test_a_fathatan_lengthens_the_letter_before_it_at_a_stop(r):
    # هُدًى
    assert r.phonemes(3) == "huda:"
    assert r.silent(3) == {"ً", "ى"}


@for_each_riwayah(HUDAN, ibtidaa=3, wasl=3)
def test_that_fathatan_stays_a_short_vowel_when_joined_forward(r):
    # هُدًى
    assert r.phonemes(3) == "huda"
    assert r.silent(3) == frozenset()


@for_each_riwayah(ITHMAN, isolated=19)
def test_a_fathatan_written_on_an_alif_lengthens_at_a_stop(r):
    # إِثْمًا
    assert r.phonemes(19) == "ʔiθma:"
    assert r.silent(19) == {"ً"}


@for_each_riwayah(ITHMAN, ibtidaa=19, wasl=19)
def test_that_alif_carries_a_sounded_noon_when_joined_forward(r):
    # إِثْمًا
    assert r.phonemes(19) == "ʔiθman"
    assert r.silent(19) == frozenset()


@for_each_riwayah(GHAFURUN, isolated=13)
def test_a_dammatan_is_simply_dropped_at_a_stop(r):
    # غَفُورٌ
    assert r.phonemes(13) == "ɣaˤfu:rˤ"
    assert r.silent(13) == {"ٌ"}


@for_each_riwayah(GHAFURUN, ibtidaa=13, wasl=13)
def test_that_dammatan_is_sounded_in_full_when_joined_forward(r):
    # غَفُورٌ
    assert r.phonemes(13) == "ɣaˤfu:rˤun"
    assert r.silent(13) == frozenset()


@for_each_riwayah(LIQAWMIN, isolated=23)
def test_a_kasratan_is_simply_dropped_at_a_stop(r):
    # لِقَوْمٍ
    assert r.phonemes(23) == "liqaˤwm"
    assert r.silent(23) == {"ٍ"}


@for_each_riwayah(LIQAWMIN, ibtidaa=23, wasl=23)
def test_that_kasratan_is_sounded_in_full_when_joined_forward(r):
    # لِقَوْمٍ
    assert r.phonemes(23) == "liqaˤwmin"
    assert r.silent(23) == frozenset()
