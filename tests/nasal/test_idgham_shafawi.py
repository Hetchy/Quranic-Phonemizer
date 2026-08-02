from __future__ import annotations

from tests.support import Site, for_each_riwayah

QULUBIHIM_MARADUN = Site(hafs=("2:10", (2, 3)))


@for_each_riwayah(QULUBIHIM_MARADUN, wasl=2, waqf=3)
def test_a_quiescent_meem_merges_into_the_meem_of_the_next_word(r):
    # قُلُوبِهِم مَّرَضٌ
    assert r.phonemes(2) == "qulu:bihi"
    assert r.phonemes(3) == "m̃arˤaˤdˤ"
