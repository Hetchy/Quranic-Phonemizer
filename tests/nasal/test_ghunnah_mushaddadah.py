from __future__ import annotations

from tests.support import Site, for_each_riwayah

WAMIMMA = Site(hafs=("2:3", (6,)))


@for_each_riwayah(WAMIMMA, waqf=6)
def test_a_doubled_meem_is_held_through_the_nose(r):
    # وَمِمَّا
    assert r.phonemes(6) == "wamim̃a:"
