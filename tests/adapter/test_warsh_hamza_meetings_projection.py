"""Selected Warsh sequences that supply adjacent qata structure."""

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality


def _span(ref: str, words: tuple[int, ...]):
    surah, ayah = (int(part) for part in ref.split(":"))
    package = recitation(Riwayah.WARSH)
    verse = VerseRef(surah, ayah)
    source = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, source))
    return tuple((source[word - 1][1], built.score.words[word - 1]) for word in words)


def _word(ref: str, word: int):
    return _span(ref, (word,))[0][1]


@pytest.mark.parametrize(("ref", "word", "text", "qualities"), (
    ("2:6", 6, "ءَآنذَرْتَهُمُۥٓ", (Quality.A, Quality.A)),
    ("6:19", 19, "أَئِنَّكُمْ", (Quality.A, Quality.I)),
    ("3:15", 2, "اَوْ۟نَبِّئُكُم", (Quality.A, Quality.U)),
    ("41:44", 9, "ءَآعْجَمِيّٞ", (Quality.A, Quality.A)),
    ("43:58", 2, "ءَاٰ۬لِهَتُنَا", (Quality.A, Quality.A)),
))
def test_one_word_selected_families_project_two_qata(ref, word, text, qualities):
    source, projected = _span(ref, (word,))[0]
    assert source == text
    slots = [slot for slot in projected.slots if slot.letter is CanonLetter.HAMZA]
    assert tuple(slot.nucleus.quality for slot in slots[:2]) == qualities


def test_second_u_family_does_not_repurpose_its_later_lexical_hamza():
    source, projected = _span("3:15", (2,))[0]

    assert source == "اَوْ۟نَبِّئُكُم"
    assert tuple(slot.letter for slot in projected.slots) == (
        CanonLetter.HAMZA,
        CanonLetter.HAMZA,
        CanonLetter.NOON,
        CanonLetter.BA,
        CanonLetter.HAMZA,
        CanonLetter.KAF,
        CanonLetter.MEEM,
    )
    assert tuple(
        slot.onset for slot in projected.slots
        if slot.letter is CanonLetter.HAMZA
    ) == (Onset.PLAIN, Onset.TASHIL, Onset.PLAIN)


def test_registered_right_qata_is_restored_when_started_without_its_left_word():
    source, projected = _span("33:24", (9,))[0]

    assert source == "اوْ"
    assert tuple(slot.letter for slot in projected.slots) == (
        CanonLetter.HAMZA,
        CanonLetter.WAW,
    )
    assert projected.slots[0].nucleus.quality is Quality.A


def test_aimma_projects_an_eased_second_qata():
    source, projected = _span("9:12", (11,))[0]
    assert source == "أَي۪مَّةَ"
    slots = [slot for slot in projected.slots if slot.letter is CanonLetter.HAMZA]
    assert tuple(slot.onset for slot in slots[:2]) == (Onset.PLAIN, Onset.TASHIL)


@pytest.mark.parametrize(("ref", "words", "text", "qualities"), (
    ("4:43", (27, 28), ("جَآءَ", "احَدٞ"), (Quality.A, Quality.A)),
    ("4:22", (7, 8), ("اَ۬لنِّسَآءِ", "الَّا"), (Quality.I, Quality.I)),
    ("46:32", (14, 15), ("أَوْلِيَآءُۖ", "اوْلَٰٓئِكَ"), (Quality.U, Quality.U)),
    ("49:9", (17, 18), ("تَفِےٓءَ", "ا۪لَىٰٓ"), (Quality.A, Quality.I)),
    ("23:44", (7, 8), ("جَآءَ", "اُ۟مَّةٗ"), (Quality.A, Quality.U)),
    ("2:235", (9, 10), ("اِ۬لنِّسَآءِ", "اَ۬وَ"), (Quality.I, Quality.A)),
    ("11:44", (5, 6), ("وَيَٰسَمَآءُ", "اَ۬قْلِعِےۖ"), (Quality.U, Quality.A)),
    ("19:7", (1, 2), ("يَٰزَكَرِيَّآءُ", "اِ۪نَّا"), (Quality.U, Quality.I)),
    ("15:61", (2, 3), ("جَآءَ", "ا۟لَ"), (Quality.A, Quality.A)),
    ("2:31", (12, 13), ("هَٰٓؤُلَآءِ", "ان"), (Quality.I, Quality.I)),
))
def test_across_word_selected_sequences_project_qata_pairs(
    ref, words, text, qualities,
):
    span = _span(ref, words)
    assert tuple(source for source, _ in span) == text
    left, right = (projected for _, projected in span)
    first = next(slot for slot in reversed(left.slots) if slot.letter is CanonLetter.HAMZA)
    second = next(slot for slot in right.slots if slot.letter is CanonLetter.HAMZA)
    assert (first.onset, second.onset) == (Onset.PLAIN, Onset.PLAIN)
    assert (first.nucleus.quality, second.nucleus.quality) == qualities


def test_a_real_wasl_sequence_is_not_claimed_as_a_meeting():
    first = _word("1:2", 1).slots[0]
    assert first.letter is CanonLetter.HAMZA
    assert first.onset is Onset.WASL
