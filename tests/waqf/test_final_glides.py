from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUWA = Site(hafs=("2:29", (1,)))
WA_HUWA = Site(hafs=("2:29", (16,)))
HIYA = Site(hafs=("2:70", (8,)))
RABBIYA = Site(hafs=("2:258", (16,)))
AMILU_SSALIHAT = Site(hafs=("2:25", (4, 5)))
KAFARU_SAWAAUN = Site(hafs=("2:6", (3, 4)))


@for_each_riwayah(HUWA, ibtidaa=1, wasl=1)
def test_a_final_waw_is_a_consonant_when_the_reading_carries_on(r):
    # هُوَ
    assert r.phonemes(1) == "huwa"
    assert r.silent(1) == frozenset()


@for_each_riwayah(HUWA, isolated=1)
def test_that_waw_becomes_pure_length_at_a_stop(r):
    # هُوَ
    assert r.phonemes(1) == "hu:"
    assert r.silent(1) == {"َ"}


@for_each_riwayah(WA_HUWA, ibtidaa=16, wasl=16)
def test_a_prefixed_word_keeps_its_consonantal_waw_when_joined(r):
    # وَهُوَ
    assert r.phonemes(16) == "wahuwa"
    assert r.silent(16) == frozenset()


@for_each_riwayah(WA_HUWA, isolated=16)
def test_that_prefixed_waw_becomes_pure_length_at_a_stop(r):
    # وَهُوَ
    assert r.phonemes(16) == "wahu:"
    assert r.silent(16) == {"َ"}


@for_each_riwayah(HIYA, ibtidaa=8, wasl=8)
def test_a_final_yaa_is_a_consonant_when_the_reading_carries_on(r):
    # هِىَ
    assert r.phonemes(8) == "hija"
    assert r.silent(8) == frozenset()


@for_each_riwayah(HIYA, isolated=8)
def test_that_yaa_becomes_pure_length_at_a_stop(r):
    # هِىَ
    assert r.phonemes(8) == "hi:"
    assert r.silent(8) == {"َ"}


@for_each_riwayah(RABBIYA, ibtidaa=16, wasl=16)
def test_a_pronoun_yaa_is_a_consonant_when_the_reading_carries_on(r):
    # رَبِّىَ
    assert r.phonemes(16) == "rˤaˤbbija"
    assert r.silent(16) == frozenset()


@for_each_riwayah(RABBIYA, isolated=16)
def test_that_pronoun_yaa_becomes_pure_length_at_a_stop(r):
    # رَبِّىَ
    assert r.phonemes(16) == "rˤaˤbbi:"
    assert r.silent(16) == {"َ"}


@for_each_riwayah(AMILU_SSALIHAT, isolated=4)
def test_a_plural_waw_is_length_already_and_the_alif_after_it_is_not_read(r):
    # وَعَمِلُوا۟
    assert r.phonemes(4) == "waʕamilu:"


@for_each_riwayah(AMILU_SSALIHAT, ibtidaa=4, waqf=5)
def test_that_length_shortens_onto_a_word_whose_hamza_has_elided(r):
    # وَعَمِلُوا۟ ٱلصَّـٰلِحَـٰتِ
    assert r.phonemes(4) == "waʕamilu"
    assert r.phonemes(5) == "sˤsˤaˤ:liħa:t"


@for_each_riwayah(KAFARU_SAWAAUN, ibtidaa=3, waqf=4)
def test_the_same_waw_keeps_its_length_onto_a_word_that_opens_on_a_vowel(r):
    # كَفَرُوا۟ سَوَآءٌ
    assert r.phonemes(3) == "kafarˤu:"
    assert r.phonemes(4) == "sawa:ʔ"
