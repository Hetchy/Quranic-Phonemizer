from __future__ import annotations

from tests.support import Site, for_each_riwayah

YAWMI = Site(hafs=("1:4", (2,)))


@for_each_riwayah(YAWMI, waqf=2)
def test_a_quiescent_waw_after_a_fatha_before_the_stopped_letter(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawm"
