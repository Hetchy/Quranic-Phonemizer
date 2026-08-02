from __future__ import annotations

from tests.support import Site, for_each_riwayah

WALA_DDALLIN = Site(hafs=("1:7", (8, 9)))


@for_each_riwayah(WALA_DDALLIN, wasl=8, waqf=9)
def test_a_long_vowel_shortens_before_a_quiescent_letter(r):
    # وَلَا ٱلضَّآلِّينَ
    assert r.phonemes(8) == "wala"
    assert r.phonemes(9) == "dˤdˤaˤ:lli:n"
