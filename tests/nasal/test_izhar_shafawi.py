from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALHAMDU = Site(hafs=("1:2", (1,)))
ANAMTA = Site(hafs=("1:7", (3,)))
AMTHALAHUM = Site(hafs=("47:3", (18,)))


@for_each_riwayah(ALHAMDU, isolated=1)
def test_a_quiescent_meem_before_a_daal_stays_clear(r):
    # ٱلْحَمْدُ
    assert r.phonemes(1) == "ʔalħamdQ"


@for_each_riwayah(ANAMTA, isolated=3)
def test_a_quiescent_meem_before_a_taa_stays_clear(r):
    # أَنْعَمْتَ
    assert r.phonemes(3) == "ʔanʕamt"


@for_each_riwayah(AMTHALAHUM, ibtidaa=18, wasl=18)
def test_a_meem_at_a_verse_end_stays_clear_before_a_faa(r):
    # أَمْثَـٰلَهُمْ فَإِذَا
    assert r.phonemes(18) == "ʔamθa:lahum"
    assert r.phonemes(19) == "faʔiða:"
