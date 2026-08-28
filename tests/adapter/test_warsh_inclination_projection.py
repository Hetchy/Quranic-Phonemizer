"""Selected-script sequence fixtures for Warsh inclination evidence."""
from __future__ import annotations

from quranic_phonemizer.model.address import Location, Script
from quranic_phonemizer.model.canon import CanonLetter, Nucleus, Onset, Quality
from quranic_phonemizer.model.inscription import SlotFact
from quranic_phonemizer.riwayat.warsh.resources import corpus, script_adapter


def _reading(ref: tuple[int, int, int]):
    location = Location(*ref)
    entry = corpus().entries[location]
    reading = script_adapter(Script.UTHMANI).read(
        location.verse, ((location, entry.text),)
    )
    return entry, reading


def _mark(reading, offset: int):
    return next(
        mark
        for cluster in reading.clusters
        for mark in cluster.marks
        if mark.offset == offset
    )


def test_a_mark_before_a_maqsura_is_reviewed_inclination_evidence():
    entry, reading = _reading((2, 16, 5))  # بِالْهُد۪ىٰ
    offset = entry.text.index("۪")

    assert entry.text[offset:offset + 3] == "۪ىٰ"
    assert _mark(reading, offset).role == "inclination_witness"
    assert any(
        row.offset == offset
        and row.fact is SlotFact.VOWEL_QUALITY
        and row.value == Nucleus.short(Quality.A)
        for row in reading.evidence
    )


def test_a_marked_yaa_dagger_sequence_is_an_alif_carrier_not_a_glide():
    entry, reading = _reading((3, 151, 15))  # وَمَأْو۪يٰهُمُ
    offset = entry.text.index("۪")
    host = next(
        cluster
        for cluster in reading.clusters
        if cluster.offset < offset
        and cluster.marks
        and cluster.marks[-1].offset == offset
    )
    carrier = reading.clusters[reading.clusters.index(host) + 1]

    assert entry.text[offset:offset + 3] == "۪يٰ"
    assert _mark(reading, offset).role == "inclination_witness"
    assert carrier.letter is CanonLetter.ALIF


def test_the_taha_witness_is_an_opening_register_sequence():
    entry, reading = _reading((20, 1, 1))  # طَه۪ۖ
    offset = entry.text.index("۪")

    assert _mark(reading, offset).role == "inclination_witness"
    assert reading.clusters[-1].letter is CanonLetter.HEH


def test_both_raa_seen_marks_are_inclination_witnesses():
    entry, reading = _reading((6, 76, 5))  # source 6:77:5 ر۪ء۪ا
    offsets = [index for index, char in enumerate(entry.text) if char == "۪"]

    assert [_mark(reading, offset).role for offset in offsets] == [
        "inclination_witness", "inclination_witness",
    ]


def test_an_aimma_mark_remains_hamza_meeting_evidence():
    entry, reading = _reading((9, 12, 11))  # أَي۪مَّةَ
    offset = entry.text.index("۪")

    assert _mark(reading, offset).role == "fatha"


def test_an_initial_alif_mark_remains_a_wasl_start_quality():
    entry, reading = _reading((2, 87, 11))  # source 2:86:11 اَ۪بْنَ
    offset = entry.text.index("۪")
    first = reading.clusters[0]

    assert _mark(reading, offset).role == "wasl_start_quality"
    assert first.letter is CanonLetter.HAMZA
    assert first.onset is Onset.WASL
