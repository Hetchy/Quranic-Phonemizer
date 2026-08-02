from __future__ import annotations

from tests.support import Site, for_each_riwayah

BIMA = Site(hafs=("2:10", (10,)))
SAWAA = Site(hafs=("2:6", (4,)))
BIMA_UNZILA = Site(hafs=("2:4", (3, 4)))
ALIF_LAM_MEEM = Site(hafs=("2:1", (1,)))
ADHDHAKARAYN = Site(hafs=("6:143", (10,)))
YUNFIQUN = Site(hafs=("2:3", (8,)))
YAWMI = Site(hafs=("1:4", (2,)))


@for_each_riwayah(BIMA, isolated=10)
def test_an_ordinary_long_vowel_needs_no_rule_to_be_long(r):
    # بِمَا
    assert r.phonemes(10) == "bima:"


@for_each_riwayah(SAWAA, isolated=4)
def test_a_long_vowel_before_a_hamza_in_the_same_word(r):
    # سَوَآءٌ
    assert r.phonemes(4) == "sawa:ʔ"


@for_each_riwayah(BIMA_UNZILA, ibtidaa=3, waqf=4)
def test_a_long_vowel_ending_a_word_before_a_hamza_opening_the_next(r):
    # بِمَآ أُنزِلَ
    assert r.phonemes(3) == "bima:"
    assert r.phonemes(4) == "ʔuŋzil"


@for_each_riwayah(ALIF_LAM_MEEM, isolated=1)
def test_a_long_vowel_before_a_quiescent_letter(r):
    # الٓمٓ
    assert r.phonemes(1) == "ʔalifla:m̃i:m"


@for_each_riwayah(ADHDHAKARAYN, isolated=10)
def test_the_same_length_after_an_interrogative_hamza(r):
    # ءَآلذَّكَرَيْنِ
    assert r.phonemes(10) == "ʔa:ððakarˤaˤjn"


@for_each_riwayah(YUNFIQUN, isolated=8)
def test_a_long_vowel_before_a_letter_the_stop_silences(r):
    # يُنفِقُونَ
    assert r.phonemes(8) == "juŋfiqu:n"
    assert r.silent(8) == {"َ"}


@for_each_riwayah(YAWMI, isolated=2)
def test_a_quiescent_waw_after_a_fatha_before_the_stopped_letter(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawm"


@for_each_riwayah(YAWMI, ibtidaa=2, wasl=2)
def test_the_same_waw_is_an_ordinary_glide_when_the_reading_joins(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawmi"
