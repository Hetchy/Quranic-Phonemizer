from __future__ import annotations

from tests.support import Site, for_each_riwayah

BAUDATAN = Site(hafs=("2:26", (9,)))
BAUDATAN_FAMA = Site(hafs=("2:26", (9, 10)))
SINATUN = Site(hafs=("2:255", (10,)))
SINATUN_WALA = Site(hafs=("2:255", (10, 11)))
WAHIDATIN = Site(hafs=("4:1", (9,)))
WAHIDATIN_WAKHALAQA = Site(hafs=("4:1", (9, 10)))
QUWWATA = Site(hafs=("18:39", (10,)))
TIJARATAN = Site(hafs=("2:282", (99,)))
TIJARATAN_HADIRA = Site(hafs=("2:282", (99, 100)))


@for_each_riwayah(BAUDATAN, isolated=9)
def test_a_taa_marbuta_is_read_as_a_haa_at_a_stop(r):
    # بَعُوضَةً
    assert r.phonemes(9) == "baʕu:dˤaˤh"
    assert r.silent(9) == {"ً"}
    assert "waqf_taa_marbuta" in r.rules_on_char(9, "ة")
    # the substitution owns the consonant and nothing else
    assert r.rules_on_sound(9, "h") == {"waqf_taa_marbuta"}
    # the tanween it was written under is dropped by a rule of its own
    assert "waqf_diacritic_drop" in r.rules_on_char(9, "ً")


@for_each_riwayah(BAUDATAN_FAMA, ibtidaa=9, waqf=10)
def test_that_taa_marbuta_is_read_as_a_taa_when_joined_forward(r):
    # بَعُوضَةً فَمَا
    assert r.phonemes(9) == "baʕu:dˤaˤtaŋ"
    assert r.silent(9) == frozenset()
    assert "waqf_taa_marbuta" not in r.rules_on_char(9, "ة")
    assert r.phonemes(10) == "fama:"


@for_each_riwayah(SINATUN, isolated=10)
def test_a_taa_marbuta_after_a_dammatan_becomes_a_haa_at_a_stop(r):
    # سِنَةٌ
    assert r.phonemes(10) == "sinah"
    assert r.silent(10) == {"ٌ"}
    assert "waqf_taa_marbuta" in r.rules_on_char(10, "ة")
    assert "waqf_taa_marbuta" in r.rules_on_sound(10, "h")


@for_each_riwayah(SINATUN_WALA, ibtidaa=10, waqf=11)
def test_that_dammatan_word_keeps_its_taa_when_joined_forward(r):
    # سِنَةٌ وَلَا
    assert r.phonemes(10) == "sinatu"
    assert r.silent(10) == frozenset()
    assert r.phonemes(11) == "w̃ala:"


@for_each_riwayah(WAHIDATIN, isolated=9)
def test_a_taa_marbuta_after_a_kasratan_becomes_a_haa_at_a_stop(r):
    # وَٰحِدَةٍ
    assert r.phonemes(9) == "wa:ħidah"
    assert r.silent(9) == {"ٍ"}
    assert "waqf_taa_marbuta" in r.rules_on_char(9, "ة")


@for_each_riwayah(WAHIDATIN_WAKHALAQA, ibtidaa=9, waqf=10)
def test_that_kasratan_word_keeps_its_taa_when_joined_forward(r):
    # وَٰحِدَةٍ وَخَلَقَ
    assert r.phonemes(9) == "wa:ħidati"
    assert r.silent(9) == frozenset()
    assert r.phonemes(10) == "w̃axaˤlaqQ"


@for_each_riwayah(QUWWATA, isolated=10)
def test_a_taa_marbuta_carrying_a_plain_fatha_becomes_a_haa(r):
    # قُوَّةَ
    assert r.phonemes(10) == "quwwah"
    assert r.silent(10) == {"َ"}
    assert r.rules_on_sound(10, "h") == {"waqf_taa_marbuta"}
    assert "waqf_diacritic_drop" in r.rules_on_char(10, "َ")


@for_each_riwayah(QUWWATA, ibtidaa=10, wasl=10)
def test_that_plain_fatha_word_keeps_its_taa_when_joined_forward(r):
    # قُوَّةَ
    assert r.phonemes(10) == "quwwata"
    assert r.silent(10) == frozenset()
    assert "waqf_taa_marbuta" not in r.rules_on_char(10, "ة")


@for_each_riwayah(TIJARATAN, isolated=99)
def test_a_taa_marbuta_after_a_fathatan_becomes_a_haa_at_a_stop(r):
    # تِجَـٰرَةً
    assert r.phonemes(99) == "tiʒa:rˤaˤh"
    assert r.silent(99) == {"ً"}
    assert "waqf_taa_marbuta" in r.rules_on_char(99, "ة")


@for_each_riwayah(TIJARATAN_HADIRA, ibtidaa=99, waqf=100)
def test_that_fathatan_word_keeps_its_taa_when_joined_forward(r):
    # تِجَـٰرَةً حَاضِرَةً
    assert r.phonemes(99) == "tiʒa:rˤaˤtan"
    assert r.silent(99) == frozenset()
    assert r.phonemes(100) == "ħa:dˤirˤaˤh"
