from __future__ import annotations

from tests.support import Site, for_each_riwayah

ULAIKA = Site(hafs=("2:5", (1,)))


@for_each_riwayah(ULAIKA, waqf=1)
def test_a_long_vowel_before_a_hamza_in_the_same_word(r):
    # أُو۟لَـٰٓئِكَ
    assert r.phonemes(1) == "ʔula:ʔik"
