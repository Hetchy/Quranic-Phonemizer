from __future__ import annotations

import pytest

from tests.support import Site, reading

A_TAH_BEFORE_A_TAA = [
    ("5:28", 2, "basatˤt"),              # بَسَطتَ
    ("27:22", 5, "ʔaħatˤt"),             # أَحَطتُ
    ("12:80", 21, "farˤrˤaˤtˤtum"),      # فَرَّطتُمْ
    ("39:56", 7, "farˤrˤaˤtˤt"),         # فَرَّطتُ
]


@pytest.mark.parametrize(("ref", "word", "expected"), A_TAH_BEFORE_A_TAA)
def test_a_taa_takes_the_place_of_the_tah_but_not_its_heaviness(
    ref, word, expected
):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == expected
    assert "idgham_mutajanisayn_naqis" in r.rules_on_char(word, "ط")
    assert "idgham_mutajanisayn_naqis" in r.rules_on_sound(word, "tˤ")
