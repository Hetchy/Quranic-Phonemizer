from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUM_BIMUMININ = Site(hafs=("2:8", (10, 11)))


@for_each_riwayah(HUM_BIMUMININ, ibtidaa=10, waqf=11)
def test_a_quiescent_meem_before_a_baa_is_hidden_at_the_lips(r):
    # هُم بِمُؤْمِنِينَ
    assert r.phonemes(10) == "huŋ"
    assert r.phonemes(11) == "bimuʔmini:n"
