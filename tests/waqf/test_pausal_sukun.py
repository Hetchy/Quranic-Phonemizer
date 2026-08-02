from __future__ import annotations

from tests.support import Site, for_each_riwayah

DHALIKA = Site(hafs=("2:2", (1,)))
AL_KITAB = Site(hafs=("2:2", (2,)))
RABBI = Site(hafs=("1:2", (3,)))
AJRAN = Site(hafs=("4:40", (14,)))
ADHABUN = Site(hafs=("2:10", (8,)))
BIGHADABIN = Site(hafs=("2:90", (22,)))


@for_each_riwayah(DHALIKA, isolated=1)
def test_a_final_fatha_is_dropped_at_a_stop(r):
    # ذَٰلِكَ
    assert r.phonemes(1) == "ða:lik"
    assert r.silent(1) == {"َ"}


@for_each_riwayah(DHALIKA, ibtidaa=1, wasl=1)
def test_that_fatha_is_sounded_when_the_reading_carries_on(r):
    # ذَٰلِكَ
    assert r.phonemes(1) == "ða:lika"
    assert r.silent(1) == frozenset()


@for_each_riwayah(AL_KITAB, isolated=2)
def test_a_final_damma_is_dropped_at_a_stop(r):
    # ٱلْكِتَـٰبُ
    assert r.phonemes(2) == "ʔalkita:bQ"
    assert r.silent(2) == {"ُ"}


@for_each_riwayah(AL_KITAB, ibtidaa=2, wasl=2)
def test_that_damma_is_sounded_when_the_reading_carries_on(r):
    # ٱلْكِتَـٰبُ
    assert r.phonemes(2) == "ʔalkita:bu"
    assert r.silent(2) == frozenset()


@for_each_riwayah(RABBI, isolated=3)
def test_a_final_kasra_is_dropped_at_a_stop(r):
    # رَبِّ
    assert r.phonemes(3) == "rˤaˤbbQ"
    assert r.silent(3) == {"ِ"}


@for_each_riwayah(RABBI, ibtidaa=3, wasl=3)
def test_that_kasra_is_sounded_when_the_reading_carries_on(r):
    # رَبِّ
    assert r.phonemes(3) == "rˤaˤbbi"
    assert r.silent(3) == frozenset()


@for_each_riwayah(ADHABUN, isolated=8)
def test_a_final_dammatan_is_dropped_at_a_stop(r):
    # عَذَابٌ
    assert r.phonemes(8) == "ʕaða:bQ"
    assert r.silent(8) == {"ٌ"}


@for_each_riwayah(ADHABUN, ibtidaa=8, wasl=8)
def test_that_dammatan_is_sounded_when_the_reading_carries_on(r):
    # عَذَابٌ
    assert r.phonemes(8) == "ʕaða:bun"
    assert r.silent(8) == frozenset()


@for_each_riwayah(BIGHADABIN, isolated=22)
def test_a_final_kasratan_is_dropped_at_a_stop(r):
    # بِغَضَبٍ
    assert r.phonemes(22) == "biɣaˤdˤaˤbQ"
    assert r.silent(22) == {"ٍ"}


@for_each_riwayah(BIGHADABIN, ibtidaa=22, wasl=22)
def test_that_kasratan_is_sounded_when_the_reading_carries_on(r):
    # بِغَضَبٍ
    assert r.phonemes(22) == "biɣaˤdˤaˤbin"
    assert r.silent(22) == frozenset()


@for_each_riwayah(AJRAN, isolated=14)
def test_a_final_fathatan_lengthens_instead_of_falling_silent(r):
    # أَجْرًا
    assert r.phonemes(14) == "ʔaʒQrˤaˤ:"
    assert r.silent(14) == {"ً"}


@for_each_riwayah(AJRAN, ibtidaa=14, wasl=14)
def test_that_fathatan_is_sounded_when_the_reading_carries_on(r):
    # أَجْرًا
    assert r.phonemes(14) == "ʔaʒQrˤaˤn"
    assert r.silent(14) == frozenset()
