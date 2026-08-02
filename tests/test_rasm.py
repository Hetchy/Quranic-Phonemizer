from __future__ import annotations

from tests.support import Site, for_each_riwayah

ULAIKA = Site(hafs=("2:5", (1,)))
WAULAIKA = Site(hafs=("2:5", (6,)))
ASSALAH = Site(hafs=("2:3", (5, 6)))
AZZAKAH = Site(hafs=("2:43", (4,)))
ALHAYAH = Site(hafs=("2:86", (4,)))
SALAWAT = Site(hafs=("2:157", (3,)))
KHALAQU = Site(hafs=("46:4", (10,)))
QALU = Site(hafs=("2:11", (8,)))
KHALAW = Site(hafs=("2:14", (8,)))
ISHTARAWU = Site(hafs=("2:16", (3,)))
MIATA = Site(hafs=("2:259", (19,)))
ARRIBA = Site(hafs=("2:275", (20,)))
BIAYDIN = Site(hafs=("51:47", (3,)))
AFAIN = Site(hafs=("3:144", (10,)))
WAMALAIHI = Site(hafs=("7:103", (9,)))
NABAI = Site(hafs=("6:34", (21,)))
WALULUAN = Site(hafs=("22:23", (19,)))
YUMINUN = Site(hafs=("2:3", (2,)))
YAKULUN = Site(hafs=("2:275", (2,)))
KHATIAH = Site(hafs=("96:16", (3,)))
LILMALAIKA = Site(hafs=("2:30", (4,)))
TAYASU = Site(hafs=("12:87", (8,)))
YAYASU = Site(hafs=("12:87", (13, 14)))
YAYASI = Site(hafs=("13:31", (20,)))


@for_each_riwayah(ULAIKA, isolated=1)
def test_a_waw_the_rasm_writes_and_recitation_never_says(r):
    # أُو۟لَـٰٓئِكَ
    assert r.phonemes(1) == "ʔula:ʔik"


@for_each_riwayah(WAULAIKA, isolated=6)
def test_the_same_silent_waw_behind_a_conjunction(r):
    # وَأُو۟لَـٰٓئِكَ
    assert r.phonemes(6) == "waʔula:ʔik"


@for_each_riwayah(ASSALAH, isolated=5)
def test_a_waw_carrying_a_dagger_alif_says_only_the_length(r):
    # ٱلصَّلَوٰةَ
    assert r.phonemes(5) == "ʔasˤsˤaˤla:h"
    assert r.silent(5) == {"َ"}


@for_each_riwayah(ASSALAH, ibtidaa=5, waqf=6)
def test_that_waw_stays_unsaid_when_the_word_is_joined_forward(r):
    # ٱلصَّلَوٰةَ وَمِمَّا
    assert r.phonemes(5) == "ʔasˤsˤaˤla:ta"
    assert r.phonemes(6) == "wamim̃a:"


@for_each_riwayah(AZZAKAH, isolated=4)
def test_the_same_spelling_in_the_word_for_alms(r):
    # ٱلزَّكَوٰةَ
    assert r.phonemes(4) == "ʔazzaka:h"


@for_each_riwayah(ALHAYAH, isolated=4)
def test_the_same_spelling_in_the_word_for_this_life(r):
    # ٱلْحَيَوٰةَ
    assert r.phonemes(4) == "ʔalħaja:h"


@for_each_riwayah(SALAWAT, isolated=3)
def test_a_waw_of_the_same_root_is_said_when_it_carries_a_fatha(r):
    # صَلَوَٰتٌ
    assert r.phonemes(3) == "sˤaˤlawa:t"


@for_each_riwayah(KHALAQU, isolated=10)
def test_the_alif_after_a_plural_waw_is_never_said(r):
    # خَلَقُوا۟
    assert r.phonemes(10) == "xaˤlaqu:"


@for_each_riwayah(QALU, isolated=8)
def test_the_same_alif_behind_a_plural_waw_that_carries_a_madd(r):
    # قَالُوٓا۟
    assert r.phonemes(8) == "qaˤ:lu:"


@for_each_riwayah(KHALAW, isolated=8)
def test_the_same_alif_behind_a_plural_waw_read_as_a_leen(r):
    # خَلَوْا۟
    assert r.phonemes(8) == "xaˤlaw"


@for_each_riwayah(ISHTARAWU, isolated=3)
def test_the_same_alif_behind_a_plural_waw_given_a_damma(r):
    # ٱشْتَرَوُا۟
    assert r.phonemes(3) == "ʔiʃtarˤaˤw"
    assert r.silent(3) == {"ا", "ُ", "۟"}


@for_each_riwayah(MIATA, isolated=19)
def test_an_alif_written_inside_a_word_and_never_said(r):
    # مِا۟ئَةَ
    assert r.phonemes(19) == "miʔah"


@for_each_riwayah(ARRIBA, isolated=20)
def test_a_final_alif_that_adds_nothing_to_a_length_already_written(r):
    # ٱلرِّبَوٰا۟
    assert r.phonemes(20) == "ʔarriba:"


@for_each_riwayah(BIAYDIN, isolated=3)
def test_a_second_yaa_the_rasm_writes_and_recitation_never_says(r):
    # بِأَيْي۟دٍ
    assert r.phonemes(3) == "biʔajdQ"


@for_each_riwayah(AFAIN, isolated=10)
def test_a_yaa_written_after_a_hamza_and_left_unsaid(r):
    # أَفَإِي۟ن
    assert r.phonemes(10) == "ʔafaʔin"


@for_each_riwayah(WAMALAIHI, isolated=9)
def test_the_same_silent_yaa_before_a_joined_pronoun(r):
    # وَمَلَإِي۟هِۦ
    assert r.phonemes(9) == "wamalaʔih"


@for_each_riwayah(NABAI, isolated=21)
def test_a_silent_yaa_at_the_end_of_a_word(r):
    # نَّبَإِى۟
    assert r.phonemes(21) == "nabaʔ"
    assert r.silent(21) == {"ى", "ِ", "۟"}


@for_each_riwayah(WALULUAN, isolated=19)
def test_the_letter_a_hamza_sits_on_spells_no_sound_of_its_own(r):
    # وَلُؤْلُؤًا
    assert r.phonemes(19) == "waluʔluʔa:"


@for_each_riwayah(YUMINUN, isolated=2)
def test_a_waw_seat_carries_a_quiescent_hamza_and_is_not_a_length(r):
    # يُؤْمِنُونَ
    assert r.phonemes(2) == "juʔminu:n"


@for_each_riwayah(YAKULUN, isolated=2)
def test_an_alif_seat_carries_a_quiescent_hamza_and_is_not_a_length(r):
    # يَأْكُلُونَ
    assert r.phonemes(2) == "jaʔkulu:n"


@for_each_riwayah(KHATIAH, isolated=3)
def test_a_dotless_yaa_seat_carries_a_hamza_with_a_fatha(r):
    # خَاطِئَةٍ
    assert r.phonemes(3) == "xaˤ:tˤiʔah"


@for_each_riwayah(LILMALAIKA, isolated=4)
def test_a_yaa_seat_after_a_length_adds_no_second_length(r):
    # لِلْمَلَـٰٓئِكَةِ
    assert r.phonemes(4) == "lilmala:ʔikah"


@for_each_riwayah(TAYASU, isolated=8)
def test_a_bare_alif_inside_a_leen_needs_neither_carrier_nor_hamza(r):
    # تَا۟يْـَٔسُوا۟
    assert r.phonemes(8) == "tajʔasu:"


@for_each_riwayah(YAYASU, ibtidaa=13, waqf=14)
def test_the_same_alif_in_the_third_person_of_that_verb(r):
    # لَا يَا۟يْـَٔسُ
    assert r.phonemes(13) == "la:"
    assert r.phonemes(14) == "jajʔas"


@for_each_riwayah(YAYASI, isolated=20)
def test_the_same_alif_where_the_verb_ends_in_a_kasra(r):
    # يَا۟يْـَٔسِ
    assert r.phonemes(20) == "jajʔas"
