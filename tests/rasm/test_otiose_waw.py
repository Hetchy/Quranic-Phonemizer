from __future__ import annotations

from tests.support import Site, for_each_riwayah

ULAIKA = Site(hafs=("2:5", (1,)))
WAULAIKA = Site(hafs=("2:5", (6,)))
ASSALAH = Site(hafs=("2:3", (5, 6)))
AZZAKAH = Site(hafs=("2:43", (4,)))
ALHAYAH = Site(hafs=("2:86", (4,)))
SALAWAT = Site(hafs=("2:157", (3,)))


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
