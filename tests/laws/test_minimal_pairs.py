"""Pairs the rasm writes the same way and a reciter reads apart.

A rule that widens far enough to swallow its pair fails here, by name,
rather than moving a percentage somewhere.
"""
from __future__ import annotations

import pytest

from conftest import score_for
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import Nucleus, Onset, Quality, Rule
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
    (
        ((62, 11, 16), "ʔallahw"),
        ((1, 1, 2), "ʔalˤlˤaˤ:h"),
        "the name of God against a word that opens the same and carries a "
        "third radical",
    ),
    (
        ((3, 13, 7), "ʔiltaqaˤta:"),
        ((2, 197, 26), "ʔattaqQwa:"),
        "a form VIII lam inflected for agreement is still not the article",
    ),
    (
        ((18, 61, 5), "nasija:"),
        ((2, 29, 1), "hu:"),
        "a glide carrying a vowel the stop cannot strip is a consonant",
    ),
    (
        ((27, 44, 17), "qaˤwa:ri:r"),
        ((76, 15, 8), "qaˤwa:ri:rˤaˤ:"),
        "one of the seven alifs is a site, not a lexeme: its own word is "
        "written twice more without it",
    ),
]

#: A hamza that elides when joined, and one shaped exactly like it that does
#: not. Read alone they are the same sounds, so only the junction tells them
#: apart -- which is what a word-by-word pair cannot show.
PROSTHETIC = [
    ((27, 66, 2), True, "form VIII doubles a letter the taa assimilates into"),
    ((19, 89, 4), False, "`إدّ` doubles the same letter and is a noun"),
    ((18, 48, 13), False, "`ألّن` doubles a lam and is not the article"),
    ((10, 53, 5), False, "two letters cannot be a prop, its load, and a stem"),
]


def _performed(packed, hafs, surah: int, ayah: int):
    """Stopping after every word, as the regression harness plans it: a
    reading in isolation is the one a minimal pair is about."""
    score = score_for(packed, hafs, surah, ayah)
    plan = BoundaryPlan(
        (Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,)
    )
    return score, perform(score, HAFS, plan)


def _word(packed, hafs, alphabet, site) -> str:
    surah, ayah, word = site
    score, performance = _performed(packed, hafs, surah, ayah)
    return "".join(phonemes_by_word(performance, score, alphabet)[word - 1])


@pytest.mark.parametrize(("left", "right", "difference"), PAIRS)
def test_the_pair_reads_apart(
    packed, hafs, alphabet, left, right, difference
) -> None:
    for site, reading in (left, right):
        assert _word(packed, hafs, alphabet, site) == reading, difference


def test_an_assimilated_closure_has_no_qalqala(packed, hafs, alphabet) -> None:
    """`بَسَطتَ` holds the tah into the taa and keeps its itbaq; a closure
    that is never released has nothing to echo."""
    assert _word(packed, hafs, alphabet, (5, 28, 2)) == "basatˤt"
    score, performance = _performed(packed, hafs, 5, 28)
    held = {slot.id for slot in score.words[1].slots}
    fired = {
        o.rule for o in performance.occurrences
        if held & {o.parts.source, o.parts.host}
    }
    assert Rule.IDGHAM_MUTAJANISAYN_NAQIS in fired
    assert not fired & {
        Rule.QALQALA_SUGHRA, Rule.QALQALA_KUBRA, Rule.QALQALA_AKBAR
    }


@pytest.mark.parametrize(("site", "prosthetic", "why"), PROSTHETIC)
def test_only_a_prosthetic_hamza_elides(
    packed, hafs, site, prosthetic, why
) -> None:
    surah, ayah, word = site
    score = score_for(packed, hafs, surah, ayah)
    opening = score.words[word - 1].slots[0]
    assert (opening.onset is Onset.WASL) is prosthetic, why


def test_the_plural_meem_is_voweled_before_a_prosthetic_hamza(
    packed, hafs, alphabet
) -> None:
    """Two quiescent letters would meet otherwise, so `ـكُمْ` takes a damma
    that only the following word calls for."""
    score = score_for(packed, hafs, 6, 93)
    assert score.words[33].slots[-1].nucleus == Nucleus.short(Quality.U)
    assert _word(packed, hafs, alphabet, (6, 93, 34)) == "ʔaŋfusakum"


def test_a_letter_name_ends_where_the_next_begins(
    packed, hafs, alphabet
) -> None:
    """`طسٓمٓ` says three names, so the noon of `سين` meets the meem of `ميم`
    across a boundary and assimilates instead of standing clear."""
    assert _word(packed, hafs, alphabet, (26, 1, 1)) == "tˤaˤ:si:m̃i:m"


def test_the_shape_of_the_article_needs_a_lam(packed, hafs, alphabet) -> None:
    """19:33 `وُلِدتُّ` puts a vowelless dal after a voweled lam behind a waw,
    which is the article's shape everywhere but the letter itself."""
    assert _word(packed, hafs, alphabet, (19, 33, 4)) == "wulitt"
