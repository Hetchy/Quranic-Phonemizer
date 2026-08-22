"""A hamza seat has no draft of its own when `canon.build` visits it, so its
decoration must wait for the hamza's, not fall back to the slot before it.
"""
from __future__ import annotations

from quranic_phonemizer.canon.build import Provenance, _flush_pending, _not_a_slot
from quranic_phonemizer.canon.derive import Context, lexeme
from quranic_phonemizer.canon.draft import _Draft
from quranic_phonemizer.canon.scribe import Scribe
from quranic_phonemizer.model.address import VerseRef
from quranic_phonemizer.model.canon import CanonLetter
from quranic_phonemizer.orthography.adapter import Cluster


def _seat_and_hamza() -> tuple[Context, Cluster]:
    seat = Cluster(base="و", offset=10, letter=CanonLetter.WAW,
                   marked_script=True)
    hamza = Cluster(base="ء", offset=11, letter=CanonLetter.HAMZA)
    context = Context(
        clusters=(seat, hamza), index=0, word_bounds=(0, 2),
        previous_nucleus=None, previous_letter=None, lexicon=None,
    )
    return context, seat


def test_hamza_seat_is_detected_on_a_bare_marked_script_cluster():
    context, _ = _seat_and_hamza()
    assert lexeme.hamza_seat(context)


def test_a_hamza_seat_decorates_nothing_until_the_hamza_gets_a_draft():
    context, seat = _seat_and_hamza()
    scribe = Scribe(VerseRef(1, 1))
    track = Provenance()
    drafts: list[_Draft] = []
    pending: list[int] = []

    consumed = _not_a_slot(CanonLetter.WAW, False, context, seat, (), drafts,
                           track, scribe, pending)

    assert consumed
    assert pending == [seat.offset]
    assert scribe.decorates == []


def test_flushing_pending_lands_the_seat_on_the_hamzas_draft():
    context, seat = _seat_and_hamza()
    scribe = Scribe(VerseRef(1, 1))
    track = Provenance()
    drafts: list[_Draft] = []
    pending: list[int] = []
    _not_a_slot(CanonLetter.WAW, False, context, seat, (), drafts, track,
               scribe, pending)

    drafts.append(_Draft(letter=CanonLetter.HAMZA))
    _flush_pending(pending, drafts, 0, scribe, track)

    assert scribe.decorates == [(seat.offset, drafts[0].uid)]
    assert pending == []
