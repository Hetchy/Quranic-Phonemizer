from __future__ import annotations

from tests.support import Site, for_each_riwayah

YUNFIQUN = Site(hafs=("2:3", (8,)))


@for_each_riwayah(YUNFIQUN, waqf=8)
def test_a_long_vowel_before_a_letter_the_stop_silences(r):
    # يُنفِقُونَ
    assert r.phonemes(8) == "juŋfiqu:n"
    assert r.silent(8) == {"َ"}
