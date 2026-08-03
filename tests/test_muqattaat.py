from __future__ import annotations

import pytest

from quranic_phonemizer.model.canon import Rule
from tests.support import Site, for_each_riwayah, reading

TA_SEEN = Site(hafs=("27:1", (1,)))
YA_SEEN = Site(hafs=("36:1", (1,)))
NOON = Site(hafs=("68:1", (1,)))

OPENINGS = {
    "2:1": "ʔalifla:m̃i:m",              # الٓمٓ
    "7:1": "ʔalifla:m̃i:msˤaˤ:dQ",       # الٓمٓصٓ
    "10:1": "ʔalifla:mrˤaˤ:",            # الٓر
    "13:1": "ʔalifla:m̃i:mrˤaˤ:",        # الٓمٓر
    "19:1": "ka:fha:ja:ʕajŋsˤaˤ:dQ",    # كٓهيعٓصٓ
    "20:1": "tˤaˤ:ha:",                  # طه
    "26:1": "tˤaˤ:si:m̃i:m",             # طسٓمٓ
    "27:1": "tˤaˤ:si:n",                 # طسٓ
    "36:1": "ja:si:n",                   # يسٓ
    "38:1": "sˤaˤ:dQ",                   # صٓ
    "40:1": "ħa:mi:m",                   # حمٓ
    "42:2": "ʕajŋsi:ŋqaˤ:f",            # عٓسٓقٓ
    "50:1": "qaˤ:f",                     # قٓ
    "68:1": "nu:n",                      # نٓ
}


#: An opening is spelled as if stopped on, so joining changes nothing here.
JOINED_TO_WHAT_FOLLOWS = [
    "2:1",    # الٓمٓ ذَٰلِكَ
    "7:1",    # الٓمٓصٓ كِتَـٰبٌ
    "10:1",   # الٓر تِلْكَ
    "13:1",   # الٓمٓر تِلْكَ
    "19:1",   # كٓهيعٓصٓ ذِكْرُ
    "20:1",   # طه مَآ
    "26:1",   # طسٓمٓ تِلْكَ
    "38:1",   # صٓ وَٱلْقُرْءَانِ
    "40:1",   # حمٓ تَنزِيلُ
    "42:2",   # عٓسٓقٓ كَذَٰلِكَ
    "50:1",   # قٓ وَٱلْقُرْءَانِ
]


@pytest.mark.parametrize(("ref", "expected"), sorted(OPENINGS.items()))
def test_every_opening_is_spelled_out_by_letter_name(ref, expected):
    assert reading(Site(hafs=(ref, (1,))), isolated=1).phonemes(1) == expected


@pytest.mark.parametrize("ref", JOINED_TO_WHAT_FOLLOWS)
def test_an_opening_reads_the_same_whether_it_is_joined_or_stopped_on(ref):
    joined = reading(Site(hafs=(ref, (1,))), ibtidaa=1, wasl=1)
    assert joined.phonemes(1) == OPENINGS[ref]


@for_each_riwayah(TA_SEEN, ibtidaa=1, wasl=1)
def test_the_noon_of_ta_seen_stays_clear_before_the_word_after_it(r):
    # طسٓ تِلْكَ
    # the engine hides the noon into the taa of the next word
    # a second reading hides it; supporting both is later work
    assert r.phonemes(1) == "tˤaˤ:si:n"
    assert r.phonemes(2) == "tilka"


@for_each_riwayah(YA_SEEN, ibtidaa=1, wasl=1)
def test_the_noon_of_ya_seen_stays_clear_across_the_verse_seam(r):
    # يسٓ وَٱلْقُرْءَانِ
    # the engine merges the noon into the waw of the next verse
    # a second reading merges it; supporting both is later work
    assert r.phonemes(1) == "ja:si:n"
    assert r.phonemes(2) == "walqurˤʔa:ni"


@for_each_riwayah(NOON, ibtidaa=1, wasl=1)
def test_the_noon_of_the_opening_noon_stays_clear_before_the_waw(r):
    # نٓ وَٱلْقَلَمِ
    # the engine merges the noon into the waw after it
    # a second reading merges it; supporting both is later work
    assert r.phonemes(1) == "nu:n"
    assert r.phonemes(2) == "walqaˤlami"


def _closing_rules(r, word: int) -> set[Rule]:
    last = r.score.words[word - 1].slots[-1]
    return {o.rule for o in r.performance.occurrences if o.parts.source == last.id}


@for_each_riwayah(NOON, ibtidaa=1, wasl=1)
def test_the_opening_noon_takes_its_own_izhar_rather_than_none(r):
    # نٓ closes on its own plain articulation; it neither merges into
    # `وَٱلْقَلَمِ` nor takes a rule from it.
    assert _closing_rules(r, 1) == {Rule.IZHAR}


@for_each_riwayah(TA_SEEN, ibtidaa=1, wasl=1)
def test_the_opening_noon_of_ta_seen_takes_its_own_izhar(r):
    assert _closing_rules(r, 1) == {Rule.IZHAR}


@pytest.mark.parametrize("ref", ["2:1", "40:1"])
def test_a_meem_final_opening_takes_its_own_izhar_shafawi(ref):
    r = reading(Site(hafs=(ref, (1,))), ibtidaa=1, wasl=1)
    assert _closing_rules(r, 1) == {Rule.IZHAR_SHAFAWI}
