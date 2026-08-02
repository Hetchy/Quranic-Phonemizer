from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALHAMDU = Site(hafs=("1:2", (1,)))


@for_each_riwayah(ALHAMDU, ibtidaa=1, waqf=1)
def test_the_article_lam_is_said_before_a_moon_letter(r):
    # ٱلْحَمْدُ
    assert r.phonemes(1) == "ʔalħamdQ"
