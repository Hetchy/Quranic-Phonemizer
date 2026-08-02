from __future__ import annotations

from tests.support import Site, for_each_riwayah

ITUNI = Site(hafs=("46:4", (18,)))
ITHAN = Site(hafs=("9:49", (3, 4)))
UTUMINA = Site(hafs=("2:283", (15, 16)))
ITUNI_JOINED = Site(hafs=("12:50", (2, 3)))


@for_each_riwayah(ITUNI, ibtidaa=18, waqf=18)
def test_a_quiescent_hamza_becomes_a_length_when_started_on(r):
    # ٱئْتُونِى
    assert r.phonemes(18) == "ʔi:tu:ni:"
    assert r.silent(18) == {"ئ"}


@for_each_riwayah(ITUNI_JOINED, ibtidaa=2, waqf=3)
def test_the_same_hamza_is_said_as_a_hamza_when_the_word_before_joins(r):
    # ٱلْمَلِكُ ٱئْتُونِى
    assert r.phonemes(2) == "ʔalmaliku"
    assert r.phonemes(3) == "ʔtu:ni:"
    assert r.silent(3) == {"ٱ"}


@for_each_riwayah(ITHAN, ibtidaa=4, waqf=4)
def test_a_quiescent_hamza_after_a_kasra_lengthens_into_a_yaa(r):
    # ٱئْذَن
    assert r.phonemes(4) == "ʔi:ðan"


@for_each_riwayah(ITHAN, ibtidaa=3, waqf=4)
def test_that_same_word_keeps_its_hamza_once_it_is_joined_into(r):
    # يَقُولُ ٱئْذَن
    assert r.phonemes(3) == "jaqu:lu"
    assert r.phonemes(4) == "ʔðan"


@for_each_riwayah(UTUMINA, ibtidaa=16, waqf=16)
def test_a_quiescent_hamza_after_a_damma_lengthens_into_a_waw(r):
    # ٱؤْتُمِنَ
    assert r.phonemes(16) == "ʔu:tumin"


@for_each_riwayah(UTUMINA, ibtidaa=15, waqf=16)
def test_that_same_word_keeps_its_hamza_once_the_relative_joins_into_it(r):
    # ٱلَّذِى ٱؤْتُمِنَ
    assert r.phonemes(15) == "ʔallaði"
    assert r.phonemes(16) == "ʔtumin"
