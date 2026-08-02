from __future__ import annotations

from tests.support import Site, for_each_riwayah

KHALAQU = Site(hafs=("46:4", (10,)))


@for_each_riwayah(KHALAQU, waqf=10)
def test_the_alif_after_a_plural_waw_is_never_said(r):
    # خَلَقُوا۟
    assert r.phonemes(10) == "xaˤlaqu:"
