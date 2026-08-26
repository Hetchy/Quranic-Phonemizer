"""Classifiers for facts already decided on the Slot: imala, tashil and
ishmam. Each gets a named occurrence so a projection can find it; none of
them emits an effect on the sound.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Annotation, Onset, Quality, Rule, VowelForm
from ..model.performance import Aspect, Occurrence, Vowel
from .tafkheem import Weight


def _classification(rule: Rule, at: SlotId) -> Verdict:
    return Verdict(Occurrence(mint(rule, at), rule, (at,)), ())


@dataclass(frozen=True, slots=True)
class Inclination:
    """Classify the effective sounded taqlil or kubra quality."""

    rule: Rule = Rule.TAQLIL
    phase: Phase = Phase.COLOUR
    emits: frozenset = frozenset({Rule.TAQLIL, Rule.IMALA})
    triggers: frozenset = frozenset({VowelForm.SHORT, VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or plan.merged_away(at, Aspect.VOWEL):
            return None
        state = (
            slot.nucleus.stopped
            if boundaries.stopped_on(word)
            else slot.nucleus.joined
        )
        rule = {
            Quality.TAQLIL: Rule.TAQLIL,
            Quality.KUBRA: Rule.IMALA,
        }.get(state.quality)
        if rule is None:
            return None
        realized = next(
            (
                effect.sound for effect in plan.effects()
                if isinstance(effect, Realize)
                and effect.slot == at
                and effect.aspect is Aspect.VOWEL
            ),
            None,
        )
        if isinstance(realized, Vowel) and realized.quality is not state.quality:
            return None
        return _classification(rule, at)


@dataclass(frozen=True, slots=True)
class CanonicalColour:
    """Imala, tashil and ishmam in one classifier: each is a quality or
    onset the slot already carries, so the same lookup finds all three.
    """

    rule: Rule = Rule.IMALA
    phase: Phase = Phase.COLOUR
    emits: frozenset = frozenset({Rule.IMALA, Rule.TASHIL, Rule.ISHMAM})
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
            following = near.after(at)
            if following is not None and following.letter is L.NOON:
                return _classification(Rule.ISHMAM, following.id)
        return None


@dataclass(frozen=True, slots=True)
class Tarqeeq:
    """A raa that is not heavy is light; taught explicitly, not as an absence.

    Scoped to raa -- the lam's light case would fire on every lam in the text.
    """

    weight: Weight = field(default_factory=Weight)
    rule: Rule = Rule.TARQEEQ
    phase: Phase = Phase.COLOUR
    triggers: frozenset = field(default=frozenset({L.RA}))
    emits: frozenset = frozenset({Rule.TARQEEQ})

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


__all__ = ["CanonicalColour", "Inclination", "Tarqeeq"]
