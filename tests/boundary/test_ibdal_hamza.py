from __future__ import annotations

from tests.support import Site, for_each_riwayah

ITUNI = Site(hafs=("46:4", (18,)))


@for_each_riwayah(ITUNI, ibtidaa=18, waqf=18)
def test_a_quiescent_hamza_becomes_a_length_when_started_on(r):
    # ٱئْتُونِى
    assert r.phonemes(18) == "ʔi:tu:ni:"
