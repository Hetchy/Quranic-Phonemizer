from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUWA = Site(hafs=("2:29", (1,)))


@for_each_riwayah(HUWA, waqf=1)
def test_a_final_waw_becomes_the_length_of_the_vowel_before_it(r):
    # هُوَ
    assert r.phonemes(1) == "hu:"
