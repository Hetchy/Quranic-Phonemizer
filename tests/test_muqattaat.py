from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

OPENINGS = {
    "2:1": "ʔalifla:m̃i:m",              # الٓمٓ
    "7:1": "ʔalifla:m̃i:msˤaˤ:dQ",       # الٓمٓصٓ
    "10:1": "ʔalifla:mrˤaˤ:",            # الٓر
    "13:1": "ʔalifla:m̃i:mrˤaˤ:",        # الٓمٓر
    "19:1": "ka:fha:ja:ʕajŋsˤaˤ:dQ",     # كٓهيعٓصٓ
    "20:1": "tˤaˤ:ha:",                  # طه
    "26:1": "tˤaˤ:si:m̃i:m",             # طسٓمٓ
    "27:1": "tˤaˤ:si:n",                 # طسٓ
    "36:1": "ja:si:n",                   # يسٓ
    "38:1": "sˤaˤ:dQ",                   # صٓ
    "40:1": "ħa:mi:m",                   # حمٓ
    "42:2": "ʕajŋsi:ŋqaˤ:f",             # عٓسٓقٓ
    "50:1": "qaˤ:f",                     # قٓ
    "68:1": "nu:n",                      # نٓ
}


@pytest.mark.parametrize(("ref", "expected"), sorted(OPENINGS.items()))
def test_every_opening_is_spelled_out_by_letter_name(ref, expected):
    assert reading(Site(hafs=(ref, (1,))), waqf=1).phonemes(1) == expected


ALIF_LAM_MEEM = Site(hafs=("2:1", (1,)))
ALIF_LAM_MEEM_SAD = Site(hafs=("7:1", (1,)))


@for_each_riwayah(ALIF_LAM_MEEM, waqf=1)
def test_the_hum_between_two_names_comes_from_the_ordinary_rules(r):
    # الٓمٓ
    assert r.phonemes(1) == "ʔalifla:m̃i:m"


@for_each_riwayah(ALIF_LAM_MEEM_SAD, waqf=1)
def test_the_echo_at_the_end_comes_from_the_ordinary_rules(r):
    # الٓمٓصٓ
    assert r.phonemes(1) == "ʔalifla:m̃i:msˤaˤ:dQ"
