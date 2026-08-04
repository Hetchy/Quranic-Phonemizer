from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

ATHQALAT_DAAWA = Site(hafs=("7:189", (20, 21)))
QAD_TABAYYANA = Site(hafs=("2:256", (5, 6)))

ACROSS_A_BOUNDARY = [
    ("2:256", (5, 6), "د", ("qaˤ", "ttabajjan")),        # قَد تَّبَيَّنَ
    ("3:69", (1, 2), "ت", ("wadda", "tˤtˤaˤ:ʔifah")),    # وَدَّت طَّآئِفَةٌ
    ("4:64", (11, 12), "ذ", ("ʔi", "ðˤðˤaˤlamu:")),      # إِذ ظَّلَمُوٓا۟
    ("7:176", (20, 21), "ث", ("jalha", "ðða:lik")),      # يَلْهَث ذَّٰلِكَ
]

INSIDE_ONE_WORD = [
    ("2:233", 45, "ʔarˤaˤttum"),                    # أَرَدتُّمْ
    ("12:32", 7, "rˤaˤ:wattuh"),                    # رَٰوَدتُّهُۥ
    ("5:110", 13, "ʔajjattuk"),                     # أَيَّدتُّكَ
    ("12:51", 5, "rˤaˤ:wattuñ"),                    # رَٰوَدتُّنَّ
]


@pytest.mark.parametrize(
    ("ref", "words", "letter", "expected"), ACROSS_A_BOUNDARY
)
def test_a_letter_merges_wholly_into_its_neighbour_of_the_same_family(
    ref, words, letter, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected
    assert "idgham_mutajanisayn_kamil" in r.rules_on_char(first, letter)
    merged = r.sounds(last)[0]
    assert "idgham_mutajanisayn_kamil" in r.rules_on_sound(last, merged)


@pytest.mark.parametrize(("ref", "word", "expected"), INSIDE_ONE_WORD)
def test_a_daal_merges_wholly_into_a_taa_inside_one_word(ref, word, expected):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == expected
    assert "idgham_mutajanisayn_kamil" in r.rules_on_char(word, "د")
    assert "idgham_mutajanisayn_kamil" in r.rules_on_sound(word, "tt")


@for_each_riwayah(QAD_TABAYYANA, isolated=5)
def test_a_stop_after_the_daal_undoes_the_merger_into_the_taa(r):
    # قَد
    assert r.phonemes(5) == "qaˤdQ"
    assert "idgham_mutajanisayn_kamil" not in r.rules_on_char(5, "د")


@for_each_riwayah(ATHQALAT_DAAWA, ibtidaa=20, waqf=21)
def test_a_quiescent_taa_merges_wholly_into_a_following_daal(r):
    # أَثْقَلَت دَّعَوَا
    # the engine sounds the taa and leaves the daal single
    assert r.phonemes(20) == "ʔaθqaˤla"
    assert r.phonemes(21) == "ddaʕawa:"
    assert "idgham_mutajanisayn_kamil" in r.rules_on_char(20, "ت")
    assert "idgham_mutajanisayn_kamil" in r.rules_on_sound(21, "dd")


IRKAB_MAANA = Site(hafs=("11:42", (14, 15)))


@for_each_riwayah(IRKAB_MAANA, ibtidaa=14, waqf=15)
def test_a_baa_merged_into_a_meem_is_held_on_its_ghunnah(r):
    # ٱرْكَب مَّعَنَا
    # the engine doubles the meem plainly instead of nasalising it
    assert r.phonemes(14) == "ʔirˤka"
    assert r.phonemes(15) == "m̃aʕana:"
    assert "idgham_mutajanisayn_kamil" in r.rules_on_char(14, "ب")
    assert "idgham_mutajanisayn_kamil" in r.rules_on_sound(15, "m̃")
