from __future__ import annotations

from tests.support import Site, for_each_riwayah

QAWARIRA = Site(hafs=("76:15", (8,)))


@for_each_riwayah(QAWARIRA, waqf=8)
def test_an_alif_written_for_the_pause_is_long_when_stopped_on(r):
    # قَوَارِيرَا۠
    assert r.phonemes(8) == "qaˤwa:ri:rˤaˤ:"
