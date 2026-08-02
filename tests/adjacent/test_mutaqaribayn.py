from __future__ import annotations

from tests.support import Site, for_each_riwayah

WAQUL_RABBI = Site(hafs=("23:118", (1, 2)))
NAKHLUQKUM = Site(hafs=("77:20", (2,)))


@for_each_riwayah(WAQUL_RABBI, wasl=1, waqf=2)
def test_a_quiescent_lam_merges_into_a_following_raa(r):
    # وَقُل رَّبِّ
    assert r.phonemes(1) == "waqu"
    assert r.phonemes(2) == "rˤrˤaˤbbQ"


@for_each_riwayah(NAKHLUQKUM, waqf=2)
def test_a_quiescent_qaaf_merges_into_a_kaaf_inside_one_word(r):
    # نَخْلُقكُّم
    assert r.phonemes(2) == "naxlukkum"
