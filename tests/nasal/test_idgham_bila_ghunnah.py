from __future__ import annotations

from tests.support import Site, for_each_riwayah

MIN_RABBIHIM = Site(hafs=("2:5", (4, 5)))


@for_each_riwayah(MIN_RABBIHIM, wasl=4, waqf=5)
def test_a_quiescent_noon_merges_into_a_raa_without_a_hum(r):
    # مِّن رَّبِّهِمْ
    assert r.phonemes(4) == "m̃i"
    assert r.phonemes(5) == "rˤrˤaˤbbihim"
