from __future__ import annotations

from tests.support import Site, for_each_riwayah

QAD_TABAYYANA = Site(hafs=("2:256", (5, 6)))
IRKAB_MAANA = Site(hafs=("11:42", (14, 15)))


@for_each_riwayah(QAD_TABAYYANA, wasl=5, waqf=6)
def test_a_daal_merges_wholly_into_a_following_taa(r):
    # قَد تَّبَيَّنَ
    assert r.phonemes(5) == "qaˤ"
    assert r.phonemes(6) == "ttabajjan"


@for_each_riwayah(IRKAB_MAANA, wasl=14, waqf=15)
def test_a_baa_merges_wholly_into_a_following_meem(r):
    # ٱرْكَب مَّعَنَا
    assert r.phonemes(14) == "rˤka"
    assert r.phonemes(15) == "mmaʕana:"
