from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUMU = Site(hafs=("8:4", (2,)))


@for_each_riwayah(HUMU, isolated=2)
def test_a_stop_makes_a_final_voweled_meem_clear(r):
    assert r.phonemes(2) == "hum"
    assert r.rules_on_sound(2, "m") == {"izhar_shafawi"}

ALHAMDU = Site(hafs=("1:2", (1,)))
ANAMTA = Site(hafs=("1:7", (3,)))
AMTHALAHUM = Site(hafs=("47:3", (18,)))


@for_each_riwayah(ALHAMDU, isolated=1)
def test_a_quiescent_meem_before_a_daal_stays_clear(r):
    # ٱلْحَمْدُ
    assert r.phonemes(1) == "ʔalħamdQ"
    assert "izhar_shafawi" in r.rules_on_char(1, "م")
    assert r.rules_on_sound(1, "m") == {"izhar_shafawi"}


@for_each_riwayah(ANAMTA, isolated=3)
def test_a_quiescent_meem_before_a_taa_stays_clear(r):
    # أَنْعَمْتَ
    assert r.phonemes(3) == "ʔanʕamt"
    assert "izhar_shafawi" in r.rules_on_char(3, "م")
    assert r.rules_on_sound(3, "m") == {"izhar_shafawi"}


@for_each_riwayah(AMTHALAHUM, ibtidaa=18, wasl=18)
def test_a_meem_at_a_verse_end_stays_clear_before_a_faa(r):
    # أَمْثَـٰلَهُمْ فَإِذَا
    assert r.phonemes(18) == "ʔamθa:lahum"
    assert r.phonemes(19) == "faʔiða:"
    assert "izhar_shafawi" in r.rules_on_char(18, "م")
    assert r.rules_on_sound(18, "m") == {"izhar_shafawi"}
