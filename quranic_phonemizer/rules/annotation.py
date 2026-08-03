"""Classifiers for facts already decided on the Slot: imala, tashil,
ishmam and silah. Each gets a named occurrence so a projection can find
it; none of them emits an effect on the sound.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Plan, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import (
    Annotation,
    NucleusKind,
    Onset,
    Phase,
    Rule,
)
from ..model.performance import Occurrence, Participants
from .tafkheem import Weight


def _classification(rule: Rule, at: SlotId, *others: SlotId) -> Verdict:
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, *others))), ()
    )


@dataclass(frozen=True, slots=True)
class CanonicalColour:
    """Imala, tashil and ishmam in one classifier: each is a quality or
    onset the slot already carries, so the same lookup finds all three.
    """

    rule: Rule = Rule.IMALA
    phase: Phase = Phase.COLOUR
    triggers: frozenset = frozenset(
        {Annotation.IMALA, Annotation.ISHMAM, Onset.TASHIL}
    )

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None:
            return None
        if slot.onset is Onset.TASHIL:
            return _classification(Rule.TASHIL, at)
        if Annotation.IMALA in slot.annotations:
            return _classification(Rule.IMALA, at)
        if Annotation.ISHMAM in slot.annotations:
            return _classification(Rule.ISHMAM, at)
        return None


@dataclass(frozen=True, slots=True)
class Silah:
    """The pronoun haa's vowel: long in wasl, absent at pause.

    Records that this is silah rather than an ordinary long vowel.
    """

    rule: Rule = Rule.SILAH
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({NucleusKind.SILAH})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.nucleus.kind is not NucleusKind.SILAH:
            return None
        if boundaries.stopped_on(word):
            # At a pause the silah is absent; `WaqfEnding` accounts for the slot.
            return None
        return _classification(Rule.SILAH, at)


@dataclass(frozen=True, slots=True)
class Tarqeeq:
    """A raa that is not heavy is light; taught explicitly, not as an absence.

    Scoped to raa -- the lam's light case would fire on every lam in the text.
    """

    weight: Weight = field(default_factory=Weight)
    rule: Rule = Rule.TARQEEQ
    phase: Phase = Phase.COLOUR
    triggers: frozenset = field(default=frozenset({L.RA}))

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if slot is None or slot.letter is not L.RA:
            return None
        if self.weight.is_heavy(near, slot, plan, boundaries):
            return None
        return _classification(Rule.TARQEEQ, at)
