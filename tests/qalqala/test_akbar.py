from __future__ import annotations

from tests.support import Site, for_each_riwayah

RABBI = Site(hafs=("23:118", (2,)))


@for_each_riwayah(RABBI, waqf=2)
def test_a_doubled_qalqala_letter_at_a_stop_is_echoed_most(r):
    # رَّبِّ
    assert r.phonemes(2) == "rˤrˤaˤbbQ"
