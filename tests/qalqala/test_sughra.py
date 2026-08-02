from __future__ import annotations

from tests.support import Site, for_each_riwayah

ATAMAHUM = Site(hafs=("106:4", (2,)))


@for_each_riwayah(ATAMAHUM, waqf=2)
def test_a_qalqala_letter_quiescent_inside_a_word_is_echoed_lightly(r):
    # أَطْعَمَهُم
    assert r.phonemes(2) == "ʔatˤQʕamahum"
