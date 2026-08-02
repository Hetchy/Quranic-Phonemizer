from __future__ import annotations

from tests.support import Site, for_each_riwayah

HUDAN_MIN = Site(hafs=("2:5", (3, 4)))


@for_each_riwayah(HUDAN_MIN, wasl=3, waqf=4)
def test_a_tanween_merges_into_the_meem_of_the_next_word(r):
    # هُدًى مِّن
    assert r.phonemes(3) == "huda"
    assert r.phonemes(4) == "m̃in"


@for_each_riwayah(HUDAN_MIN, waqf=3)
def test_the_same_tanween_lengthens_instead_when_stopped_on(r):
    # هُدًى
    assert r.phonemes(3) == "huda:"
    assert r.silent(3) == {"ً", "ى"}
