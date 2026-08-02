from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALIF_LAM_MEEM = Site(hafs=("2:1", (1,)))


@for_each_riwayah(ALIF_LAM_MEEM, waqf=1)
def test_a_long_vowel_before_a_quiescent_letter(r):
    # الٓمٓ
    assert r.phonemes(1) == "ʔalifla:m̃i:m"
