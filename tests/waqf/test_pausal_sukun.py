from __future__ import annotations

from tests.support import Site, for_each_riwayah

DHALIKA = Site(hafs=("2:2", (1,)))
AL_KITAB = Site(hafs=("2:2", (2,)))
RABBI = Site(hafs=("1:2", (3,)))


@for_each_riwayah(DHALIKA, isolated=1)
def test_a_final_fatha_is_dropped_at_a_stop(r):
    # ذَٰلِكَ
    assert r.phonemes(1) == "ða:lik"
    assert r.silent(1) == {"َ"}
    assert "pausal_sukun" in r.rules_on_char(1, "ك")


@for_each_riwayah(DHALIKA, ibtidaa=1, wasl=1)
def test_that_fatha_is_sounded_when_the_reading_carries_on(r):
    # ذَٰلِكَ
    assert r.phonemes(1) == "ða:lika"
    assert r.silent(1) == frozenset()
    assert "pausal_sukun" not in r.rules_on_char(1, "ك")


@for_each_riwayah(AL_KITAB, isolated=2)
def test_a_final_damma_is_dropped_at_a_stop(r):
    # ٱلْكِتَـٰبُ
    assert r.phonemes(2) == "ʔalkita:bQ"
    assert r.silent(2) == {"ُ"}
    assert "pausal_sukun" in r.rules_on_char(2, "ب")


@for_each_riwayah(AL_KITAB, ibtidaa=2, wasl=2)
def test_that_damma_is_sounded_when_the_reading_carries_on(r):
    # ٱلْكِتَـٰبُ
    assert r.phonemes(2) == "ʔalkita:bu"
    assert r.silent(2) == frozenset()
    assert "pausal_sukun" not in r.rules_on_char(2, "ب")


@for_each_riwayah(RABBI, isolated=3)
def test_a_final_kasra_is_dropped_at_a_stop(r):
    # رَبِّ
    assert r.phonemes(3) == "rˤaˤbbQ"
    assert r.silent(3) == {"ِ"}
    assert "pausal_sukun" in r.rules_on_char(3, "ب")


@for_each_riwayah(RABBI, ibtidaa=3, wasl=3)
def test_that_kasra_is_sounded_when_the_reading_carries_on(r):
    # رَبِّ
    assert r.phonemes(3) == "rˤaˤbbi"
    assert r.silent(3) == frozenset()
    assert "pausal_sukun" not in r.rules_on_char(3, "ب")
