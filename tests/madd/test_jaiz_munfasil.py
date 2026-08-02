from __future__ import annotations

from tests.support import Site, for_each_riwayah

BIMA_UNZILA = Site(hafs=("2:4", (3, 4)))


@for_each_riwayah(BIMA_UNZILA, wasl=3, waqf=4)
def test_a_long_vowel_ending_a_word_before_a_hamza_opening_the_next(r):
    # بِمَآ أُنزِلَ
    assert r.phonemes(3) == "bima:"
    assert r.phonemes(4) == "ʔuŋzil"
