"""Qalqala: the echo on a quiescent plosive, and its three degrees.

The degrees are separate Rule members because a projection that cannot say
which one fired is not a tajweed projection.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter, Onset, Rule
from ..model.performance import Aspect, Degree, Occurrence, Participants, Release
from .tables import Pairs

#: The rule each degree is minted under, keyed the other way for the sound.
_DEGREE_OF_RULE = {
    Rule.QALQALA_SUGHRA: Degree.SUGHRA,
    Rule.QALQALA_KUBRA: Degree.KUBRA,
    Rule.QALQALA_AKBAR: Degree.AKBAR,
}


@dataclass(frozen=True, slots=True)
class Qalqala:
    letters: frozenset[CanonLetter]
    pairs: Pairs
    rule: Rule = Rule.QALQALA_SUGHRA
    phase: Phase = Phase.RELEASE
    triggers: frozenset = field(default=frozenset())

    def __post_init__(self) -> None:
        object.__setattr__(self, "triggers", frozenset(self.letters))

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if plan.merged_away(at, Aspect.CONSONANT) or self._consumed(near, at, slot):
            return None  # an assimilated closure is held, never released

        # The echo needs a real closure: either canonically silent, or
        # silenced by a BOUNDARY rule. A long final vowel is neither.
        canonically = slot.nucleus.is_silent
        silenced = plan.merged_away(at, Aspect.VOWEL)
        if not (canonically or silenced):
            return None

        if boundaries.stopped_on(word) and _is_last(near, at, word):
            degree = (
                Rule.QALQALA_AKBAR
                if slot.onset is Onset.GEMINATE
                else Rule.QALQALA_KUBRA
            )
        else:
            degree = Rule.QALQALA_SUGHRA

        return Verdict(
            Occurrence(mint(degree, at), degree, Participants(at)),
            (Realize(at, Aspect.VOWEL, Release(_DEGREE_OF_RULE[degree])),),
        )

    def _consumed(self, near: Neighbourhood, at: SlotId, slot) -> bool:
        """A closure the next consonant assimilates: identical, close or
        homorganic, and joined -- the same pair table `Idgham` reads."""
        if not slot.nucleus.is_silent:
            return False
        following = near.after(at)
        if following is None:
            return False
        if slot.letter is following.letter:
            return True
        return self.pairs.of(slot.letter, following.letter) is not None


def _is_last(near: Neighbourhood, at: SlotId, word: int) -> bool:
    slots = near.score.words[word].slots
    return bool(slots) and slots[-1].id == at
