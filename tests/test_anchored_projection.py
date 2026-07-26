"""The Spelling relation and the projection it exists for.

These are behavioural tests over the assembled `HAFS` ruleset, deliberately.
Every other engine test in this suite binds a one-rule `RuleSet`, which is why
cross-family interactions were invisible to all of them.
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

#: A spread rather than a favourite: an article lām that assimilates, a verse
#: with cross-word nūn, the muqaṭṭaʿāt, and one of the four sakt sites.
VERSES = [(112, 2), (2, 20), (1, 1), (7, 1), (18, 1), (33, 10)]


def _view(packed, shared, surah, ayah, alphabet):
    built = built_for(packed, shared, surah, ayah)
    performance = perform(built.score, HAFS, all_join(len(built.score.words)))
    return built, anchored(performance, built.score, built.inscription, alphabet)


@pytest.mark.parametrize(("surah", "ayah"), VERSES)
def test_every_slot_is_reachable_from_the_writing(packed, shared, surah, ayah):
    """I7. Falsified by a slot no grapheme accounts for — which the tanwīn nūn
    was for the whole first draft, at 5,831 Uthmani sites.

    Uthmani only, and not parametrised over `Script`: the packaged corpus is
    Uthmani, so an IndoPak parameter here would skip and read as two-script
    coverage while being one. IndoPak's I7 is asserted for real by
    `tools/cross_parity.py`, which runs `check_inscription` on both scripts
    over every verse.
    """
    built = built_for(packed, shared, surah, ayah)
    check_inscription(built.inscription, built.score)


def test_i7_fails_when_a_slot_is_unreachable(packed, shared):
    """The law is only worth having if it can fail. Drop the edges that reach
    the last slot and it must say so, naming the slot."""
    built = built_for(packed, shared, 112, 2)
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


def test_a_merged_sound_names_both_its_letters(packed, shared, alphabet):
    """`ٱللَّهُ` — the article lām merges into the shadda'd lām, and the sound
    the merger produces must point at *both*, not only the survivor. This is
    the question `Occurrence.parts` alone cannot answer."""
    _, view = _view(packed, shared, 112, 2, alphabet)
    merged = [sound for sound in view.sounds if sound.merged_from]
    assert merged, "112:2 has an assimilating article lam"
    for sound in merged:
        assert sound.rule is not Rule.PLAIN
        assert len(sound.graphemes) > 1, (
            f"{sound.token} came from a merger and names one grapheme"
        )


def test_a_silent_letter_names_the_rule_that_silenced_it(
    packed, shared, alphabet
):
    built, view = _view(packed, shared, 2, 20, alphabet)
    chars = graphemes_by_id(built.inscription)
    assert view.silent, "2:20 elides at least one wasl hamza"
    for silent in view.silent:
        assert silent.rule is not Rule.PLAIN
        # Every silent letter must be pointable at in the source text.
        assert all(grapheme in chars for grapheme in silent.graphemes)


def test_the_inverse_lookup_covers_the_sounds(packed, shared, alphabet):
    """`by_grapheme` is the direction an application highlighting text needs."""
    _, view = _view(packed, shared, 1, 1, alphabet)
    inverse = view.by_grapheme()
    anchored_sounds = {
        sound.sound for sound in view.sounds if sound.graphemes
    }
    reachable = {sound for ids in inverse.values() for sound in ids}
    assert anchored_sounds <= reachable


def test_derived_facts_have_no_grapheme_and_that_is_correct(
    packed, shared, alphabet
):
    """The waṣl helping vowel is supplied by `canon.build`, not written. Its
    sound legitimately names no grapheme, and the projection must say so
    rather than inventing one — otherwise a highlight points at the wrong
    letter. I7 is a law about *slots*, not about every aspect."""
    _, view = _view(packed, shared, 112, 2, alphabet)
    assert any(not sound.graphemes for sound in view.sounds)


def _target(spelling) -> SlotId | None:
    match spelling:
        case Evidences(slot=slot) | Decorates(slot=slot):
            return slot
        case Attests(anchor=anchor):
            return anchor
    return None
