from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah

BIMA = Site(hafs=("2:10", (10,)))
SAWAA = Site(hafs=("2:6", (4,)))
BIMA_UNZILA = Site(hafs=("2:4", (3, 4)))
ALIF_LAM_MEEM = Site(hafs=("2:1", (1,)))
YUNFIQUN = Site(hafs=("2:3", (8,)))
YAWMI = Site(hafs=("1:4", (2,)))
HAAULAA = Site(hafs=("2:31", (12,)))
AHAAULAA = Site(hafs=("34:40", (7,)))
YAAAYYUHA = Site(hafs=("4:1", (1,)))
HAAUM = Site(hafs=("69:19", (7,)))
ADHEEMUN = Site(hafs=("2:7", (12,)))
QURAYSH = Site(hafs=("106:1", (2,)))
MUSAA = Site(hafs=("20:9", (4,)))
QAWLI = Site(hafs=("20:28", (2,)))
ADDAALLEEN = Site(hafs=("1:7", (9,)))
KAAHAYAAAINSAAD = Site(hafs=("19:1", (1,)))
MIHAADAN = Site(hafs=("78:6", (4,)))
AYNAN = Site(hafs=("2:60", (13,)))
WAANA = Site(hafs=("6:163", (6,)))
DAALLAN = Site(hafs=("93:7", (2,)))


@for_each_riwayah(BIMA, isolated=10)
def test_an_ordinary_long_vowel_takes_the_plain_length(r):
    # بِمَا
    assert r.phonemes(10) == "bima:"
    assert "madd_tabii" in r.rules_on_char(10, "ا")
    assert r.rules_on_sound(10, "a:") == {"madd_tabii"}


@for_each_riwayah(SAWAA, isolated=4)
def test_a_long_vowel_before_a_hamza_in_the_same_word(r):
    # سَوَآءٌ
    assert r.phonemes(4) == "sawa:ʔ"
    assert "madd_muttasil" in r.rules_on_char(4, "ا")
    assert r.rules_on_sound(4, "a:") == {"madd_muttasil"}


@for_each_riwayah(BIMA_UNZILA, ibtidaa=3, waqf=4)
def test_a_long_vowel_ending_a_word_before_a_hamza_opening_the_next(r):
    # بِمَآ أُنزِلَ
    assert r.phonemes(3) == "bima:"
    assert r.phonemes(4) == "ʔuŋzil"
    assert "madd_munfasil" in r.rules_on_char(3, "ا")
    assert r.rules_on_sound(3, "a:") == {"madd_munfasil"}


@for_each_riwayah(ALIF_LAM_MEEM, isolated=1)
def test_a_long_vowel_before_a_quiescent_letter(r):
    # الٓمٓ
    assert r.phonemes(1) == "ʔalifla:m̃i:m"
    assert "madd_lazim" in r.rules_on_char(1, "م")


@for_each_riwayah(YUNFIQUN, isolated=8)
def test_a_long_vowel_before_a_letter_the_stop_silences(r):
    # يُنفِقُونَ
    assert r.phonemes(8) == "juŋfiqu:n"
    assert r.silent(8) == {"َ"}
    assert "madd_arid_lissukun" in r.rules_on_char(8, "و")
    assert "madd_arid_lissukun" in r.rules_on_sound(8, "u:")


@for_each_riwayah(YAWMI, isolated=2)
def test_a_quiescent_waw_after_a_fatha_before_the_stopped_letter(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawm"
    assert "madd_leen" in r.rules_on_char(2, "و")
    assert r.rules_on_sound(2, "w") == {"madd_leen"}


@for_each_riwayah(YAWMI, ibtidaa=2, wasl=2)
def test_the_same_waw_is_an_ordinary_glide_when_the_reading_joins(r):
    # يَوْمِ
    assert r.phonemes(2) == "jawmi"
    assert r.rules_on_char(2, "و") == frozenset()


@for_each_riwayah(HAAULAA, wasl=12)
def test_a_particle_the_rasm_joined_holds_the_length_of_a_separation(r):
    # هَـٰٓؤُلَآءِ -- ها التنبيه and أولاء, one word written and two spoken,
    # so the word carries a separated madd and a joined one.
    assert r.phonemes(12) == "ha:ʔula:ʔi"
    assert r.rules_on_char(12, "ه") == {"madd_munfasil"}
    assert r.rules_on_char(12, "ل") == {"madd_muttasil"}


@for_each_riwayah(AHAAULAA, wasl=7)
def test_an_interrogative_hamza_before_the_particle_moves_neither_madd(r):
    # أَهَـٰٓؤُلَآءِ -- the hamza stands before ها, not between ها and أولاء,
    # so the separation it does not touch reads as it does without it.
    assert r.phonemes(7) == "ʔaha:ʔula:ʔi"
    assert r.rules_on_char(7, "ه") == {"madd_munfasil"}
    assert r.rules_on_char(7, "ل") == {"madd_muttasil"}


@for_each_riwayah(YAAAYYUHA, wasl=1)
def test_the_vocative_particle_is_separated_the_same_way(r):
    # يَـٰٓأَيُّهَا
    assert r.rules_on_char(1, "ي") == {"madd_munfasil"}


@for_each_riwayah(HAAUM, wasl=7)
def test_the_same_shape_inside_one_lexeme_stays_joined(r):
    # هَآؤُمُ -- the imperative noun هاء, whose hamza is a third radical and
    # not a word standing behind a particle.
    assert r.phonemes(7) == "ha:ʔumu"
    assert r.rules_on_char(7, "ه") == {"madd_muttasil"}


@for_each_riwayah(YAAAYYUHA, wasl=1)
def test_a_joined_wasl_hamza_is_no_hamza_to_lengthen_for(r):
    # يَـٰٓأَيُّهَا ٱلنَّاسُ -- the hamza drops, so what the alif meets is the
    # sakin behind it and the length shortens instead of separating.
    assert r.phonemes(1) == "ja:ʔajjuha"
    assert r.rules_on_char(1, "ا") == {"iltiqa_shortening"}


@for_each_riwayah(ADHEEMUN, isolated=12)
def test_a_tanween_noon_is_not_the_letter_the_stop_lands_on(r):
    # عَظِيمٌ -- the stop drops the tanween and stops on the meem, so the
    # long vowel before it meets a sukun the reading made.
    assert r.phonemes(12) == "ʕaðˤi:m"
    assert "madd_arid_lissukun" in r.rules_on_char(12, "ي")


@for_each_riwayah(QURAYSH, isolated=2)
def test_a_leen_is_read_past_the_tanween_the_same_way(r):
    # قُرَيْشٍ
    assert r.phonemes(2) == "qurˤaˤjʃ"
    assert r.rules_on_char(2, "ي") == {"madd_leen"}


@for_each_riwayah(MUSAA, isolated=4)
def test_a_word_ending_long_silences_nothing_for_a_madd_to_lengthen_on(r):
    # مُوسَىٰٓ -- the stop cannot strip a long vowel, so the `u:` before it
    # meets no sukun and stays plain.
    assert r.phonemes(4) == "mu:sa:"
    assert r.rules_on_char(4, "و") == {"madd_tabii"}


@for_each_riwayah(QAWLI, isolated=2)
def test_a_leen_needs_the_same_silencing_and_does_not_get_it(r):
    # قَوْلِى -- ends on a long `i:`, so the waw is an ordinary diphthong.
    assert r.phonemes(2) == "qaˤwli:"
    assert r.rules_on_char(2, "و") == frozenset()


@for_each_riwayah(ADDAALLEEN, isolated=9)
def test_a_long_vowel_before_a_doubled_letter_is_lazim(r):
    """ٱلضَّآلِّينَ. A geminate is a sakin and a voweled letter, so the madd
    before it meets a sukun the Score holds permanently."""
    assert r.phonemes(9) == "ʔadˤdˤaˤ:lli:n"
    assert "madd_lazim" in r.rules_on_char(9, "ا")
    assert "madd_arid_lissukun" in r.rules_on_char(9, "ي")


@for_each_riwayah(KAAHAYAAAINSAAD, isolated=1)
def test_a_leen_before_a_permanent_sakin_is_lazim_and_not_leen(r):
    """كٓهيعٓصٓ. The ain spells out as a leen before a sakin the Score holds
    for good, so no stop is needed to make the length obligatory."""
    assert r.phonemes(1) == "ka:fha:ja:ʕajŋsˤaˤ:dQ"
    assert "madd_lazim" in r.rules_on_char(1, "ع")
    assert "madd_leen" not in r.rules_on_char(1, "ع")


@for_each_riwayah(MIHAADAN, isolated=4)
def test_a_tanween_fath_lengthens_at_the_stop_and_silences_nothing(r):
    """مِهَـٰدًا. The stop turns the tanween into the iwad alif, so the letter
    it lands on is never quiescent and the madd before it stays plain."""
    assert r.phonemes(4) == "miha:da:"
    assert "madd_tabii" in r.rules_on_char(4, "ٰ")
    assert "madd_arid_lissukun" not in r.rules_on_char(4, "ٰ")


@for_each_riwayah(AYNAN, isolated=13)
def test_a_leen_before_a_tanween_fath_is_no_leen_either(r):
    # عَيْنًا -- the noon carries the iwad, so the yaa meets no sukun.
    assert r.rules_on_char(13, "ي") == frozenset()


@for_each_riwayah(WAANA, wasl=6)
def test_a_pausal_alif_joined_is_short_and_separates_nothing(r):
    """وَأَنَا۠ أَوَّلُ. Joined, the alif's own vowel is canonically short, so
    the hamza opening the next word has no length to separate."""
    assert r.phonemes(6) == "waʔana"
    assert "madd_munfasil" not in r.rules_on_char(6, "ا")


@for_each_riwayah(DAALLAN, isolated=2)
def test_a_geminate_the_iwad_vowels_still_holds_the_madd_before_it(r):
    """ضَآلًّا. The stop exchanges the fathatan for a long aa on the lam, and
    the first half of the shadda stands under it, so the madd stays lazim."""
    assert r.phonemes(2) == "dˤaˤ:lla:"
    assert r.rules_on_sound(2, "aˤ:") == {"madd_lazim", "tafkheem"}
