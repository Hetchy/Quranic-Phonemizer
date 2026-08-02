from __future__ import annotations

from tests.support import Site, for_each_riwayah

BAUDATAN = Site(hafs=("2:26", (9,)))
SINATUN = Site(hafs=("2:255", (10,)))
WAHIDATIN = Site(hafs=("4:1", (9,)))
QUWWATA = Site(hafs=("18:39", (10,)))
TIJARATAN = Site(hafs=("2:282", (99,)))


@for_each_riwayah(BAUDATAN, isolated=9)
def test_a_taa_marbuta_is_read_as_a_haa_at_a_stop(r):
    # بَعُوضَةً
    assert r.phonemes(9) == "baʕu:dˤaˤh"
    assert r.silent(9) == {"ً"}


@for_each_riwayah(BAUDATAN, ibtidaa=9, wasl=9)
def test_that_taa_marbuta_is_read_as_a_taa_when_joined_forward(r):
    # بَعُوضَةً
    assert r.phonemes(9) == "baʕu:dˤaˤtaŋ"
    assert r.silent(9) == frozenset()


@for_each_riwayah(SINATUN, isolated=10)
def test_a_taa_marbuta_after_a_dammatan_becomes_a_haa_at_a_stop(r):
    # سِنَةٌ
    assert r.phonemes(10) == "sinah"
    assert r.silent(10) == {"ٌ"}


@for_each_riwayah(SINATUN, ibtidaa=10, wasl=10)
def test_that_dammatan_word_keeps_its_taa_when_joined_forward(r):
    # سِنَةٌ
    assert r.phonemes(10) == "sinatu"
    assert r.silent(10) == frozenset()


@for_each_riwayah(WAHIDATIN, isolated=9)
def test_a_taa_marbuta_after_a_kasratan_becomes_a_haa_at_a_stop(r):
    # وَٰحِدَةٍ
    assert r.phonemes(9) == "wa:ħidah"
    assert r.silent(9) == {"ٍ"}


@for_each_riwayah(WAHIDATIN, ibtidaa=9, wasl=9)
def test_that_kasratan_word_keeps_its_taa_when_joined_forward(r):
    # وَٰحِدَةٍ
    assert r.phonemes(9) == "wa:ħidati"
    assert r.silent(9) == frozenset()


@for_each_riwayah(QUWWATA, isolated=10)
def test_a_taa_marbuta_carrying_a_plain_fatha_becomes_a_haa(r):
    # قُوَّةَ
    assert r.phonemes(10) == "quwwah"
    assert r.silent(10) == {"َ"}


@for_each_riwayah(QUWWATA, ibtidaa=10, wasl=10)
def test_that_plain_fatha_word_keeps_its_taa_when_joined_forward(r):
    # قُوَّةَ
    assert r.phonemes(10) == "quwwata"
    assert r.silent(10) == frozenset()


@for_each_riwayah(TIJARATAN, isolated=99)
def test_a_taa_marbuta_after_a_fathatan_becomes_a_haa_at_a_stop(r):
    # تِجَـٰرَةً
    assert r.phonemes(99) == "tiʒa:rˤaˤh"
    assert r.silent(99) == {"ً"}


@for_each_riwayah(TIJARATAN, ibtidaa=99, wasl=99)
def test_that_fathatan_word_keeps_its_taa_when_joined_forward(r):
    # تِجَـٰرَةً
    assert r.phonemes(99) == "tiʒa:rˤaˤtan"
    assert r.silent(99) == frozenset()
