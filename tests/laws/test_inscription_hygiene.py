"""Seven glyph/Spelling defects B1 closed: each test fails on the old code."""
from __future__ import annotations

import pytest

from quranic_phonemizer.canon import derive
from quranic_phonemizer.model.address import Location, Script, VerseRef
from quranic_phonemizer.model.inscription import (
    Decorates,
    Evidences,
    GraphemeClass,
    SlotFact,
    Structural,
)
from quranic_phonemizer.orthography.cluster import read_verse
from quranic_phonemizer.orthography.inventory import load_inventory
from quranic_phonemizer.riwayat.hafs.resources import DATA, RIWAYAH

from conftest import built_for

CONTRACT = {
    "riwayah": RIWAYAH,
    "derivations": frozenset(derive.registered()),
    "roles": derive.required_roles(),
}


def _uthmani():
    return load_inventory(
        DATA / "scripts" / "uthmani.yaml", script=Script.UTHMANI, **CONTRACT
    )


def _read(text: str):
    verse = VerseRef(999, 999)
    return read_verse(_uthmani(), verse, ((Location(999, 999, 1), text),))


def test_no_grapheme_offset_is_spelled_twice(packed, hafs):
    """2:72 `فَٱدَّٰرَٰٔتُمْ`: a combining hamza that falls off a released
    dagger seat used to record its own grapheme twice."""
    built = built_for(packed, hafs, 2, 72)
    offsets = [g.id for g in built.inscription.graphemes]
    assert len(offsets) == len(set(offsets))


def test_a_glyph_declared_onset_is_evidenced_once(packed, hafs):
    """`ٱ` (WASL) used to be evidenced by the cluster and again by the
    builder, at the same offset."""
    built = built_for(packed, hafs, 96, 1)
    onsets = [
        spelling for spelling in built.inscription.spellings
        if isinstance(spelling, Evidences) and spelling.fact is SlotFact.ONSET
    ]
    seen = [edge.grapheme for edge in onsets]
    assert len(seen) == len(set(seen))
    assert onsets, "96:1 opens on a hamzat wasl"


def test_a_dagger_evidences_its_own_glyph_not_the_carrier(packed, hafs):
    """2:5 `أُو۟لَـٰٓئِكَ`: the dagger on the maqsura used to spell its
    NUCLEUS from the carrier's own offset, indistinguishable from it."""
    built = built_for(packed, hafs, 2, 5)
    daggers = [
        g for g in built.inscription.graphemes if g.cls is GraphemeClass.SMALL_VOWEL
    ]
    assert daggers, "2:5 carries a small-vowel dagger"
    by_offset = {g.id.offset: g.id for g in built.inscription.graphemes}
    nucleus_edges = {
        spelling.grapheme: spelling.slot
        for spelling in built.inscription.spellings
        if isinstance(spelling, Evidences) and spelling.fact is SlotFact.VOWEL_LENGTH
    }
    decorated = {
        (spelling.grapheme, spelling.slot)
        for spelling in built.inscription.spellings
        if isinstance(spelling, Decorates)
    }
    for dagger in daggers:
        slot = nucleus_edges[dagger.id]
        carrier = by_offset[dagger.id.offset - 1]
        assert carrier not in nucleus_edges, (
            "the carrier's own offset must not evidence the dagger's fact"
        )
        assert (carrier, slot) in decorated, (
            "the carrier must still decorate the slot its dagger lengthens"
        )


def test_an_iwad_carrier_is_reachable(packed, hafs):
    """4:48 `إِثْمًا`: the alif that lengthens at a stop used to be skipped
    with no Spelling edge at all -- it decorates the base slot it lengthens,
    not the tanween noon it silences."""
    built = built_for(packed, hafs, 4, 48)
    word = built.score.words[18]  # 0-based; corpus word 19
    base = word.slots[-2].id
    decorating_base = [
        spelling for spelling in built.inscription.spellings
        if isinstance(spelling, Decorates) and spelling.slot == base
    ]
    assert decorating_base, "the iwad alif must decorate the base slot"


def test_sakt_is_evidenced_by_no_glyph(packed, hafs):
    """83:14 `بَلْ`: sakt is a word fact the Ledger states; no glyph supplies
    it, so it must never appear as an `Evidences` edge."""
    built = built_for(packed, hafs, 83, 14)
    sakt_edges = [
        spelling for spelling in built.inscription.spellings
        if isinstance(spelling, Evidences) and spelling.fact is SlotFact.SAKT
    ]
    assert not sakt_edges
    assert any(w.sakt_after for w in built.score.words)


def test_the_inter_word_space_is_a_glyph(packed, hafs):
    """A space inside a word's own text was always a `Structural` glyph; the
    one between two words used to advance the offset counter and vanish."""
    built = built_for(packed, hafs, 1, 1)
    spaces = [g for g in built.inscription.graphemes if g.char == " "]
    assert len(spaces) == 3, "three inter-word gaps across four words"
    structural_offsets = {
        spelling.grapheme.offset for spelling in built.inscription.spellings
        if isinstance(spelling, Structural)
    }
    assert all(space.id.offset in structural_offsets for space in spaces)


def test_a_bare_seat_is_structural_not_decorated():
    """A tatweel nothing was ever written on takes the Structural edge, the
    same one a stop sign takes -- not a Decorates edge of its own."""
    reading = _read("بَـ")
    assert reading.structural == (2,)
    assert not reading.decorations


def test_a_marked_seat_still_reaches_a_slot():
    """A tatweel carrying a dagger is not swallowed by the bare-seat case:
    it still lengthens the letter before it."""
    reading = _read("بَـٰ")
    tatweel = next(i for i, c in enumerate(reading.clusters) if c.base == "ـ")
    assert any(
        row.cluster == tatweel and row.fact is SlotFact.VOWEL_LENGTH
        for row in reading.evidence
    )
