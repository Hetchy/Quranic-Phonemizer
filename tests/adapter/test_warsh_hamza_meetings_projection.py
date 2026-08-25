"""Selected Warsh sequences that supply adjacent qata structure."""

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality


def _word(ref: str, word: int):
    surah, ayah = (int(part) for part in ref.split(":"))
    package = recitation(Riwayah.WARSH)
    verse = VerseRef(surah, ayah)
    built = package.build(package.read(Script.UTHMANI, verse, package.words(verse)))
    return built.score.words[word - 1]


@pytest.mark.parametrize(("ref", "word", "qualities"), (
    ("2:6", 6, (Quality.A, Quality.A)),
    ("6:19", 19, (Quality.A, Quality.I)),
    ("3:15", 2, (Quality.A, Quality.U)),
    ("41:44", 9, (Quality.A, Quality.A)),
))
def test_one_word_selected_families_project_two_qata(ref, word, qualities):
    slots = [slot for slot in _word(ref, word).slots if slot.letter is CanonLetter.HAMZA]
    assert tuple(slot.nucleus.quality for slot in slots[:2]) == qualities


def test_aimma_projects_an_eased_second_qata():
    slots = [slot for slot in _word("9:12", 11).slots if slot.letter is CanonLetter.HAMZA]
    assert tuple(slot.onset for slot in slots[:2]) == (Onset.PLAIN, Onset.TASHIL)


def test_a_real_wasl_sequence_is_not_claimed_as_a_meeting():
    first = _word("1:2", 1).slots[0]
    assert first.letter is CanonLetter.HAMZA
    assert first.onset is Onset.WASL
