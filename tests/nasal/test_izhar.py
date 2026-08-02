from __future__ import annotations

from tests.support import Site, for_each_riwayah

ANAMTA = Site(hafs=("1:7", (3,)))
DUNYA = Site(hafs=("2:85", (38,)))


@for_each_riwayah(ANAMTA, waqf=3)
def test_a_quiescent_noon_before_a_throat_letter_stays_clear(r):
    # أَنْعَمْتَ
    assert r.phonemes(3) == "ʔanʕamt"


@for_each_riwayah(DUNYA, waqf=38)
def test_a_noon_before_a_glide_inside_one_word_stays_clear(r):
    # ٱلدُّنْيَا
    assert r.phonemes(38) == "ddunja:"
    assert r.silent(38) == {"ٱ"}
