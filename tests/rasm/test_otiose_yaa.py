from __future__ import annotations

from tests.support import Site, for_each_riwayah

BIAYDIN = Site(hafs=("51:47", (3,)))
AFAIN = Site(hafs=("3:144", (10,)))
WAMALAIHI = Site(hafs=("7:103", (9,)))
NABAI = Site(hafs=("6:34", (21,)))


@for_each_riwayah(BIAYDIN, ibtidaa=3, waqf=3)
def test_a_second_yaa_the_rasm_writes_and_recitation_never_says(r):
    # بِأَيْي۟دٍ
    assert r.phonemes(3) == "biʔajdQ"


@for_each_riwayah(AFAIN, ibtidaa=10, waqf=10)
def test_a_yaa_written_after_a_hamza_and_left_unsaid(r):
    # أَفَإِي۟ن
    assert r.phonemes(10) == "ʔafaʔin"


@for_each_riwayah(WAMALAIHI, ibtidaa=9, waqf=9)
def test_the_same_silent_yaa_before_a_joined_pronoun(r):
    # وَمَلَإِي۟هِۦ
    assert r.phonemes(9) == "wamalaʔih"


@for_each_riwayah(NABAI, ibtidaa=21, waqf=21)
def test_a_silent_yaa_at_the_end_of_a_word(r):
    # نَّبَإِى۟
    assert r.phonemes(21) == "nabaʔ"
    assert r.silent(21) == {"ى", "ِ", "۟"}
