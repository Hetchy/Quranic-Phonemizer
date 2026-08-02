from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

ATHQALAT_DAAWA = Site(hafs=("7:189", (20, 21)))
QAD_TABAYYANA = Site(hafs=("2:256", (5, 6)))

ACROSS_A_BOUNDARY = [
    ("2:256", (5, 6), ("qaˤ", "ttabajjan")),        # قَد تَّبَيَّنَ
    ("3:69", (1, 2), ("wadda", "tˤtˤaˤ:ʔifah")),    # وَدَّت طَّآئِفَةٌ
    ("4:64", (11, 12), ("ʔi", "ðˤðˤaˤlamu:")),      # إِذ ظَّلَمُوٓا۟
    ("11:42", (14, 15), ("ʔirˤka", "mmaʕana:")),    # ٱرْكَب مَّعَنَا
    ("7:176", (20, 21), ("jalha", "ðða:lik")),      # يَلْهَث ذَّٰلِكَ
]

INSIDE_ONE_WORD = [
    ("2:233", 45, "ʔarˤaˤttum"),                    # أَرَدتُّمْ
    ("12:32", 7, "rˤaˤ:wattuh"),                    # رَٰوَدتُّهُۥ
    ("5:110", 13, "ʔajjattuk"),                     # أَيَّدتُّكَ
    ("12:51", 5, "rˤaˤ:wattuñ"),                    # رَٰوَدتُّنَّ
]


@pytest.mark.parametrize(("ref", "words", "expected"), ACROSS_A_BOUNDARY)
def test_a_letter_merges_wholly_into_its_neighbour_of_the_same_family(
    ref, words, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected


@pytest.mark.parametrize(("ref", "word", "expected"), INSIDE_ONE_WORD)
def test_a_daal_merges_wholly_into_a_taa_inside_one_word(ref, word, expected):
    r = reading(Site(hafs=(ref, (word,))), isolated=word)
    assert r.phonemes(word) == expected


@for_each_riwayah(QAD_TABAYYANA, isolated=5)
def test_a_stop_after_the_daal_undoes_the_merger_into_the_taa(r):
    # قَد
    assert r.phonemes(5) == "qaˤdQ"


@pytest.mark.engine_bug
@for_each_riwayah(ATHQALAT_DAAWA, ibtidaa=20, waqf=21)
def test_a_quiescent_taa_merges_wholly_into_a_following_daal(r):
    # أَثْقَلَت دَّعَوَا
    # the engine sounds the taa and leaves the daal single
    assert r.phonemes(20) == "ʔaθqaˤla"
    assert r.phonemes(21) == "ddaʕawa:"
