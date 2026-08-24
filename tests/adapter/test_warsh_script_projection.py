"""Sequence-aware projection of the selected King Fahd Warsh script."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from quranic_phonemizer.model.address import Location, Script
from quranic_phonemizer.model.canon import CanonLetter, Nucleus, Onset, Quality
from quranic_phonemizer.model.inscription import SlotFact
from quranic_phonemizer.orthography.inventory import InventoryError
from quranic_phonemizer.riwayat.warsh.resources import corpus, script_adapter

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "corpus_sources" / "warsh" / "scripts" / "king-fahd" / "quran.json"


def _reading(ref: tuple[int, int, int]):
    location = Location(*ref)
    entry = corpus().entries[location]
    return entry, script_adapter(Script.UTHMANI).read(
        location.verse, ((location, entry.text),)
    )


def _evidence_at(reading, offset: int, fact: SlotFact):
    return next(
        row for row in reading.evidence
        if row.offset == offset and row.fact is fact
    )


def test_the_inventory_is_total_over_all_62_selected_source_scalars():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    scalars = {char for record in source.values() for char in record["text"]}
    inventory = script_adapter(Script.UTHMANI).inventory

    assert len(scalars) == 62
    assert all(inventory.classify(char) is not None for char in scalars)


def test_initial_alif_haraka_mark_is_one_wasl_sequence():
    entry, reading = _reading((1, 2, 1))  # source 1:1:1 اِ۬لْحَمْدُ
    first = reading.clusters[0]
    onset_offsets = {
        row.offset for row in reading.evidence if row.fact is SlotFact.ONSET
    }

    assert entry.text.startswith("اِ۬")
    assert first.letter is CanonLetter.HAMZA and first.onset is Onset.WASL
    assert [mark.role for mark in first.marks[:2]] == [
        "wasl_link_haraka", "wasl_start_quality",
    ]
    assert onset_offsets == {0, 1}
    assert [grapheme.source.offset for grapheme in reading.graphemes[:3]] == [0, 1, 2]


def test_the_wasl_mark_supplies_the_start_quality_over_the_visible_haraka():
    # اِ۬لْحَمْدُ writes a kasra-shaped linking vowel, yet its mark starts the
    # article with fatha; the haraka never becomes the start.
    entry, reading = _reading((1, 2, 1))
    quality = _evidence_at(reading, 2, SlotFact.VOWEL_QUALITY)

    assert entry.text[1] == "ِ"
    assert quality.value == Nucleus.short(Quality.A)


def test_a_bare_glide_after_the_wasl_sequence_is_the_silenced_qata_hamza():
    entry, reading = _reading((10, 79, 3))  # source 10:79:3 اُ۪يتُونِے
    second = reading.clusters[1]

    assert entry.text[3] == "ي"
    assert second.letter is CanonLetter.HAMZA


def test_an_unreviewed_initial_alif_scalar_fails_projection():
    # U+0671 is not a scalar of this source; a rewritten onset must fail
    # rather than receive a best-effort start.
    location = Location(1, 2, 1)
    with pytest.raises(InventoryError):
        script_adapter(Script.UTHMANI).read(
            location.verse, ((location, "ٱلْحَمْدُ"),)
        )


def test_alternate_tanwin_supplies_the_same_canonical_nunation_fact():
    entry, reading = _reading((2, 178, 20))  # شَےْءٞ
    offset = entry.text.index("ٞ")
    evidence = _evidence_at(reading, offset, SlotFact.VOWEL_QUALITY)

    assert evidence.derivation == "tanween"
    assert reading.clusters[evidence.cluster].letter is CanonLetter.HAMZA


def test_mini_meem_attests_composite_tanwin_without_becoming_a_meem():
    entry, reading = _reading((2, 10, 9))  # اَلِيمُۢ
    offset = entry.text.index("ۢ")
    attestation = reading.attestations[0]

    assert attestation.offset == offset
    assert reading.clusters[attestation.cluster].letter is CanonLetter.MEEM
    assert reading.clusters[attestation.cluster].mark("dammatan") is not None
    assert sum(cluster.letter is CanonLetter.MEEM for cluster in reading.clusters) == 1


def test_reversed_alif_fathatan_stays_on_the_preceding_letter():
    entry, reading = _reading((2, 10, 6))  # مَرَضاٗ
    offset = entry.text.index("ٗ")
    evidence = _evidence_at(reading, offset, SlotFact.VOWEL_QUALITY)

    assert entry.text[offset - 1] == "ا"
    assert reading.clusters[evidence.cluster].letter is CanonLetter.DAD
    assert reading.clusters[evidence.cluster + 1].letter is CanonLetter.ALIF


def test_mini_meem_after_the_iwad_alif_attaches_to_the_tanwin_host():
    entry, reading = _reading((2, 95, 3))  # أَبَداَۢ
    attestation = reading.attestations[0]

    assert entry.text[attestation.offset - 2:attestation.offset + 1] == "اَۢ"
    assert reading.clusters[attestation.cluster].letter is CanonLetter.DAL
    assert reading.clusters[attestation.cluster + 1].letter is CanonLetter.ALIF


def test_plural_alif_sukun_is_a_source_backed_silence_sign():
    entry, reading = _reading((2, 16, 3))  # اَ۪شْتَرَوُاْ
    sukun = entry.text.rindex("ْ")
    decoration = next(row for row in reading.decorations if row.offset == sukun)

    assert decoration.silences
    assert reading.clusters[decoration.cluster].letter is CanonLetter.ALIF


def test_sounded_yaa_before_combining_hamza_remains_a_separate_glide():
    entry, reading = _reading((2, 48, 8))  # شَئْاٗ
    letters = tuple(cluster.letter for cluster in reading.clusters)

    assert "ئْ" in entry.text
    assert letters[:3] == (
        CanonLetter.SHEEN, CanonLetter.YA, CanonLetter.HAMZA,
    )


def test_dagger_before_standalone_hamza_is_a_seat_not_a_length():
    entry, reading = _reading((2, 72, 4))  # فَادَّٰرَٰءْتُمْ
    seat = entry.text.index("ٰء")
    decoration = next(row for row in reading.decorations if row.offset == seat)

    assert reading.clusters[decoration.cluster].letter is CanonLetter.RA
    assert not any(
        row.offset == seat and row.fact is SlotFact.VOWEL_LENGTH
        for row in reading.evidence
    )
    assert reading.clusters[decoration.cluster + 1].letter is CanonLetter.HAMZA


def test_yeh_barree_is_preserved_as_source_but_projects_to_yaa():
    entry, reading = _reading((2, 10, 1))  # فِے
    barree = next(grapheme for grapheme in reading.graphemes if grapheme.char == "ے")

    assert reading.clusters[-1].letter is CanonLetter.YA
    assert barree.source.location == entry.sources[0].location
    assert barree.source.offset == entry.text.index("ے")
