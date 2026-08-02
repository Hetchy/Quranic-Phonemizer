from __future__ import annotations

from tests.support import Site, for_each_riwayah

ARRAHMAN = Site(hafs=("1:1", (3,)))
GHAYRI = Site(hafs=("1:7", (5,)))


@for_each_riwayah(ARRAHMAN, waqf=3)
def test_a_raa_with_a_fatha_is_heavy(r):
    # ٱلرَّحْمَـٰنِ
    assert r.phonemes(3) == "rˤrˤaˤħma:n"


@for_each_riwayah(GHAYRI, waqf=5)
def test_a_raa_after_a_quiescent_yaa_is_light(r):
    # غَيْرِ
    assert r.phonemes(5) == "ɣaˤjr"
