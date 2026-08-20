from __future__ import annotations

from tests.support import Site, for_each_riwayah

ITUNI = Site(hafs=("46:4", (18,)))
ITHAN = Site(hafs=("9:49", (3, 4)))
UTUMINA = Site(hafs=("2:283", (15, 16)))
ITUNI_JOINED = Site(hafs=("12:50", (2, 3)))


@for_each_riwayah(ITUNI, isolated=18)
def test_a_quiescent_hamza_becomes_a_length_when_started_on(r):
    # ٱئْتُونِى
    assert r.phonemes(18) == "ʔi:tu:ni:"
    assert r.silent(18) == {"ئ"}
    assert "ibdal_hamza" in r.rules_on_char(18, "ٱ")


@for_each_riwayah(ITUNI, isolated=18)
def test_the_ibdal_names_the_hamza_it_replaced(r):
    """The quiescent hamza is the subject; the prosthetic one it lengthens
    is named by the start rule that sounds it."""
    # ٱئْتُونِى
    assert r.source_of("ibdal_hamza") == "ئ"
    assert r.host_of("ibdal_hamza") == "ٱ"
    assert "hamza_wasl_kasra" in r.rules_on_char(18, "ٱ")


@for_each_riwayah(ITUNI, isolated=18)
def test_the_length_the_ibdal_made_takes_no_madd_beside_it(r):
    """The helping vowel is short in the reading and long only because the
    ibdal lengthened it, so no madd over the reading names it."""
    # ٱئْتُونِى
    assert r.rules_on_char(18, "ٱ") == {"ibdal_hamza", "hamza_wasl_kasra"}
    assert r.rules_on_char(18, "ئ") == {"ibdal_hamza"}


@for_each_riwayah(ITUNI_JOINED, ibtidaa=2, waqf=3)
def test_the_same_hamza_is_said_as_a_hamza_when_the_word_before_joins(r):
    # ٱلْمَلِكُ ٱئْتُونِى
    assert r.phonemes(2) == "ʔalmaliku"
    assert r.phonemes(3) == "ʔtu:ni:"
    assert r.silent(3) == {"ٱ"}
    assert "ibdal_hamza" not in r.rules_on_char(3, "ٱ")


@for_each_riwayah(ITHAN, isolated=4)
def test_a_quiescent_hamza_after_a_kasra_lengthens_into_a_yaa(r):
    # ٱئْذَن
    assert r.phonemes(4) == "ʔi:ðan"
    assert "ibdal_hamza" in r.rules_on_char(4, "ٱ")


@for_each_riwayah(ITHAN, ibtidaa=3, waqf=4)
def test_that_same_word_keeps_its_hamza_once_it_is_joined_into(r):
    # يَقُولُ ٱئْذَن
    assert r.phonemes(3) == "jaqu:lu"
    assert r.phonemes(4) == "ʔðan"
    assert "ibdal_hamza" not in r.rules_on_char(4, "ٱ")


@for_each_riwayah(UTUMINA, isolated=16)
def test_a_quiescent_hamza_after_a_damma_lengthens_into_a_waw(r):
    # ٱؤْتُمِنَ
    assert r.phonemes(16) == "ʔu:tumin"
    assert "ibdal_hamza" in r.rules_on_char(16, "ٱ")


@for_each_riwayah(UTUMINA, ibtidaa=15, waqf=16)
def test_that_same_word_keeps_its_hamza_once_the_relative_joins_into_it(r):
    # ٱلَّذِى ٱؤْتُمِنَ
    assert r.phonemes(15) == "ʔallaði"
    assert r.phonemes(16) == "ʔtumin"
    assert "ibdal_hamza" not in r.rules_on_char(16, "ٱ")
