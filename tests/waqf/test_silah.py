from __future__ import annotations

from tests.support import Site, for_each_riwayah

LAHU = Site(hafs=("112:4", (3,)))


@for_each_riwayah(LAHU, wasl=3)
def test_the_pronoun_haa_is_long_when_the_reading_carries_on(r):
    # لَّهُۥ
    assert r.phonemes(3) == "llahu:"


@for_each_riwayah(LAHU, waqf=3)
def test_the_same_haa_loses_its_length_at_a_stop(r):
    # لَّهُۥ
    assert r.phonemes(3) == "llah"
    assert r.silent(3) == {"ُ", "ۥ"}
