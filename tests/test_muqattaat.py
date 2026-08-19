from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

TA_SEEN = Site(hafs=("27:1", (1,)))

OPENINGS = {
    "2:1": "ʔalifla:m̃i:m",              # الٓمٓ
    "7:1": "ʔalifla:m̃i:msˤaˤ:dQ",       # الٓمٓصٓ
    "10:1": "ʔalifla:mrˤaˤ:",            # الٓر
    "13:1": "ʔalifla:m̃i:mrˤaˤ:",        # الٓمٓر
    "19:1": "ka:fha:ja:ʕajŋsˤaˤ:dQ",    # كٓهيعٓصٓ
    "20:1": "tˤaˤ:ha:",                  # طه
    "26:1": "tˤaˤ:si:m̃i:m",             # طسٓمٓ
    "27:1": "tˤaˤ:si:n",                 # طسٓ
    "38:1": "sˤaˤ:dQ",                   # صٓ
    "40:1": "ħa:mi:m",                   # حمٓ
    "42:2": "ʕajŋsi:ŋqaˤ:f",            # عٓسٓقٓ
    "50:1": "qaˤ:f",                     # قٓ
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


@for_each_riwayah(TA_SEEN, ibtidaa=1, wasl=1)
def test_the_opening_noon_of_ta_seen_takes_its_own_plain_articulation(r):
    # The noon closing a spelled-out opening is read clear on its own terms
    # rather than by whatever letter the next word begins with.
    assert r.rules_on_sound(1, "n") == {"izhar"}


@pytest.mark.parametrize("ref", ["2:1", "40:1"])
def test_a_meem_final_opening_takes_its_own_plain_articulation(ref):
    r = reading(Site(hafs=(ref, (1,))), ibtidaa=1, wasl=1)
    assert r.rules_on_sound(1, "m") == {"izhar_shafawi"}
    assert "madd_lazim" in r.rules_on_char(1, "م")


def test_an_opening_joined_to_the_name_of_god_breaks_the_meeting_with_a_fatha():
    """`الٓمٓ ٱللَّهُ` (3:1 into 3:2): the meem meets the bare lam the elided hamza
    leaves, takes a fatha, and stops the vowel before it no longer."""
    from quranic_phonemizer import Phonemizer

    joined = Phonemizer().phonemize(ref="3:1-3:2")
    assert "".join(joined.phonemes())[:12] == "ʔalifla:m̃i:ma"[:12]
    named = {r.rule.value for r in joined.rules}
    assert "iltiqa_fatha" in named
    # the meem is voweled now, so it is no longer a meem sakinah at all
    meem = joined.sounds.index(next(s for s in joined.sounds if s.token == "m"))
    on = {joined.rules[m.by].rule.value for m in joined.modifiers if m.sound == meem}
    assert "izhar_shafawi" not in on

    alone = Phonemizer().phonemize(ref="3:1")
    assert "".join(alone.phonemes()) == "ʔalifla:m̃i:m"
    assert "iltiqa_fatha" not in {r.rule.value for r in alone.rules}
