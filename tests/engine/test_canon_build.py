"""What `canon.build` requires of its caller, and what it promises back."""
from __future__ import annotations

import inspect

import pytest

from quranic_phonemizer.canon.build import build
from quranic_phonemizer.canon.draft import _Draft
from quranic_phonemizer.canon.scribe import OrphanedEdgeError, Scribe
from quranic_phonemizer.model.address import Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter
from quranic_phonemizer.model.inscription import SlotFact

#: The muqattaat openings, the only place a pass replaces a whole word's drafts.
COMPACT = ((2, 1), (3, 1), (19, 1), (42, 1))


def _reading(hafs, surah: int = 112, ayah: int = 2):
    verse = VerseRef(surah, ayah)
    return hafs.read(Script.UTHMANI, verse, hafs.words(verse))


def test_a_pass_list_never_arrives_by_default(hafs) -> None:
    """A riwayah must explicitly supply its passes; they are not inferred."""
    assert inspect.signature(build).parameters["passes"].default is inspect.Parameter.empty
    with pytest.raises(TypeError, match="passes"):
        build(_reading(hafs), lexicon=hafs.lexicon, ledger=hafs.ledger)


# -- draft identity ---

def test_two_drafts_alike_in_every_field_are_still_two_drafts() -> None:
    """`list.remove` and `list.index` compare by value, so without this a
    span could be spliced at an identical draft in an earlier word."""
    one, other = _Draft(letter=CanonLetter.ALIF), _Draft(letter=CanonLetter.ALIF)
    assert one != other
    drafts = [one, other]
    assert drafts.index(other) == 1
    drafts.remove(other)
    assert drafts == [one]


@pytest.mark.parametrize("surah,ayah", COMPACT)
def test_a_replaced_span_leaves_no_edge_behind(hafs, surah, ayah) -> None:
    """The muqattaat pass drops a word's drafts and spells the letter names
    in their place. Every spelled slot is reached by an edge."""
    verse = VerseRef(surah, ayah)
    built = hafs.build(hafs.read(Script.UTHMANI, verse, hafs.words(verse)))
    reached = {
        spelling.slot.ordinal
        for spelling in built.inscription.spellings
        if getattr(spelling, "slot", None) is not None
    }
    spelled = {slot.id.ordinal for slot in built.score.words[0].slots}
    assert spelled <= reached, f"unreached: {sorted(spelled - reached)}"


def test_an_edge_into_a_dropped_draft_raises(hafs) -> None:
    """An edge into a dropped draft raises OrphanedEdgeError."""
    verse = VerseRef(112, 2)
    reading = hafs.read(Script.UTHMANI, verse, hafs.words(verse))
    scribe = Scribe(verse)
    scribe.evidence(0, _Draft(letter=CanonLetter.ALIF), SlotFact.LETTER)
    with pytest.raises(OrphanedEdgeError, match="no slot came from"):
        scribe.finish(reading, [], {})


def test_withdrawing_a_draft_takes_all_three_kinds_of_edge(hafs) -> None:
    verse = VerseRef(112, 2)
    draft, kept = _Draft(letter=CanonLetter.ALIF), _Draft(letter=CanonLetter.MEEM)
    scribe = Scribe(verse)
    for subject in (draft, kept):
        scribe.evidence(0, subject, SlotFact.LETTER)
        scribe.decoration(1, subject)
        scribe.attestation(2, subject)
    scribe.withdraw([draft])
    assert [row[1] for row in scribe.evidences] == [kept.uid]
    assert [row[1] for row in scribe.decorates] == [kept.uid]
    assert [row[1] for row in scribe.attests] == [kept.uid]
