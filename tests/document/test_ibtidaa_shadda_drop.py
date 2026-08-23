"""A shadda on a word's first letter is the merger from the word before it.

Started on there is no word before, so the letter is said once. The sites
are read off the corpus rather than listed.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.model import performance as pf
from quranic_phonemizer.model.address import VerseRef

from tests.support import Site, loaded, reading

SHADDA = "ّ"


def _start_sites() -> tuple[tuple[str, int, str], ...]:
    """Every word whose written first letter carries a shadda, with that
    letter. A word opening its verse is left out: the word before it sits in
    the verse before, which one scored verse does not hold.
    """
    recitation = loaded()
    counts = recitation.corpus.surah_info
    sites = []
    for surah in range(1, len(counts) + 1):
        for ayah in range(1, len(counts[str(surah)]) + 1):
            for location, text in recitation.words(VerseRef(surah, ayah)):
                if location.word > 1 and text[1:2] == SHADDA:
                    sites.append((f"{surah}:{ayah}", location.word, text[0]))
    return tuple(sites)


SITES = _start_sites()


def _one_per_letter():
    """The first site of each opening letter, in corpus order."""
    first: dict[str, tuple[str, int]] = {}
    for ref, word, letter in SITES:
        first.setdefault(letter, (ref, word))
    return tuple((letter, ref, word) for letter, (ref, word) in first.items())


PER_LETTER = _one_per_letter()
IDS = [letter for letter, _, _ in PER_LETTER]


def _started(ref: str, word: int):
    return reading(Site(hafs=(ref, (word - 1, word))), ibtidaa=word)


def _joined(ref: str, word: int):
    return reading(Site(hafs=(ref, (word - 1, word))), ibtidaa=word - 1,
                   waqf=word)


def _opening_consonant(r, word: int) -> pf.Consonant:
    slot = r.score.words[word - 1].slots[0].id
    sounds = dict(r.performance.sounds)
    for edge in r.performance.attributions:
        if (
            isinstance(edge, pf.Hosts)
            and edge.aspect is pf.Aspect.CONSONANT
            and slot in edge.slots
        ):
            return sounds[edge.sound]
    raise AssertionError(f"word {word} of {r.text(word)} says no first letter")


def _bridging(r, word: int) -> tuple[pf.Occurrence, ...]:
    """Occurrences named on the word before that reach this word's first
    letter by an edge of their own."""
    before = {slot.id for slot in r.score.words[word - 2].slots}
    opening = r.score.words[word - 1].slots[0].id
    targets = pf.effect_targets(r.performance)
    return tuple(
        occurrence for occurrence in r.performance.occurrences
        if set(occurrence.subjects) & before
        and opening in targets.get(occurrence.id, ())
    )


def _named_together(r, word: int) -> tuple[pf.Occurrence, ...]:
    """Occurrences naming a slot of the word before and this word's first
    letter at once, whether as subject, context, or effect."""
    before = {slot.id for slot in r.score.words[word - 2].slots}
    opening = r.score.words[word - 1].slots[0].id
    targets = pf.effect_targets(r.performance)
    out = []
    for occurrence in r.performance.occurrences:
        named = (
            set(occurrence.subjects)
            | set(occurrence.context)
            | set(targets.get(occurrence.id, ()))
        )
        if named & before and opening in named:
            out.append(occurrence)
    return tuple(out)


@pytest.mark.parametrize(("letter", "ref", "word"), PER_LETTER, ids=IDS)
def test_a_word_started_on_says_its_first_letter_once(letter, ref, word):
    assert not _opening_consonant(_started(ref, word), word).geminate


@pytest.mark.parametrize(("letter", "ref", "word"), PER_LETTER, ids=IDS)
def test_nothing_from_the_word_before_reaches_a_word_started_on(
    letter, ref, word
):
    """The falsifier for a shadda read as the word's own: a rule still
    holding a participant in the word the start left behind."""
    r = _started(ref, word)
    assert _named_together(r, word) == ()


@pytest.mark.parametrize(("letter", "ref", "word"), PER_LETTER, ids=IDS)
def test_the_same_shadda_is_a_merger_once_the_word_before_joins(
    letter, ref, word
):
    r = _joined(ref, word)
    assert _opening_consonant(r, word).geminate
    bridge = _bridging(r, word)
    assert len(bridge) == 1
    assert set(bridge[0].subjects) <= {
        slot.id for slot in r.score.words[word - 2].slots
    }


@pytest.mark.slow
def test_every_start_site_in_the_corpus_says_its_first_letter_once():
    doubled = [
        (ref, word) for ref, word, _ in SITES
        if _opening_consonant(_started(ref, word), word).geminate
    ]
    assert not doubled
