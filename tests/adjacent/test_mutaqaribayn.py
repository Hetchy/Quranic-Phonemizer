from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

NAKHLUQKUM = Site(hafs=("77:20", (2,)))
WAQUL_RABBI = Site(hafs=("23:118", (1, 2)))

A_LAM_BEFORE_A_RAA = [
    ("23:118", (1, 2), ("waqu", "rˤrˤaˤbbQ")),      # وَقُل رَّبِّ
    ("4:158", (1, 2), ("ba", "rˤrˤaˤfaʕah")),       # بَل رَّفَعَهُ
]


@pytest.mark.parametrize(("ref", "words", "expected"), A_LAM_BEFORE_A_RAA)
def test_a_quiescent_lam_merges_into_a_following_raa(ref, words, expected):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected


@for_each_riwayah(NAKHLUQKUM, isolated=2)
def test_a_quiescent_qaaf_merges_into_a_kaaf_inside_one_word(r):
    # نَخْلُقكُّم
    assert r.phonemes(2) == "naxlukkum"


@for_each_riwayah(WAQUL_RABBI, isolated=1)
def test_a_stop_after_the_lam_undoes_the_merger_into_the_raa(r):
    # وَقُل
    assert r.phonemes(1) == "waqul"
