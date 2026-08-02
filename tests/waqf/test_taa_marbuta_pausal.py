from __future__ import annotations

from tests.support import Site, for_each_riwayah

BAUDATAN = Site(hafs=("2:26", (9,)))


@for_each_riwayah(BAUDATAN, waqf=9)
def test_a_taa_marbuta_is_read_as_a_haa_at_a_stop(r):
    # بَعُوضَةً
    assert r.phonemes(9) == "baʕu:dˤaˤh"
    assert r.silent(9) == {"ً"}
