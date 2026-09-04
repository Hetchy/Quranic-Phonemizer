"""Lam weight from structural triggers and riwayah-owned registers."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Recolour, SoundFeature, Verdict, mint
from ..model.address import BoundaryPlan, KhilafId, Location, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Quality, Rule, Score, VowelForm
from ..model.performance import Aspect, Occurrence
from .tafkheem import Weight

LamKey = tuple[Location, int]

#: Coupled selectors name the inclination half in the option; the lam weight
#: is the second member of the pair.
HEAVY = {
    "tafkheem": True,
    "tarqiq": False,
    "fath_tafkheem": True,
    "taqlil_tarqiq": False,
}


@dataclass(frozen=True, slots=True)
class LamChoice:
    """One selector-owned lam site and the junction its dispute lives in."""

    khilaf: KhilafId
    junction: str
    default: str

    def active(self, stopped: bool) -> bool:
        return self.junction == "all" or stopped


@dataclass(frozen=True, slots=True)
class GeneralLamChoice:
    """The taa or zhaa consumer over the ordinary qualifying scope."""

    khilaf: KhilafId
    default: str


@dataclass(frozen=True, slots=True)
class LamProfile:
    selected: dict[LamKey, LamChoice] = field(default_factory=dict)
    taa: GeneralLamChoice | None = None
    zhaa: GeneralLamChoice | None = None

    def rule(self, near: Neighbourhood, at: SlotId, boundaries) -> Rule | None:
        word = near.word_of(at)
        slot = near.slot(at)
        if word is None or slot is None or slot.letter is not L.LAM:
            return None
        choice = self.selected.get(_key(near, word, at))
        if choice is not None and choice.active(boundaries.stopped_on(word)):
            name = near.score.selection.chosen(choice.khilaf) or choice.default
            return Rule.TAFKHEEM if HEAVY[name] else Rule.TARQEEQ
        trigger = _trigger(near, slot)
        general = self._general(trigger)
        if general is None:
            return Rule.TAFKHEEM if trigger is not None else Rule.TARQEEQ
        name = near.score.selection.chosen(general.khilaf) or general.default
        return Rule.TAFKHEEM if HEAVY[name] else Rule.TARQEEQ

    def _general(self, trigger) -> GeneralLamChoice | None:
        if trigger is L.TAH:
            return self.taa
        if trigger is L.ZAH:
            return self.zhaa
        return None


@dataclass(frozen=True, slots=True)
class LamWeight:
    profile: LamProfile
    base_weight: Weight = field(default_factory=Weight)
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
        if plan.merged_away(at, Aspect.CONSONANT):
            return None
        # The shared emphasis rule owns the ordinary divine-name verdict.
        # This Warsh profile only supplies the riwayah-specific lam cases and
        # the explicit light fallback; emitting both would give one lam two
        # contradictory identities.
        if self.base_weight.is_heavy(near, slot, plan, boundaries):
            return None
        rule = self.profile.rule(near, at, boundaries)
        if rule is None:
            return None
        occurrence = Occurrence(mint(rule, at), rule, (at,))
        if rule is Rule.TARQEEQ:
            return Verdict(occurrence, ())
        effects = [Recolour(at, Aspect.CONSONANT, SoundFeature.EMPHATIC, True)]
        state = (
            slot.nucleus.stopped
            if boundaries.stopped_on(word)
            else slot.nucleus.joined
        )
        if (
            state.quality is Quality.A
            and state.form is not VowelForm.ABSENT
            and not plan.merged_away(at, Aspect.VOWEL)
        ):
            effects.append(
                Recolour(at, Aspect.VOWEL, SoundFeature.EMPHATIC, True)
            )
        return Verdict(occurrence, tuple(effects))


def general_owner(
    near: Neighbourhood, slot, boundaries, profile: LamProfile
) -> GeneralLamChoice | None:
    """The taa or zhaa consumer owning this lam in the current state."""
    word = near.word_of(slot.id)
    if word is None or slot.letter is not L.LAM:
        return None
    choice = profile.selected.get(_key(near, word, slot.id))
    if choice is not None and choice.active(boundaries.stopped_on(word)):
        return None
    return profile._general(_trigger(near, slot))


def general_sites(
    score: Score, boundaries: BoundaryPlan, profile: LamProfile
) -> tuple[tuple[str, int], ...]:
    """Every (selector id, word index) the taa and zhaa consumers own."""
    near = Neighbourhood(score, boundaries)
    sites = []
    for index, word in enumerate(score.words):
        for slot in word.slots:
            owner = general_owner(near, slot, boundaries, profile)
            if owner is not None:
                sites.append((owner.khilaf.value, index))
    return tuple(sites)


def _key(near: Neighbourhood, word: int, at: SlotId) -> LamKey:
    score_word = near.score.words[word]
    ordinal = sum(
        slot.letter is L.LAM
        for slot in score_word.slots
        if slot.id.ordinal <= at.ordinal
    )
    return score_word.location, ordinal


def _trigger(near: Neighbourhood, slot) -> L | None:
    before = near.before(slot.id)
    if before is None or near.word_of(before.id) != near.word_of(slot.id):
        return None
    if slot.nucleus.joined.quality is not Quality.A:
        return None
    if slot.nucleus.joined.form not in {VowelForm.SHORT, VowelForm.LONG}:
        return None
    if before.letter not in {L.SAD, L.TAH, L.ZAH}:
        return None
    state = before.nucleus.joined
    qualifies = state.form is VowelForm.ABSENT or (
        state.form is VowelForm.SHORT and state.quality is Quality.A
    )
    return before.letter if qualifies else None


__all__ = [
    "GeneralLamChoice",
    "LamChoice",
    "LamKey",
    "LamProfile",
    "LamWeight",
    "general_owner",
    "general_sites",
]
