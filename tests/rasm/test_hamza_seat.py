from __future__ import annotations

from tests.support import Site, for_each_riwayah

WALULUAN = Site(hafs=("22:23", (19,)))
YUMINUN = Site(hafs=("2:3", (2,)))
YAKULUN = Site(hafs=("2:275", (2,)))
KHATIAH = Site(hafs=("96:16", (3,)))
LILMALAIKA = Site(hafs=("2:30", (4,)))


@for_each_riwayah(WALULUAN, ibtidaa=19, waqf=19)
def test_the_letter_a_hamza_sits_on_spells_no_sound_of_its_own(r):
    # وَلُؤْلُؤًا
    assert r.phonemes(19) == "waluʔluʔa:"


@for_each_riwayah(YUMINUN, ibtidaa=2, waqf=2)
def test_a_waw_seat_carries_a_quiescent_hamza_and_is_not_a_length(r):
    # يُؤْمِنُونَ
    assert r.phonemes(2) == "juʔminu:n"


@for_each_riwayah(YAKULUN, ibtidaa=2, waqf=2)
def test_an_alif_seat_carries_a_quiescent_hamza_and_is_not_a_length(r):
    # يَأْكُلُونَ
    assert r.phonemes(2) == "jaʔkulu:n"


@for_each_riwayah(KHATIAH, ibtidaa=3, waqf=3)
def test_a_dotless_yaa_seat_carries_a_hamza_with_a_fatha(r):
    # خَاطِئَةٍ
    assert r.phonemes(3) == "xaˤ:tˤiʔah"


@for_each_riwayah(LILMALAIKA, ibtidaa=4, waqf=4)
def test_a_yaa_seat_after_a_length_adds_no_second_length(r):
    # لِلْمَلَـٰٓئِكَةِ
    assert r.phonemes(4) == "lilmala:ʔikah"
