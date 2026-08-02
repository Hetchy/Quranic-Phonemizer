from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALHAMDU = Site(hafs=("1:2", (1,)))
ANAMTA = Site(hafs=("1:7", (3,)))


@for_each_riwayah(ALHAMDU, waqf=1)
def test_a_quiescent_meem_before_a_daal_stays_clear(r):
    # ٱلْحَمْدُ
    assert r.phonemes(1) == "ʔalħamdQ"


@for_each_riwayah(ANAMTA, waqf=3)
def test_a_quiescent_meem_before_a_taa_stays_clear(r):
    # أَنْعَمْتَ
    assert r.phonemes(3) == "ʔanʕamt"
