"""The native facts cache agrees with the legacy assembler, fact by fact.

The legacy `Assembled` is the reference: for a spread of references across
every boundary state, both are built and every performance-tier fact compared.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis import (
    Classified,
    Hosted,
    Insertion,
    Merged,
    Recoloured,
    Relengthened,
    Silenced,
    analyse,
)
from quranic_phonemizer.model.address import Junction, Script
from quranic_phonemizer.model.performance import (
    Aspect, Consonant, Hosts, Inserted, Release, Side, Vowel,
)
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd
from quranic_phonemizer.analysis.sounds import sounds_in_order as native_order
from quranic_phonemizer.phonemize.assemble import assemble
from quranic_phonemizer.phonemize.ordering import sounds_in_order as legacy_order
from quranic_phonemizer.session import phonemize_request

#: One reference per boundary state, chosen for the hard cases they exercise:
#: a word isolated, words joined, a start, a stop, a sakt, mergers (idgham),
#: releases (qalqala), and the iltiqa fatha at a spelled-out opening.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("2:5", {}),
    ("3:1-3:2", {}),
    ("36:52-36:53", {}),
    ("2:255", {}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]

_PART = {Aspect.CONSONANT: ed.Part.CONSONANT, Aspect.VOWEL: ed.Part.VOWEL}


@pytest.fixture
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _both(hafs, pen, alphabet, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    return session, assemble(session, pen, alphabet), analyse(session, alphabet)


def _assert_sound(native, legacy) -> None:
    assert native.token == legacy.token
    value = native.value
    if isinstance(value, Consonant):
        assert legacy.kind is nd.SoundKind.CONSONANT
        assert (value.letter, value.geminate, value.emphatic, value.ghunnah,
                value.eased) == (legacy.letter, legacy.geminate,
                                 legacy.emphatic, legacy.ghunnah, legacy.eased)
    elif isinstance(value, Vowel):
        assert legacy.kind is nd.SoundKind.VOWEL
        assert (value.quality, value.long, value.emphatic) == (
            legacy.quality, legacy.long, legacy.emphatic)
    else:
        assert isinstance(value, Release)
        assert legacy.kind is nd.SoundKind.QALQALA
        assert value.degree == legacy.degree


def _slot_ordinal(edge) -> int:
    if isinstance(edge, Insertion):
        return edge.anchor[0].ordinal
    return edge.slots[0].ordinal


def _assert_attribution(native, legacy) -> None:
    if isinstance(legacy, ed.Hosts):
        assert isinstance(native, (Hosted, Insertion))
        assert native.sound == legacy.sound
    elif isinstance(legacy, ed.MergedInto):
        assert isinstance(native, Merged)
        assert native.sound == legacy.sound
    else:
        assert isinstance(legacy, ed.Silent)
        assert isinstance(native, Silenced)
    assert native.by == legacy.by
    assert _PART[native.aspect] == legacy.part
    assert _slot_ordinal(native) == legacy.unit


def _assert_modifier(native, legacy) -> None:
    assert native.sound == legacy.sound
    assert native.by == legacy.by
    if isinstance(legacy, ed.SetsLength):
        assert isinstance(native, Relengthened)
        assert native.length == legacy.length
    elif isinstance(legacy, ed.Recolours):
        assert isinstance(native, Recoloured)
    else:
        assert isinstance(legacy, ed.Classifies)
        assert isinstance(native, Classified)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_sounds_agree_in_order_and_token(hafs, pen, alphabet, ref, kwargs):
    _, a, facts = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(facts.sounds) == len(a.sounds)
    for native, legacy in zip(facts.sounds, a.sounds):
        _assert_sound(native, legacy)
    assert all(facts.sound_index[s] == i for i, s in enumerate(facts.sound_index))


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_word_of_slot_agrees(hafs, pen, alphabet, ref, kwargs):
    _, a, facts = _both(hafs, pen, alphabet, ref, kwargs)
    assert facts.word_of_slot == tuple(unit.word for unit in a.units)
    assert len(facts.slots) == len(a.units)
    assert all(facts.slot_index[s.id] == i for i, s in enumerate(facts.slots))


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_occurrences_and_effect_targets_agree(hafs, pen, alphabet, ref, kwargs):
    _, a, facts = _both(hafs, pen, alphabet, ref, kwargs)
    for i, occurrence in enumerate(facts.occurrences):
        instance = a.rules[i]
        assert instance.rule == occurrence.rule
        assert instance.source == occurrence.subjects[0].ordinal
        named = occurrence.subjects[1:] + facts.effect_targets.get(
            occurrence.id, ()
        )
        assert instance.host == (named[0].ordinal if named else None)
        assert facts.occurrence_index[occurrence.id] == i


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_attribution_edges_agree(hafs, pen, alphabet, ref, kwargs):
    _, a, facts = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(facts.attributions) == len(a.attributions)
    for native, legacy in zip(facts.attributions, a.attributions):
        _assert_attribution(native, legacy)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_modifier_edges_agree(hafs, pen, alphabet, ref, kwargs):
    _, a, facts = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(facts.modifiers) == len(a.modifiers)
    for native, legacy in zip(facts.modifiers, a.modifiers):
        _assert_modifier(native, legacy)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_junctions_are_the_boundary_plan(hafs, pen, alphabet, ref, kwargs):
    session, _, facts = _both(hafs, pen, alphabet, ref, kwargs)
    assert facts.junctions == session.boundaries.junctions


def test_the_site_set_exercises_the_hard_cases(hafs, alphabet):
    """Releases, mergers, silences, and every junction state must actually
    occur, so the comparisons above are not vacuous."""
    releases = mergers = silences = False
    junctions: set[Junction] = set()
    modifiers: set[type] = set()
    for ref, kwargs in SITES:
        facts = analyse(phonemize_request(hafs, ref, **kwargs), alphabet)
        releases |= any(isinstance(s.value, Release) for s in facts.sounds)
        mergers |= bool(facts.merges)
        silences |= bool(facts.silences)
        junctions |= set(facts.junctions)
        modifiers |= {type(m) for m in facts.modifiers}
    assert releases and mergers and silences
    assert junctions == set(Junction)
    assert modifiers == {Recoloured, Relengthened, Classified}


@pytest.mark.parametrize(
    "side,before", [(Side.BEFORE, True), (Side.AFTER, False)]
)
def test_an_inserted_sound_lands_on_its_anchor_side(hafs, side, before):
    # No Hafs rule mints an Insert effect, so the corpus never reaches the
    # inserted-anchor branch. Synthesize one that collides with a hosted sound
    # on the same slot and aspect, where the anchor side is what orders them,
    # and hold the native ordering to the legacy on it.
    session = phonemize_request(hafs, "2:255")
    perf = session.performance
    hosted = next(a for a in perf.attributions if isinstance(a, Hosts) and a.slots)
    guest = next(s for s, _ in perf.sounds if s != hosted.sound)
    inserted = Inserted(
        anchor=(hosted.slots[0], side), aspect=hosted.aspect,
        sound=guest, by=hosted.by,
    )
    synthetic = dataclasses.replace(
        perf, attributions=perf.attributions + (inserted,)
    )
    order = native_order(synthetic)

    assert any(isinstance(a, Inserted) for a in synthetic.attributions)
    assert order == legacy_order(synthetic)
    assert (order.index(guest) < order.index(hosted.sound)) is before
