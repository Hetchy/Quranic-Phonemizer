from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALHAMDU = Site(hafs=("1:2", (1,)))


@for_each_riwayah(ALHAMDU, ibtidaa=1, waqf=1)
def test_a_qalqala_letter_the_stop_silences_is_echoed_more(r):
    # ٱلْحَمْدُ
    assert r.phonemes(1) == "ʔalħamdQ"
