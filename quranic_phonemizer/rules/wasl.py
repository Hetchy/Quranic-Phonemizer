"""Wasl and ibtidaa: what a join or a start does to a prosthetic hamza.

Everything here reads the `BoundaryPlan`. The Score is boundary-free, so
these are the only rules that may ask where the reciter starts.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Length,
    Phase,
    Plan,
    Realize,
    Relength,
    Silence,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, Junction, SlotId
from ..model.canon import (
    CanonLetter,
    Onset,
    Quality,
    Rule,
    SlotOrigin,
    VowelForm,
)
from ..model.performance import Aspect, Occurrence, Vowel

#: A start names the helping vowel it is read with.
_START_OF: dict[Quality, Rule] = {
    Quality.A: Rule.HAMZA_WASL_FATHA,
    Quality.I: Rule.HAMZA_WASL_KASRA,
    Quality.U: Rule.HAMZA_WASL_DAMMA,
}


@dataclass(frozen=True, slots=True)
class WaslHamza:
    """The prosthetic hamza sounds only when started on.

    Its nucleus is the helping vowel: joining silences both aspects,
    starting leaves the canonical value untouched.
    """

    rule: Rule = Rule.HAMZA_WASL_SILENT
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Onset.WASL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or slot.onset is not Onset.WASL:
            return None
        if boundaries.started_on(word) and near.first_of_word(at):
            start = _START_OF[slot.nucleus.quality]
            return Verdict(
                Occurrence(
                    mint(start, at), start, (at,),
                    boundary=_junction_before(word),
                ),
                (),
            )
        return Verdict(
            Occurrence(
                mint(Rule.HAMZA_WASL_SILENT, at), Rule.HAMZA_WASL_SILENT, (at,),
                boundary=_junction_before(word),
            ),
            (Silence(at, Aspect.CONSONANT), Silence(at, Aspect.VOWEL)),
        )


@dataclass(frozen=True, slots=True)
class SoftenedHamza:
    """Two hamzas are not said in a row. Started on, the prosthetic hamza's
    vowel lengthens and carries the quiescent one -- the subject, since it
    is the hamza the length replaces -- as its madd letter."""

    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Onset.WASL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or slot.onset is not Onset.WASL:
            return None
        if not (boundaries.started_on(word) and near.first_of_word(at)):
            return None   # joined, the prosthetic hamza has no vowel to carry
        following = near.after(at)
        if (
            following is None
            or following.letter is not CanonLetter.HAMZA
            or not following.nucleus.is_silent
        ):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.IBDAL_HAMZA, following.id), Rule.IBDAL_HAMZA,
                (following.id,), boundary=_junction_before(word),
            ),
            (
                Relength(at, Length.LONG),
                Silence(following.id, Aspect.CONSONANT),
            ),
        )


@dataclass(frozen=True, slots=True)
class TanweenBeforeWasl:
    """A tanween noon grows a kasra to reach the word after it."""
    # `خَيْرٌ ٱهْبِطُوا۟` joins a quiescent noon to the quiescent letter the elided
    # prosthetic hamza leaves bare, and two of them cannot meet: the noon
    # takes the kasra that breaks them. The other half of the same repair
    # shortens a madd instead -- see `rules/madd.py::IltiqaShortening`.

    rule: Rule = Rule.ILTIQA_HARAKA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.NOON})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or slot.origin is not SlotOrigin.NUNATION:
            return None
        if not near.last_of_word(at):
            return None
        # `after` is `None` at a stop, where `TanweenDrop` owns the noon.
        following = near.after(at)
        if following is None or following.onset is not Onset.WASL:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.ILTIQA_HARAKA, at), Rule.ILTIQA_HARAKA, (at,),
                (following.id,), boundary=word,
            ),
            (Realize(at, Aspect.VOWEL, Vowel(Quality.I)),),
        )


@dataclass(frozen=True, slots=True)
class SpelledBeforeWasl:
    """A spelled-out letter grows a fatha to reach the word after it."""
    # `الٓمٓ ٱللَّهُ` joins the quiescent meem closing the opening to the quiescent
    # lam the elided prosthetic hamza leaves bare. Two of them cannot meet, and
    # the letter names of an opening take the lighter fatha where a tanween noon
    # takes a kasra -- see `TanweenBeforeWasl`. Breaking the meeting also leaves
    # the meem voweled, so the long vowel before it is no longer stopped by a
    # sakin and `MaddClass` reads it as the ordinary two counts, not madd lazim.

    rule: Rule = Rule.ILTIQA_HARAKA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({VowelForm.ABSENT})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or slot.origin is not SlotOrigin.SPELLED:
            return None
        if not slot.nucleus.is_silent or not near.last_of_word(at):
            return None
        if boundaries.after(word) is not Junction.JOIN:
            return None
        # `after` hides the word past an opening: a name is spelled rather than
        # read, so nothing carries out of it. Two quiescent letters still meet
        # in performance, and the repair is the one thing that has to see them.
        following = near.raw_after(at)
        if following is None or following.onset is not Onset.WASL:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.ILTIQA_HARAKA, at), Rule.ILTIQA_HARAKA, (at,),
                (following.id,), boundary=word,
            ),
            (Realize(at, Aspect.VOWEL, Vowel(Quality.A)),),
        )


def _junction_before(word: int) -> int:
    """A `BoundaryPlan` keys a junction by the word it falls after, so the
    one a started word reads is the word before it; -1 is the span's start."""
    return word - 1
