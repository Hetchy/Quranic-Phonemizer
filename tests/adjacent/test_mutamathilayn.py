from __future__ import annotations

from tests.support import Site, for_each_riwayah

RABIHAT_TIJARATUHUM = Site(hafs=("2:16", (7, 8)))


@for_each_riwayah(RABIHAT_TIJARATUHUM, wasl=7, waqf=8)
def test_a_letter_merges_into_the_same_letter_across_a_boundary(r):
    # رَبِحَت تِّجَـٰرَتُهُمْ
    assert r.phonemes(7) == "rˤaˤbiħa"
    assert r.phonemes(8) == "ttiʒa:rˤaˤtuhum"
