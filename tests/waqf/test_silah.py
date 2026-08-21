from __future__ import annotations

from tests.support import Site, for_each_riwayah

LAHU = Site(hafs=("112:4", (3,)))
HAWLAHU = Site(hafs=("2:17", (9,)))
BIHI = Site(hafs=("2:26", (30,)))
BI_IDHNIHI = Site(hafs=("2:255", (26,)))
INDAHU = Site(hafs=("2:255", (24, 25)))
FIHI = Site(hafs=("2:20", (9,)))
ANNAHU = Site(hafs=("2:26", (16,)))
FIHI_SILAH = Site(hafs=("25:69", (7,)))


@for_each_riwayah(LAHU, ibtidaa=3, wasl=3)
def test_the_pronoun_haa_is_long_when_the_reading_carries_on(r):
    # لَّهُۥ
    assert r.phonemes(3) == "lahu:"
    assert r.silent(3) == frozenset()
    # the drawn-out haa names itself, and the plain madd how long it is held
    assert "madd_silah" in r.rules_on_char(3, "ۥ")
    assert r.rules_on_sound(3, "u:") == {"madd_silah", "madd_tabii"}


@for_each_riwayah(LAHU, isolated=3)
def test_the_same_haa_loses_its_length_at_a_stop(r):
    # لَّهُۥ
    assert r.phonemes(3) == "lah"
    assert r.silent(3) == {"ُ", "ۥ"}
    assert "madd_silah" not in r.rules_on_char(3, "ۥ")
    # the haa is left bare, so one rule takes the whole nucleus
    assert r.rules_on_char(3, "ۥ") == {"waqf_silah_drop"}


@for_each_riwayah(LAHU, isolated=3)
def test_the_stop_leaves_no_second_drop_on_the_haa(r):
    """The damma and the small waw spell one vowel between them, and the stop
    takes all of it, so there is no separate haraka left to drop."""
    # لَّهُۥ
    assert r.rules_on_char(3, "ُ") == {"waqf_silah_drop"}
    assert "waqf_diacritic_drop" not in r.rules_on_char(3, "ه")


@for_each_riwayah(HAWLAHU, ibtidaa=9, wasl=9)
def test_a_haa_with_damma_is_drawn_out_when_joined_forward(r):
    # حَوْلَهُۥ
    assert r.phonemes(9) == "ħawlahu:"
    assert r.silent(9) == frozenset()


@for_each_riwayah(HAWLAHU, isolated=9)
def test_that_damma_haa_is_bare_at_a_stop(r):
    # حَوْلَهُۥ
    assert r.phonemes(9) == "ħawlah"
    assert r.silent(9) == {"ُ", "ۥ"}


@for_each_riwayah(BIHI, ibtidaa=30, wasl=30)
def test_a_haa_with_kasra_is_drawn_out_when_joined_forward(r):
    # بِهِۦ
    assert r.phonemes(30) == "bihi:"
    assert r.silent(30) == frozenset()
    assert "madd_silah" in r.rules_on_char(30, "ۦ")
    assert r.rules_on_sound(30, "i:") == {"madd_silah", "madd_tabii"}


@for_each_riwayah(BIHI, isolated=30)
def test_that_kasra_haa_is_bare_at_a_stop(r):
    # بِهِۦ
    assert r.phonemes(30) == "bih"
    assert r.silent(30) == {"ِ", "ۦ"}


@for_each_riwayah(BI_IDHNIHI, ibtidaa=26, wasl=26)
def test_a_second_kasra_haa_is_drawn_out_when_joined_forward(r):
    # بِإِذْنِهِۦ
    assert r.phonemes(26) == "biʔiðnihi:"
    assert r.silent(26) == frozenset()


@for_each_riwayah(BI_IDHNIHI, isolated=26)
def test_that_second_kasra_haa_is_bare_at_a_stop(r):
    # بِإِذْنِهِۦ
    assert r.phonemes(26) == "biʔiðnih"
    assert r.silent(26) == {"ِ", "ۦ"}


@for_each_riwayah(FIHI, ibtidaa=9, wasl=9)
def test_a_haa_after_a_quiescent_letter_gets_no_length(r):
    # فِيهِ
    assert r.phonemes(9) == "fi:hi"
    assert r.silent(9) == frozenset()
    assert r.rules_on_char(9, "ه") == frozenset()


@for_each_riwayah(FIHI, isolated=9)
def test_that_haa_is_bare_at_a_stop_too(r):
    # فِيهِ
    assert r.phonemes(9) == "fi:h"
    assert r.silent(9) == {"ِ"}


@for_each_riwayah(ANNAHU, ibtidaa=16, wasl=16)
def test_a_haa_before_a_quiescent_letter_gets_no_length(r):
    # أَنَّهُ
    assert r.phonemes(16) == "ʔañahu"
    assert r.silent(16) == frozenset()
    assert r.rules_on_char(16, "ه") == frozenset()


@for_each_riwayah(ANNAHU, isolated=16)
def test_that_short_haa_is_bare_at_a_stop_as_well(r):
    # أَنَّهُ
    assert r.phonemes(16) == "ʔañah"
    assert r.silent(16) == {"ُ"}


@for_each_riwayah(INDAHU, ibtidaa=24, waqf=25)
def test_a_haa_before_a_word_opening_hamza_is_held_the_longer_count(r):
    """The silah is still the haa's own length; a hamza opening the next
    word says how long it is held, and no plain madd names it too."""
    # عِندَهُۥٓ إِلَّا
    assert r.phonemes(24) == "ʕiŋdahu:"
    assert r.rules_on_sound(24, "u:") == {"madd_silah", "madd_munfasil"}


@for_each_riwayah(FIHI_SILAH, isolated=7)
def test_the_haa_the_stop_leaves_bare_is_the_letter_a_madd_reads(r):
    """فِيهِۦ. The silah is gone at the stop, so the haa is quiescent and the
    long yaa before it is held for the stop's count."""
    assert r.phonemes(7) == "fi:h"
    assert r.rules_on_char(7, "ۦ") == {"waqf_silah_drop"}
    assert r.rules_on_sound(7, "i:") == {"madd_arid_lissukun"}
