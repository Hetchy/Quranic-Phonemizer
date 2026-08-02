from __future__ import annotations

from tests.support import Site, for_each_riwayah

ULAIKA = Site(hafs=("2:5", (1,)))


@for_each_riwayah(ULAIKA, waqf=1)
def test_a_waw_the_rasm_writes_and_recitation_never_says(r):
    # أُو۟لَـٰٓئِكَ
    assert r.phonemes(1) == "ʔula:ʔik"
