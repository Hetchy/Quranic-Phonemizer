"""Sequence-aware projection of the selected King Fahd Warsh script."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from quranic_phonemizer.model.address import Location, Script
from quranic_phonemizer.model.canon import (
    Annotation,
    CanonLetter,
    Nucleus,
    Onset,
    Quality,
)
from quranic_phonemizer.model.inscription import SlotFact
from quranic_phonemizer.orthography.inventory import InventoryError
from quranic_phonemizer.riwayat.warsh import naql_script
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
    # An alif form this script never writes must fail rather than
    # receive a best-effort start.
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


def _reading_pair(first: tuple[int, int, int], second: tuple[int, int, int]):
    one, two = Location(*first), Location(*second)
    entries = (corpus().entries[one], corpus().entries[two])
    return entries, script_adapter(Script.UTHMANI).read(
        one.verse, ((one, entries[0].text), (two, entries[1].text))
    )


def test_a_word_initial_bare_alif_haraka_supplies_the_latent_qata():
    entry, reading = _reading((23, 1, 2))  # اَفْلَحَ
    first = reading.clusters[0]
    quality = _evidence_at(reading, 1, SlotFact.VOWEL_QUALITY)

    assert entry.text[:2] == "اَ"
    assert first.letter is CanonLetter.HAMZA and first.onset is None
    assert quality.value == Nucleus.short(Quality.A)


def test_the_damm_stroke_after_a_bare_alif_is_the_qata_damm():
    entry, reading = _reading((77, 12, 3))  # ا۟جِّلَتْ
    first = reading.clusters[0]
    quality = _evidence_at(reading, 1, SlotFact.VOWEL_QUALITY)

    assert entry.text[1] == "۟"
    assert first.letter is CanonLetter.HAMZA and first.onset is None
    assert quality.value == Nucleus.short(Quality.U)


@pytest.mark.parametrize(("ref", "quality"), (
    ((5, 41, 24), Quality.A),
    ((2, 161, 7), Quality.U),
    ((6, 158, 23), Quality.I),
    ((10, 53, 5), Quality.I),
))
def test_initial_badals_are_deferred_from_ordinary_naql(ref, quality):
    entry, _ = _reading(ref)
    assert naql_script.latent_qata_badal_quality(entry.text) is quality
    assert naql_script.latent_qata_quality(entry.text) is None


def test_the_same_stroke_in_a_wasl_sequence_stays_the_start_quality():
    entry, reading = _reading((7, 195, 21))  # اُ۟دْعُواْ
    first = reading.clusters[0]
    quality = _evidence_at(reading, 2, SlotFact.VOWEL_QUALITY)

    assert entry.text[2] == "۟"
    assert first.letter is CanonLetter.HAMZA and first.onset is Onset.WASL
    assert quality.value == Nucleus.short(Quality.U)


def test_the_eased_aal_spelling_is_not_claimed_by_the_latent_family():
    entry, reading = _reading((15, 61, 3))  # جَآءَ ا۟لَ
    assert entry.text.startswith("ا۟لَ")
    assert not any(
        row.offset == 1 and row.fact is SlotFact.VOWEL_QUALITY
        for row in reading.evidence
    )


def test_the_moved_host_haraka_demotes_to_a_naql_witness():
    (host, _), reading = _reading_pair((23, 1, 1), (23, 1, 2))  # قَدَ اَفْلَحَ
    fatha = 3
    decoration = next(row for row in reading.decorations if row.offset == fatha)

    assert host.text[fatha] == "َ"
    assert reading.clusters[decoration.cluster].letter is CanonLetter.DAL
    assert not any(
        row.offset == fatha and row.fact is SlotFact.VOWEL_QUALITY
        for row in reading.evidence
    )
    assert any(row.offset == fatha for row in reading.attestations)


def test_the_latent_qata_keeps_its_full_shape_for_restoration():
    # The projection never bakes the joined outcome in: the qata's letter and
    # vowel stay canonical, so ibtidaa and a stop before it restore the hamza.
    _, reading = _reading_pair((23, 1, 1), (23, 1, 2))
    qata = next(
        cluster for cluster in reading.clusters if cluster.word == 1
    )
    assert qata.letter is CanonLetter.HAMZA
    assert qata.mark("fatha") is not None


def test_the_article_rasm_alif_supplies_the_carried_naql_annotation():
    entry, reading = _reading((2, 11, 7))  # اِ۬لَارْضِ
    alif = 5
    annotation = _evidence_at(reading, alif, SlotFact.TAJWEED_MARK)

    assert entry.text[alif] == "ا"
    assert reading.clusters[annotation.cluster].letter is CanonLetter.LAM
    assert annotation.value is Annotation.NAQL


def test_a_long_article_base_supplies_its_length_on_the_lam():
    entry, reading = _reading((2, 4, 10))  # وَبِالَاخِرَةِ
    wasl = reading.clusters[2]
    quality = _evidence_at(reading, 6, SlotFact.VOWEL_QUALITY)
    annotation = _evidence_at(reading, 7, SlotFact.TAJWEED_MARK)

    assert entry.text[4:8] == "الَا"
    assert wasl.letter is CanonLetter.HAMZA and wasl.onset is Onset.WASL
    assert quality.value == Nucleus.long(Quality.A)
    assert annotation.value is Annotation.NAQL


def test_an_ordinary_lam_alif_shape_is_not_an_article_naql():
    entry, reading = _reading((20, 45, 1))  # قَالَا
    assert not any(
        row.fact is SlotFact.TAJWEED_MARK for row in reading.evidence
    )
