"""Pairs the rasm writes the same way and a reciter reads apart.

A rule that widens far enough to swallow its pair fails here, by name,
rather than moving a percentage somewhere.
"""
from __future__ import annotations

import pytest

from conftest import score_for
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.render.recite import phonemes_by_word
from quranic_phonemizer.riwayat.hafs import HAFS

#: (surah, ayah, word), the reading, and what makes it that reading.
PAIRS = [
    (
        ((2, 237, 18), "jaʕfu:"),
        ((5, 95, 21), "ðawa:"),
        "the alif al-fasila against the dual's, told apart by the vowel "
        "before the waw",
    ),
    (
        ((5, 12, 9), "ʔiθnaj"),
        ((2, 54, 3), "mu:sa:"),
        "a maqsura carrying a sukun is a consonant, not an unwritten alif",
    ),
    (
        ((93, 4, 5), "ʔalʔu:la:"),
        ((2, 5, 1), "ʔula:ʔik"),
        "the waw of `أولئك` is rasm; the one of `الأولى` is read",
    ),
    (
        ((2, 197, 26), "ʔattaqQwa:"),
        ((54, 12, 4), "faltaqaˤ:"),
        "the article before a sun letter against a form VIII lam radical",
    ),
    (
        ((38, 6, 5), "ʔimʃu:"),
        ((7, 55, 1), "ʔudQʕu:"),
        "an arid damma takes kasra where a stem's own damma does not",
    ),
]


def _performed(packed, shared, surah: int, ayah: int):
    """Stopping after every word, as the regression harness plans it: a
    reading in isolation is the one a minimal pair is about."""
    score = score_for(packed, shared, surah, ayah)
    plan = BoundaryPlan(
        (Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,)
    )
    return score, perform(score, HAFS, plan)


def _word(packed, shared, alphabet, site) -> str:
    surah, ayah, word = site
    score, performance = _performed(packed, shared, surah, ayah)
    return "".join(phonemes_by_word(performance, score, alphabet)[word - 1])


@pytest.mark.parametrize(("left", "right", "difference"), PAIRS)
def test_the_pair_reads_apart(
    packed, shared, alphabet, left, right, difference
) -> None:
    for site, reading in (left, right):
        assert _word(packed, shared, alphabet, site) == reading, difference


def test_an_assimilated_closure_has_no_qalqala(packed, shared, alphabet) -> None:
    """`بَسَطتَ` holds the tah into the taa and keeps its itbaq; a closure
    that is never released has nothing to echo."""
    assert _word(packed, shared, alphabet, (5, 28, 2)) == "basatˤt"
    score, performance = _performed(packed, shared, 5, 28)
    held = {slot.id for slot in score.words[1].slots}
    fired = {
        o.rule for o in performance.occurrences if held & set(o.parts.slots)
    }
    assert Rule.IDGHAM_MUTAJANISAYN_NAQIS in fired
    assert not fired & {
        Rule.QALQALA_SUGHRA, Rule.QALQALA_KUBRA, Rule.QALQALA_AKBAR
    }


def test_the_shape_of_the_article_needs_a_lam(packed, shared, alphabet) -> None:
    """19:33 `وُلِدتُّ` puts a vowelless dal after a voweled lam behind a waw,
    which is the article's shape everywhere but the letter itself."""
    assert _word(packed, shared, alphabet, (19, 33, 4)) == "wulitt"
