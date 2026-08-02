from __future__ import annotations

from tests.support import Site, for_each_riwayah

BASATTA = Site(hafs=("5:28", (2,)))
AHATTU = Site(hafs=("27:22", (5,)))


@for_each_riwayah(BASATTA, waqf=2)
def test_a_taa_keeps_the_heaviness_of_the_taa_before_it(r):
    # بَسَطتَ
    assert r.phonemes(2) == "basatˤt"


@for_each_riwayah(AHATTU, waqf=5)
def test_the_same_partial_merger_before_a_damma(r):
    # أَحَطتُ
    assert r.phonemes(5) == "ʔaħatˤt"
