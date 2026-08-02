from __future__ import annotations

from tests.support import Site, for_each_riwayah

ALHAMDU = Site(hafs=("1:2", (1,)))
ALLAHU = Site(hafs=("2:15", (1,)))


@for_each_riwayah(ALHAMDU, ibtidaa=1, waqf=1)
def test_a_prosthetic_hamza_is_sounded_when_the_reading_starts_on_it(r):
    # ٱلْحَمْدُ
    assert r.phonemes(1) == "ʔalħamdQ"


@for_each_riwayah(ALLAHU, ibtidaa=1, waqf=1)
def test_the_helping_vowel_is_a_fatha_before_the_divine_name(r):
    # ٱللَّهُ
    assert r.phonemes(1) == "ʔalˤlˤaˤ:h"
