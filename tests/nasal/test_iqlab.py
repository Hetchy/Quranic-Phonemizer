from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALIMUN_BIMA = Site(hafs=("2:10", (9, 10)))


@for_each_riwayah(ALIMUN_BIMA, wasl=9, waqf=10)
def test_a_tanween_before_a_baa_turns_into_a_nasal(r):
    # أَلِيمٌ بِمَا
    assert r.phonemes(9) == "ʔali:muŋ"
    assert r.phonemes(10) == "bima:"


@for_each_riwayah(ALIMUN_BIMA, waqf=(9, 10))
def test_the_same_tanween_does_not_turn_when_stopped_on(r):
    # أَلِيمٌ
    assert r.phonemes(9) == "ʔali:m"
    assert r.silent(9) == {"ٌ"}
