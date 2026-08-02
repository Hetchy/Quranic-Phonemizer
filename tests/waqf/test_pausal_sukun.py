from __future__ import annotations

from tests.support import Site, for_each_riwayah

DHALIKA = Site(hafs=("2:2", (1,)))


@for_each_riwayah(DHALIKA, waqf=1)
def test_a_final_short_vowel_is_dropped_at_a_stop(r):
    # ذَٰلِكَ
    assert r.phonemes(1) == "ða:lik"
    assert r.silent(1) == {"َ"}
