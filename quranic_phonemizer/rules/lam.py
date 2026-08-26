"""Lam weight from structural triggers and riwayah-owned registers."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Recolour, SoundFeature, Verdict, mint
from ..model.address import BoundaryPlan, Location, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Quality, Rule, VowelForm
from ..model.performance import Aspect, Occurrence

LamKey = tuple[Location, int]


@dataclass(frozen=True, slots=True)
class LamProfile:
    coupled_tafkheem: frozenset[LamKey] = frozenset()
    coupled_tarqeeq: frozenset[LamKey] = frozenset()
    salsal_tarqeeq: frozenset[LamKey] = frozenset()
    separated_tafkheem: frozenset[LamKey] = frozenset()
    final_waqf_tafkheem: frozenset[LamKey] = frozenset()

    def rule(self, near: Neighbourhood, at: SlotId, boundaries) -> Rule | None:
        word = near.word_of(at)
        slot = near.slot(at)
        if word is None or slot is None or slot.letter is not L.LAM:
            return None
        key = _key(near, word, at)
        if key in self.coupled_tafkheem:
            return Rule.TAFKHEEM
        if key in self.coupled_tarqeeq:
            return Rule.TARQEEQ
        if key in self.salsal_tarqeeq:
            return Rule.TARQEEQ
        if key in self.separated_tafkheem:
            return Rule.TAFKHEEM
        if key in self.final_waqf_tafkheem and boundaries.stopped_on(word):
            return Rule.TAFKHEEM
        return Rule.TAFKHEEM if _ordinary_trigger(near, slot) else None


@dataclass(frozen=True, slots=True)
class LamWeight:
    profile: LamProfile
    rule: Rule = Rule.TAFKHEEM
    phase: Phase = Phase.COLOUR
    triggers: frozenset = frozenset({L.LAM})
    emits: frozenset = frozenset({Rule.TAFKHEEM, Rule.TARQEEQ})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        rule = self.profile.rule(near, at, boundaries)
        if rule is None:
            return None
        occurrence = Occurrence(mint(rule, at), rule, (at,))
        if rule is Rule.TARQEEQ:
            return Verdict(occurrence, ())
        effects = []
        if not plan.merged_away(at, Aspect.CONSONANT):
            effects.append(
                Recolour(at, Aspect.CONSONANT, SoundFeature.EMPHATIC, True)
            )
        state = (
            slot.nucleus.stopped
            if boundaries.stopped_on(word)
            else slot.nucleus.joined
        )
        if (
            state.quality is Quality.A
            and not plan.merged_away(at, Aspect.VOWEL)
        ):
            effects.append(
                Recolour(at, Aspect.VOWEL, SoundFeature.EMPHATIC, True)
            )
        if not effects:
            return None
        return Verdict(occurrence, tuple(effects))


def _key(near: Neighbourhood, word: int, at: SlotId) -> LamKey:
    score_word = near.score.words[word]
    ordinal = sum(
        slot.letter is L.LAM
        for slot in score_word.slots
        if slot.id.ordinal <= at.ordinal
    )
    return score_word.location, ordinal


def _ordinary_trigger(near: Neighbourhood, slot) -> bool:
    before = near.before(slot.id)
    if before is None or near.word_of(before.id) != near.word_of(slot.id):
        return False
    if slot.nucleus.joined.quality is not Quality.A:
        return False
    if slot.nucleus.joined.form not in {VowelForm.SHORT, VowelForm.LONG}:
        return False
    if before.letter not in {L.SAD, L.TAH, L.ZAH}:
        return False
    state = before.nucleus.joined
    return state.form is VowelForm.ABSENT or (
        state.form is VowelForm.SHORT and state.quality is Quality.A
    )


__all__ = ["LamKey", "LamProfile", "LamWeight"]
