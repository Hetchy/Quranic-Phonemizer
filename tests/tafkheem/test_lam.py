from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALLAHU = Site(hafs=("2:15", (1,)))
LILLAHI = Site(hafs=("1:2", (2,)))


@for_each_riwayah(ALLAHU, ibtidaa=1, waqf=1)
def test_the_lam_of_the_divine_name_is_heavy_after_a_fatha(r):
    # ٱللَّهُ
    assert r.phonemes(1) == "ʔalˤlˤaˤ:h"


@for_each_riwayah(LILLAHI, waqf=2)
def test_the_same_lam_is_light_after_a_kasra(r):
    # لِلَّهِ
    assert r.phonemes(2) == "lilla:h"
