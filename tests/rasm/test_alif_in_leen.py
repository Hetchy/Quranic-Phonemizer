from __future__ import annotations

from tests.support import Site, for_each_riwayah

TAYASU = Site(hafs=("12:87", (8,)))


@for_each_riwayah(TAYASU, waqf=8)
def test_a_bare_alif_inside_a_leen_needs_neither_carrier_nor_hamza(r):
    # تَا۟يْـَٔسُوا۟
    assert r.phonemes(8) == "tajʔasu:"
