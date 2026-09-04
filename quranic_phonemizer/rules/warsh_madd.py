"""Warsh-specific madd classifications and lexical exclusions."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Classify, Phase, Plan, Verdict, mint
from ..model.address import BoundaryPlan, Location, SlotId
from ..model.canon import Annotation, Onset, Quality, Rule
from ..model.canon import CanonLetter as L
from ..model.performance import Aspect, Occurrence
from .madd import _madd_of


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


@dataclass(frozen=True, slots=True)
class MaddMimAlJam:
    """Classify the joined-only long of the plural-pronoun mim.

    The effective madd beside it remains munfasil; this rule names why the
    carrier exists, in parallel with pronoun-haa silah.
    """

    rule: Rule = Rule.MADD_MIM_AL_JAM
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({Annotation.MIM_AL_JAM})
    emits: frozenset = frozenset({Rule.MADD_MIM_AL_JAM})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if (
            slot is None
            or Annotation.MIM_AL_JAM not in slot.annotations
            or not slot.nucleus.is_joined_only_long
            or slot.nucleus.quality is not Quality.U
            or _madd_of(near, plan, at, boundaries) is None
        ):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_MIM_AL_JAM, at), Rule.MADD_MIM_AL_JAM, (at,)
            ),
            (),
        )


@dataclass(frozen=True, slots=True)
class MaddYaaZawaid:
    """Classify a yaa-zawaid long retained only in a joined reading.

    Its effective madd remains tabii, munfasil, or badal. The exceptional
    consonantal Naml yaa is annotated by the projection but is not a madd.
    """

    rule: Rule = Rule.MADD_YAA_ZAWAID
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({Annotation.YAA_ZAWAID})
    emits: frozenset = frozenset({Rule.MADD_YAA_ZAWAID})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if (
            slot is None
            or Annotation.YAA_ZAWAID not in slot.annotations
            or not slot.nucleus.is_joined_only_long
            or slot.nucleus.quality is not Quality.I
            or _madd_of(near, plan, at, boundaries) is None
        ):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_YAA_ZAWAID, at), Rule.MADD_YAA_ZAWAID, (at,)
            ),
            (),
        )


__all__ = [
    "MaddLeenMahmuz",
    "MaddMimAlJam",
    "MaddYaaZawaid",
    "StartedBadal",
]
