from __future__ import annotations

from tests.support import Site, for_each_riwayah

BISMI_ALLAHI = Site(hafs=("1:1", (1, 2)))


@for_each_riwayah(BISMI_ALLAHI, wasl=1, waqf=2)
def test_a_prosthetic_hamza_drops_when_the_word_before_it_joins(r):
    # بِسْمِ ٱللَّهِ
    assert r.phonemes(1) == "bismi"
    assert r.phonemes(2) == "lla:h"
    assert r.silent(2) == {"ِ", "ٱ"}
