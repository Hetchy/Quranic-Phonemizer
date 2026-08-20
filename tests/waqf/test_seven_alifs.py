from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

QAWARIRA = Site(hafs=("76:15", (8,)))
QAWARIRA_SECOND = Site(hafs=("76:16", (1,)))
SALASILA = Site(hafs=("76:4", (4,)))
DHUNUNA = Site(hafs=("33:10", (16,)))
RASULA = Site(hafs=("33:66", (11,)))
SABILA = Site(hafs=("33:67", (8,)))
ANA = Site(hafs=("2:258", (21,)))
ANA_AGAIN = Site(hafs=("18:39", (15,)))
LAKINNA = Site(hafs=("18:38", (1,)))

#: Written with the mark that is sounded at a stop and silent when joined.
SOUNDED_AT_A_STOP = [
    (QAWARIRA, 8, "qaˤwa:ri:rˤaˤ:", "qaˤwa:ri:rˤaˤ"),   # قَوَارِيرَا۠
    (DHUNUNA, 16, "ʔaðˤðˤunu:na:", "ʔaðˤðˤunu:na"),     # ٱلظُّنُونَا۠
    (RASULA, 11, "ʔarˤrˤaˤsu:la:", "ʔarˤrˤaˤsu:la"),    # ٱلرَّسُولَا۠
    (SABILA, 8, "ʔassabi:la:", "ʔassabi:la"),           # ٱلسَّبِيلَا۠
    (ANA, 21, "ʔana:", "ʔana"),                         # أَنَا۠
    (ANA_AGAIN, 15, "ʔana:", "ʔana"),                   # أَنَا۠
    (LAKINNA, 1, "la:kiña:", "la:kiña"),                # لَّـٰكِنَّا۠
]


@pytest.mark.parametrize(("site", "word", "stopped", "joined"),
                         SOUNDED_AT_A_STOP)
def test_each_pausal_alif_is_sounded_when_it_is_stopped_on(
    site, word, stopped, joined
):
    r = reading(site, isolated=word)
    assert r.phonemes(word) == stopped
    # stopped on, this rule says the alif and the natural madd holds it
    assert "pausal_alif" in r.rules_on_char(word, "۠")
    assert "madd_tabii" in r.rules_on_char(word, "۠")
    # the alif is sounded, so the stop drops nothing here
    assert "waqf_diacritic_drop" not in r.rules_on_char(word, "۠")
    assert r.silent(word) == frozenset()


@pytest.mark.parametrize(("site", "word", "stopped", "joined"),
                         SOUNDED_AT_A_STOP)
def test_each_pausal_alif_falls_silent_when_the_reading_carries_on(
    site, word, stopped, joined
):
    r = reading(site, ibtidaa=word, wasl=word)
    assert r.phonemes(word) == joined
    assert "pausal_alif" in r.rules_on_char(word, "۠")


@for_each_riwayah(QAWARIRA_SECOND, ibtidaa=1, wasl=1)
def test_the_round_zero_keeps_a_short_fatha_when_joined_forward(r):
    # قَوَارِيرَا۟
    assert r.phonemes(1) == "qaˤwa:ri:rˤaˤ"
    assert r.silent(1) == frozenset()
    # the round zero is not one of the seven; the rule never reaches it
    assert "pausal_alif" not in r.rules_on_char(1, "۟")


@for_each_riwayah(QAWARIRA_SECOND, isolated=1)
def test_the_round_zero_drops_its_alif_at_a_stop(r):
    # قَوَارِيرَا۟
    assert r.phonemes(1) == "qaˤwa:ri:r"
    assert r.silent(1) == {"َ", "ا", "۟"}


@for_each_riwayah(SALASILA, ibtidaa=4, wasl=4)
def test_salasila_keeps_a_short_fatha_when_the_reading_carries_on(r):
    # سَلَـٰسِلَا۟
    assert r.phonemes(4) == "sala:sila"
    assert r.silent(4) == frozenset()


@for_each_riwayah(SALASILA, isolated=4)
def test_salasila_is_stopped_on_without_sounding_its_alif(r):
    # سَلَـٰسِلَا۟
    assert r.phonemes(4) == "sala:sil"
    assert r.silent(4) == {"َ", "ا", "۟"}
