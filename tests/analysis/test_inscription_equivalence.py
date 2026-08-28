"""The native inscription facts agree with the legacy assembler and
`derived.py`, fact by fact. The legacy is the reference: a fact computed
differently is a bug in the native port, not a reason to change the reference.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.analysis import (
    Decorated,
    Structural,
    Supplied,
    Witnessed,
    analyse,
    decoration_targets,
    inscribe,
    open_vowel_units,
    shortened_carriers,
    silent_groups,
)
from quranic_phonemizer.model.address import Junction, Script
from quranic_phonemizer.model.inscription import GlyphKind, SlotFact
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize import derived as legacy
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize.assemble import assemble
from quranic_phonemizer.session import phonemize_request

pytestmark = pytest.mark.audit

#: Chosen for the hard cases a `derived.py` port goes wrong on: a tatweel seat
#: and a dagger alif beside its carrier (`إِبْرَٰهِـۧمَ`), a tanween's noon, a
#: silent rasm alif (`كَفَرُوا۟`), and a shortened carrier at an iltiqa. Spread
#: across every boundary state: a start, a join, a cross-verse join, a stop,
#: and a sakt (`36:52` `مَرْقَدِنَا ۜ`).
SITES = [
    ("2:6", {}),
    ("2:124", {}),
    ("2:255", {}),
    ("2:2", {}),
    ("3:1-3:2", {}),
    ("36:52-36:53", {}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


@pytest.fixture
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _both(hafs, pen, alphabet, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    return (
        assemble(session, pen, alphabet),
        analyse(session, alphabet),
        inscribe(session),
    )


def _legacy_structural(assembled) -> set[int]:
    return {e.glyph for e in assembled.spellings if isinstance(e, ed.Structural)}


def _legacy_vowel_absent(assembled) -> set[int]:
    return {
        e.glyph for e in assembled.spellings
        if isinstance(e, ed.Supplies) and e.fact is ed.Fact.VOWEL_ABSENCE
    }


#: The rename the legacy edge applies to the model fact: only ONSET differs.
_FACT = {
    SlotFact.LETTER: ed.Fact.LETTER,
    SlotFact.ONSET: ed.Fact.CONSONANT,
    SlotFact.VOWEL_QUALITY: ed.Fact.VOWEL_QUALITY,
    SlotFact.VOWEL_LENGTH: ed.Fact.VOWEL_LENGTH,
    SlotFact.VOWEL_ABSENCE: ed.Fact.VOWEL_ABSENCE,
    SlotFact.TAJWEED_MARK: ed.Fact.TAJWEED_MARK,
}


def _assert_spelling(native, legacy) -> None:
    assert native.glyph == legacy.glyph
    if isinstance(legacy, ed.Supplies):
        assert isinstance(native, Supplied)
        assert native.slot.ordinal == legacy.unit
        assert _FACT[native.fact] == legacy.fact
    elif isinstance(legacy, ed.Witnesses):
        assert isinstance(native, Witnessed)
        assert native.slot.ordinal == legacy.unit
    elif isinstance(legacy, ed.Decorates):
        assert isinstance(native, Decorated)
        assert native.slot.ordinal == legacy.unit
    else:
        assert isinstance(legacy, ed.Structural) and isinstance(native, Structural)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_glyphs_agree_in_order(hafs, pen, alphabet, ref, kwargs):
    a, _, inscription = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(inscription.glyphs) == len(a.glyphs)
    for native, legacy_glyph in zip(inscription.glyphs, a.glyphs):
        assert native.char == legacy_glyph.char
        assert native.kind.value == legacy_glyph.kind.value
        assert native.word == legacy_glyph.word
        assert native.word_index == legacy_glyph.word_index


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_spelling_edges_agree(hafs, pen, alphabet, ref, kwargs):
    a, _, inscription = _both(hafs, pen, alphabet, ref, kwargs)
    assert len(inscription.spellings) == len(a.spellings)
    for native, legacy_edge in zip(inscription.spellings, a.spellings):
        _assert_spelling(native, legacy_edge)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_structural_and_vowel_absent_sets_agree(hafs, pen, alphabet, ref, kwargs):
    a, _, inscription = _both(hafs, pen, alphabet, ref, kwargs)
    assert set(inscription.structural) == _legacy_structural(a)
    assert set(inscription.vowel_absent) == _legacy_vowel_absent(a)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_derivations_agree(hafs, pen, alphabet, ref, kwargs):
    a, facts, inscription = _both(hafs, pen, alphabet, ref, kwargs)

    native_open = {slot.ordinal for slot in open_vowel_units(facts)}
    legacy_open = legacy.open_vowel_units(a.attributions, a.sounds)
    assert native_open == legacy_open

    native_targets = decoration_targets(inscription)
    legacy_targets = legacy.decoration_targets(a.glyphs, a.spellings)
    assert {g: slot.ordinal for g, slot in native_targets.items()} == legacy_targets

    native_silent = silent_groups(
        inscription, open_vowel_units(facts), native_targets
    )
    legacy_silent = legacy.silent_groups(
        a.glyphs, a.spellings, legacy_open, legacy_targets
    )
    assert native_silent == legacy_silent

    assert shortened_carriers(facts, inscription) == legacy.shortened_carriers(
        a.spellings, a.attributions, a.modifiers
    )


def test_the_site_set_exercises_the_hard_cases(hafs, alphabet):
    """The tatweel seat, dagger alif, tanween noon, silent rasm alif, and
    iltiqa shortening must actually occur, and every junction state, so the
    comparisons above are not vacuous."""
    tatweel = dagger = tanween_noon = orthographic = shortened = False
    junctions: set[Junction] = set()
    for ref, kwargs in SITES:
        session = phonemize_request(hafs, ref, **kwargs)
        facts = analyse(session, alphabet)
        inscription = inscribe(session)
        kinds = {glyph.kind for glyph in inscription.glyphs}
        tatweel |= GlyphKind.TATWEEL in kinds
        dagger |= GlyphKind.SMALL_VOWEL in kinds
        tanween_noon |= bool(decoration_targets(inscription))
        orthographic |= bool(
            silent_groups(
                inscription, open_vowel_units(facts),
                decoration_targets(inscription),
            )
        )
        shortened |= bool(shortened_carriers(facts, inscription))
        junctions |= set(facts.junctions)
    assert tatweel and dagger and tanween_noon and orthographic and shortened
    assert junctions == set(Junction)
