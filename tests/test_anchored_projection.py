"""The Spelling relation and the projection it exists for.

Runs against the assembled `HAFS` ruleset rather than a single rule, so
cross-family interactions are exercised too.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.laws import LawError, check_inscription
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import SlotId
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.inscription import Attests, Decorates, Evidences
from quranic_phonemizer.render.anchored import anchored, graphemes_by_id
from quranic_phonemizer.riwayat.hafs import HAFS

from conftest import built_for

#: Chosen to cover distinct cases: an article lam that assimilates, a verse
#: with cross-word noon, the muqattaat, and one of the four sakt sites.
VERSES = [(112, 2), (2, 20), (1, 1), (7, 1), (18, 1), (33, 10)]


def _view(packed, hafs, surah, ayah, alphabet):
    built = built_for(packed, hafs, surah, ayah)
    performance = perform(built.score, HAFS, all_join(len(built.score.words)))
    return built, anchored(performance, built.inscription, alphabet)


@pytest.mark.parametrize(("surah", "ayah"), VERSES)
def test_every_slot_is_reachable_from_the_writing(packed, hafs, surah, ayah):
    """Every slot in the score must be accounted for by some grapheme.

    Uthmani only: the packaged corpus is Uthmani. IndoPak coverage is
    checked separately by `tools/cross_parity.py`.
    """
    built = built_for(packed, hafs, surah, ayah)
    check_inscription(built.inscription, built.score)


def test_i7_fails_when_a_slot_is_unreachable(packed, hafs):
    """Dropping the edges that reach the last slot must raise, naming that slot."""
    built = built_for(packed, hafs, 112, 2)
    last = built.score.words[-1].slots[-1].id
    stripped = tuple(
        spelling
        for spelling in built.inscription.spellings
        if _target(spelling) != last
    )
    crippled = type(built.inscription)(
        verse=built.inscription.verse,
        script=built.inscription.script,
        words=built.inscription.words,
        graphemes=built.inscription.graphemes,
        spellings=stripped,
        advice=built.inscription.advice,
    )
    with pytest.raises(LawError, match="I7"):
        check_inscription(crippled, built.score)


def test_a_merged_sound_names_both_its_letters(packed, hafs, alphabet):
    """`ٱللَّهُ`: the article lam merges into the shadda'd lam, and the merged
    sound must point at both letters, not only the survivor."""
    _, view = _view(packed, hafs, 112, 2, alphabet)
    merged = [sound for sound in view.sounds if sound.merged_from]
    assert merged, "112:2 has an assimilating article lam"
    for sound in merged:
        assert sound.rule is not Rule.PLAIN
        assert len(sound.graphemes) > 1, (
            f"{sound.token} came from a merger and names one grapheme"
        )


def test_a_silent_letter_names_the_rule_that_silenced_it(
    packed, hafs, alphabet
):
    built, view = _view(packed, hafs, 2, 20, alphabet)
    chars = graphemes_by_id(built.inscription)
    assert view.silent, "2:20 elides at least one wasl hamza"
    for silent in view.silent:
        assert silent.rule is not Rule.PLAIN
        # Every silent letter must be pointable at in the source text.
        assert all(grapheme in chars for grapheme in silent.graphemes)


def test_the_inverse_lookup_covers_the_sounds(packed, hafs, alphabet):
    """`by_grapheme` is the direction an application highlighting text needs."""
    _, view = _view(packed, hafs, 1, 1, alphabet)
    inverse = view.by_grapheme()
    anchored_sounds = {
        sound.sound for sound in view.sounds if sound.graphemes
    }
    reachable = {sound for ids in inverse.values() for sound in ids}
    assert anchored_sounds <= reachable


def test_derived_facts_have_no_grapheme_and_that_is_correct(
    packed, hafs, alphabet
):
    """The wasl helping vowel is supplied by `canon.build`, not written, so
    its sound names no grapheme. The projection must say so rather than
    invent one, or a highlight would point at the wrong letter."""
    _, view = _view(packed, hafs, 112, 2, alphabet)
    assert any(not sound.graphemes for sound in view.sounds)


def _target(spelling) -> SlotId | None:
    match spelling:
        case Evidences(slot=slot) | Decorates(slot=slot):
            return slot
        case Attests(anchor=anchor):
            return anchor
    return None
