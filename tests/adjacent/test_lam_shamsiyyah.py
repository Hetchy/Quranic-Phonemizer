from __future__ import annotations

from tests.support import Site, for_each_riwayah

ARRAHMAN = Site(hafs=("1:1", (3,)))
ADDUNYA = Site(hafs=("2:85", (38,)))


@for_each_riwayah(ARRAHMAN, waqf=3)
def test_the_article_lam_merges_into_a_sun_letter(r):
    # ٱلرَّحْمَـٰنِ
    assert r.phonemes(3) == "rˤrˤaˤħma:n"
    assert r.silent(3) == {"ِ", "ٱ"}


@for_each_riwayah(ADDUNYA, waqf=38)
def test_the_same_merger_before_a_daal(r):
    # ٱلدُّنْيَا
    assert r.phonemes(38) == "ddunja:"
