from __future__ import annotations

from tests.support import Site, for_each_riwayah

ASSIRAT = Site(hafs=("1:6", (2,)))


@for_each_riwayah(ASSIRAT, waqf=2)
def test_an_istilaa_letter_is_heavy_and_carries_its_vowel_with_it(r):
    # ٱلصِّرَٰطَ
    assert r.phonemes(2) == "sˤsˤirˤaˤ:tˤQ"
