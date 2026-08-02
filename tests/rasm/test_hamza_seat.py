from __future__ import annotations

from tests.support import Site, for_each_riwayah

WALULUAN = Site(hafs=("22:23", (19,)))


@for_each_riwayah(WALULUAN, waqf=19)
def test_the_letter_a_hamza_sits_on_spells_no_sound_of_its_own(r):
    # وَلُؤْلُؤًا
    assert r.phonemes(19) == "w̃aluʔluʔa:"
