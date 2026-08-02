from __future__ import annotations

import pytest

from tests.support import (
    KhilafId,
    Option,
    Site,
    VariantSelection,
    for_each_riwayah,
    reading,
)

RAA = KhilafId.RAA_TAFKHEEM
NUCLEUS = KhilafId.NUCLEUS_VOWEL

SITES = [
    ("26:63", 11, "فiرقiن", "join",
     "firˤqiŋ", "firˤqQ", "firˤqiŋ", "firqiŋ"),
    ("34:12", 10, "ءaلقiطرi", "stop",
     "ʔalqitˤQri", "ʔalqitˤQr", "ʔalqitˤQrˤ", "ʔalqitˤQr"),
    ("12:99", 10, "مiصرa", "stop",
     "misˤrˤaˤ", "misˤrˤ", "misˤrˤ", "misˤr"),
    ("10:87", 8, "بiمiصرa", "stop",
     "bimisˤrˤaˤ", "bimisˤrˤ", "bimisˤrˤ", "bimisˤr"),
    ("54:16", 4, "وaنuذuرi", "stop",
     "wanuðuri", "wanuðurˤ", "wanuðurˤ", "wanuður"),
    ("54:23", 3, "بiءaلنuذuرi", "stop",
     "biñuðuri", "biñuðurˤ", "biñuðurˤ", "biñuður"),
    ("89:4", 3, "يaسرi", "stop",
     "jasri", "jasr", "jasrˤ", "jasr"),
    ("20:77", 6, "ءaسرi", "stop",
     "ʔasri", "ʔasr", "ʔasrˤ", "ʔasr"),
    ("11:81", 9, "فaءaسرi", "stop",
     "faʔasri", "faʔasr", "faʔasrˤ", "faʔasr"),
]

COLUMNS = ("ref", "word", "key", "disputed", "joined", "stopped",
           "heavy", "light")


def _read(ref, word, selection, stopped):
    site = Site(hafs=(ref, (word,)))
    plan = ({"isolated": word} if stopped
            else {"ibtidaa": word, "wasl": word})
    return reading(site, selection=selection, **plan).phonemes(word)


@pytest.mark.parametrize(COLUMNS, SITES)
def test_the_documented_default_is_taken(
    ref, word, key, disputed, joined, stopped, heavy, light
):
    plain = VariantSelection()
    assert _read(ref, word, plain, False) == joined
    assert _read(ref, word, plain, True) == stopped


@pytest.mark.parametrize(COLUMNS, SITES)
def test_both_wajh_are_reachable(
    ref, word, key, disputed, joined, stopped, heavy, light
):
    at_stop = disputed == "stop"
    picked = VariantSelection((Option(RAA, "heavy", key),))
    assert _read(ref, word, picked, at_stop) == heavy
    picked = VariantSelection((Option(RAA, "light", key),))
    assert _read(ref, word, picked, at_stop) == light


DUF = Site(hafs=("30:54", (5,)))


@for_each_riwayah(DUF, isolated=5)
def test_a_vowel_khilaf_is_settled_before_there_is_a_performance(r):
    # ضَعْفٍ
    assert r.phonemes(5) == "dˤaˤʕf"


def test_the_other_vowel_wajh_gives_the_other_word():
    # ضَعْفٍ
    picked = VariantSelection((Option(NUCLEUS, "damma", "ضعف"),))
    assert _read("30:54", 5, picked, True) == "dˤuʕf"
