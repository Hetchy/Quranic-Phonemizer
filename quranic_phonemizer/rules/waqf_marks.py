"""Boundary rules for source-backed pronunciation marks."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import Annotation, CanonLetter, Rule
from ..model.performance import Occurrence

_IQLAB_MARK_VARIANT = 2


@dataclass(frozen=True, slots=True)
class WaqfIqlabMarkDrop:
    """A native iqlab mark on final noon is inactive at waqf."""

    rule: Rule = Rule.WAQF_DIACRITIC_DROP
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.NOON})
    emits: frozenset = frozenset({Rule.WAQF_DIACRITIC_DROP})

    def look(
        self,
        near: Neighbourhood,
        plan: Plan,
        at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if (
            slot is None
            or word is None
            or Annotation.IQLAB_WITNESS not in slot.annotations
            or not near.last_of_word(at)
            or not boundaries.stopped_on(word)
        ):
            return None
        occurrence = Occurrence(
            mint(Rule.WAQF_DIACRITIC_DROP, at, _IQLAB_MARK_VARIANT),
            Rule.WAQF_DIACRITIC_DROP,
            (at,),
            boundary=word,
        )
        return Verdict(occurrence, ())


__all__ = ["WaqfIqlabMarkDrop"]
