"""Muqattaat letters: named rather than read.

`canon/spell.py` lays down the names only; the ghunnah in 2:1 and the
qalqala in 7:1 must come from the ordinary rules, with no special case.
"""
from __future__ import annotations

import pytest

from conftest import built_for
from quranic_phonemizer.engine.laws import check_inscription
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import Rule, SlotOrigin
from quranic_phonemizer.render.recite import phonemes_by_word
from quranic_phonemizer.riwayat.hafs import HAFS

#: Every distinct opening, one per form, plus the one that gave trouble.
SITES = {
    (2, 1): ["ʔ", "a", "l", "i", "f", "l", "a:", "m̃", "i:", "m"],
    (7, 1): ["ʔ", "a", "l", "i", "f", "l", "a:", "m̃", "i:",
             "m", "sˤ", "aˤ:", "d", "Q"],
    (19, 1): ["k", "a:", "f", "h", "a:", "j", "a:", "ʕ", "a", "j",
              "ŋ", "sˤ", "aˤ:", "d", "Q"],
    (20, 1): ["tˤ", "aˤ:", "h", "a:"],
    (36, 1): ["j", "a:", "s", "i:", "n"],
    (42, 2): ["ʕ", "a", "j", "ŋ", "s", "i:", "ŋ", "q", "aˤ:", "f"],  # qāf is istiʿlāʾ: its vowel is emphatic,
    (68, 1): ["n", "u:", "n"],
}


def _first_word(packed, shared, alphabet, surah, ayah):
    built = built_for(packed, shared, surah, ayah)
    score = built.score
    check_inscription(built.inscription, score)
    plan = BoundaryPlan(
        (Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,)
    )
    performance = perform(score, HAFS, plan)
    return score, performance, list(
        phonemes_by_word(performance, score, alphabet)[0]
    )


@pytest.mark.parametrize(("site", "expected"), sorted(SITES.items()))
def test_the_openings_are_spelled_out(packed, shared, alphabet, site, expected):
    _, _, got = _first_word(packed, shared, alphabet, *site)
    assert got == expected


def test_the_spelled_slots_are_marked_as_such(packed, shared, alphabet):
    """A spelled-out muqattaat letter must produce `SlotOrigin.SPELLED`
    slots."""
    score, _, _ = _first_word(packed, shared, alphabet, 7, 1)
    origins = {slot.origin for slot in score.words[0].slots}
    assert origins == {SlotOrigin.SPELLED}


def test_the_ordinary_rules_act_on_the_spelled_letters(packed, shared, alphabet):
    """2:1's ghunnah and 7:1's qalqala both come from ordinary rules, not
    from `canon/spell.py`."""
    _, performance, _ = _first_word(packed, shared, alphabet, 7, 1)
    fired = {o.rule for o in performance.occurrences}
    assert Rule.QALQALA_KUBRA in fired or Rule.QALQALA_SUGHRA in fired
    assert fired & {Rule.IDGHAM_SHAFAWI, Rule.IDGHAM_MUTAMATHILAYN}


def test_a_word_with_any_vowel_is_not_spelled(packed, shared, alphabet):
    """The trigger is "nothing in this word is voweled", asked of the clusters.
    An ordinary verse must be untouched."""
    score, _, _ = _first_word(packed, shared, alphabet, 1, 1)
    assert all(
        slot.origin is not SlotOrigin.SPELLED
        for word in score.words
        for slot in word.slots
    )
