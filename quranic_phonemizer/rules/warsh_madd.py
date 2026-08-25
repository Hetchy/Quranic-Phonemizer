"""Warsh-specific madd classifications and lexical exclusions."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Classify, Phase, Plan, Verdict, mint
from ..model.address import BoundaryPlan, Location, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Quality, Rule
from ..model.performance import Aspect, Occurrence


@dataclass(frozen=True, slots=True)
class StartedBadal:
    """Name the start-only badal created after a realized wasl onset."""

    rule: Rule = Rule.MADD_BADAL
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({Onset.WASL})
    emits: frozenset = frozenset({Rule.MADD_BADAL})

    def look(self, near: Neighbourhood, plan: Plan, at: SlotId,
             boundaries: BoundaryPlan) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if (
            slot is None or word is None or slot.onset is not Onset.WASL
            or not boundaries.started_on(word) or not near.first_of_word(at)
            or not plan.relengthened_long(at)
        ):
            return None
        root = near.after(at)
        if root is None or root.letter is not L.HAMZA or not root.nucleus.is_silent:
            return None
        return Verdict(
            Occurrence(mint(Rule.MADD_BADAL, at), Rule.MADD_BADAL,
                       (at, root.id)),
            (Classify(at, Aspect.VOWEL),),
        )


@dataclass(frozen=True, slots=True)
class MaddLeenMahmuz:
    """A same-word fatha plus sakin glide plus hamza, less two exclusions."""

    excluded: frozenset[Location] = frozenset()
    rule: Rule = Rule.MADD_LEEN_MAHMUZ
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})
    emits: frozenset = frozenset({Rule.MADD_LEEN_MAHMUZ})

    def look(self, near: Neighbourhood, plan: Plan, at: SlotId,
             boundaries: BoundaryPlan) -> Verdict | None:
        del plan, boundaries
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if near.score.words[word].location in self.excluded:
            return None
        if not slot.nucleus.is_silent or slot.onset is Onset.GEMINATE:
            return None
        before, following = near.before(at), near.after(at)
        if before is None or following is None:
            return None
        if near.word_of(before.id) != word or near.word_of(following.id) != word:
            return None
        if not before.nucleus.is_short or before.nucleus.quality is not Quality.A:
            return None
        if following.letter is not L.HAMZA:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_LEEN_MAHMUZ, at), Rule.MADD_LEEN_MAHMUZ,
                (at,), (following.id,),
            ),
            (Classify(at, Aspect.CONSONANT),),
        )


__all__ = ["MaddLeenMahmuz", "StartedBadal"]
