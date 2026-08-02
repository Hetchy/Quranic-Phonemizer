from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUDAN = Site(hafs=("2:5", (3,)))


@for_each_riwayah(HUDAN, waqf=3)
def test_a_fathatan_lengthens_the_letter_before_it_at_a_stop(r):
    # هُدًى
    assert r.phonemes(3) == "huda:"
    assert r.silent(3) == {"ً", "ى"}
