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

SITES = [
    ("26:63", 11, "فiرقiن", "firˤqiŋ", "firˤqQ", "join"),
    ("34:12", 10, "ءaلقiطرi", "ʔalqitˤQri", "ʔalqitˤQr", "stop"),
    ("12:99", 10, "مiصرa", "misˤrˤaˤ", "misˤrˤ", "stop"),
    ("10:87", 8, "بiمiصرa", "bimisˤrˤaˤ", "bimisˤrˤ", "stop"),
    ("54:16", 4, "وaنuذuرi", "wanuðuri", "wanuðurˤ", "stop"),
    ("54:23", 3, "بiءaلنuذuرi", "biñuðuri", "biñuðurˤ", "stop"),
    ("89:4", 3, "يaسرi", "jasri", "jasr", "stop"),
    ("20:77", 6, "ءaسرi", "ʔasri", "ʔasr", "stop"),
    ("11:81", 9, "فaءaسرi", "faʔasri", "faʔasr", "stop"),
]


def _read(ref, word, selection, stopped):
    site = Site(hafs=(ref, (word,)))
    plan = ({"isolated": word} if stopped
            else {"ibtidaa": word, "wasl": word})
    return reading(site, selection=selection, **plan).phonemes(word)


@pytest.mark.parametrize(
    ("ref", "word", "key", "joined", "stopped", "disputed"), SITES
)
def test_the_documented_default_is_taken(
    ref, word, key, joined, stopped, disputed
):
    plain = VariantSelection()
    assert _read(ref, word, plain, False) == joined
    assert _read(ref, word, plain, True) == stopped


@pytest.mark.parametrize(
    ("ref", "word", "key", "joined", "stopped", "disputed"), SITES
)
def test_both_wajh_are_reachable(
    ref, word, key, joined, stopped, disputed
):
    heavy = VariantSelection((Option(RAA, "heavy", key),))
    light = VariantSelection((Option(RAA, "light", key),))
    at_stop = disputed == "stop"
    assert _read(ref, word, heavy, at_stop) != _read(ref, word, light, at_stop)


DUF = Site(hafs=("30:54", (5,)))


@for_each_riwayah(DUF, isolated=5)
def test_a_vowel_khilaf_is_settled_before_there_is_a_performance(r):
    # ضَعْفٍ
    assert r.phonemes(5)
