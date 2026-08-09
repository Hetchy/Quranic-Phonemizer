from __future__ import annotations

from tests.support import Site, for_each_riwayah

BIMA = Site(hafs=("2:10", (10,)))
SAWAA = Site(hafs=("2:6", (4,)))
BIMA_UNZILA = Site(hafs=("2:4", (3, 4)))
ALIF_LAM_MEEM = Site(hafs=("2:1", (1,)))
ADHDHAKARAYN = Site(hafs=("6:143", (10,)))
YUNFIQUN = Site(hafs=("2:3", (8,)))
YAWMI = Site(hafs=("1:4", (2,)))
HAAULAA = Site(hafs=("2:31", (12,)))
AHAAULAA = Site(hafs=("34:40", (7,)))
YAAAYYUHA = Site(hafs=("4:1", (1,)))
HAAUM = Site(hafs=("69:19", (7,)))


@for_each_riwayah(BIMA, isolated=10)
def test_an_ordinary_long_vowel_needs_no_rule_to_be_long(r):
    # بِمَا
    assert r.phonemes(10) == "bima:"


@for_each_riwayah(SAWAA, isolated=4)
def test_a_long_vowel_before_a_hamza_in_the_same_word(r):
    # سَوَآءٌ
    assert r.phonemes(4) == "sawa:ʔ"


@for_each_riwayah(BIMA_UNZILA, ibtidaa=3, waqf=4)
def test_a_long_vowel_ending_a_word_before_a_hamza_opening_the_next(r):
    # بِمَآ أُنزِلَ
    assert r.phonemes(3) == "bima:"
    assert r.phonemes(4) == "ʔuŋzil"


@for_each_riwayah(ALIF_LAM_MEEM, isolated=1)
def test_a_long_vowel_before_a_quiescent_letter(r):
    # الٓمٓ
    assert r.phonemes(1) == "ʔalifla:m̃i:m"


@for_each_riwayah(ADHDHAKARAYN, isolated=10)
def test_the_same_length_after_an_interrogative_hamza(r):
    # ءَآلذَّكَرَيْنِ
    assert r.phonemes(10) == "ʔa:ððakarˤaˤjn"


@for_each_riwayah(YUNFIQUN, isolated=8)
def test_a_long_vowel_before_a_letter_the_stop_silences(r):
    # يُنفِقُونَ
    assert r.phonemes(8) == "juŋfiqu:n"
    assert r.silent(8) == {"َ"}


@for_each_riwayah(YAWMI, isolated=2)
def test_a_quiescent_waw_after_a_fatha_before_the_stopped_letter(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawm"


@for_each_riwayah(YAWMI, ibtidaa=2, wasl=2)
def test_the_same_waw_is_an_ordinary_glide_when_the_reading_joins(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawmi"


@for_each_riwayah(HAAULAA, wasl=12)
def test_a_particle_the_rasm_joined_holds_the_length_of_a_separation(r):
    # هَـٰٓؤُلَآءِ -- ها التنبيه and أولاء, one word written and two spoken,
    # so the word carries a separated madd and a joined one.
    assert r.phonemes(12) == "ha:ʔula:ʔi"
    assert r.rules_on_char(12, "ه") == {"madd_jaiz_munfasil"}
    assert r.rules_on_char(12, "ل") == {"madd_wajib_muttasil"}


@for_each_riwayah(AHAAULAA, wasl=7)
def test_an_interrogative_hamza_before_the_particle_moves_neither_madd(r):
    # أَهَـٰٓؤُلَآءِ -- the hamza stands before ها, not between ها and أولاء,
    # so the separation it does not touch reads as it does without it.
    assert r.phonemes(7) == "ʔaha:ʔula:ʔi"
    assert r.rules_on_char(7, "ه") == {"madd_jaiz_munfasil"}
    assert r.rules_on_char(7, "ل") == {"madd_wajib_muttasil"}


@for_each_riwayah(YAAAYYUHA, wasl=1)
def test_the_vocative_particle_is_separated_the_same_way(r):
    # يَـٰٓأَيُّهَا
    assert r.rules_on_char(1, "ي") == {"madd_jaiz_munfasil"}


@for_each_riwayah(HAAUM, wasl=7)
def test_the_same_shape_inside_one_lexeme_stays_joined(r):
    # هَآؤُمُ -- the imperative noun هاء, whose hamza is a third radical and
    # not a word standing behind a particle.
    assert r.phonemes(7) == "ha:ʔumu"
    assert r.rules_on_char(7, "ه") == {"madd_wajib_muttasil"}


@for_each_riwayah(YAAAYYUHA, wasl=1)
def test_a_joined_wasl_hamza_is_no_hamza_to_lengthen_for(r):
    # يَـٰٓأَيُّهَا ٱلنَّاسُ -- the hamza drops, so what the alif meets is the
    # sakin behind it and the length shortens instead of separating.
    assert r.phonemes(1) == "ja:ʔajjuha"
    assert r.rules_on_char(1, "ا") == {"iltiqa_repair"}
