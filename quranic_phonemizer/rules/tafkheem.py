"""Tafkheem: which sounds are heavy.

Emphasis spreads onto a following `a` and onto neither `i` nor `u`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Recolour, SoundFeature, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import (
    Annotation,
    CanonLetter,
    Onset,
    Quality,
    Rule,
)
from ..model.performance import Aspect, Occurrence, Participants
from .khilaf import SitedKhilaf, vocalised_word

#: Raa and the lam of the divine name are heavy only under the conditions
#: below, so they trigger the rule without belonging to any heavy set.
CONDITIONAL = frozenset({L.RA, L.LAM})

#: How far back `_governing` looks for a vowel that is actually heard.
MAX_LOOKBACK = 3


@dataclass(frozen=True, slots=True)
class Weight:
    """Which sounds are heavy. Held by both rules that ask, so the question
    is stated once and the two cannot drift apart."""

    always_heavy: frozenset[CanonLetter] = frozenset()
    raa: SitedKhilaf = field(default_factory=SitedKhilaf)

    def is_heavy(self, near, slot, plan, boundaries) -> bool:
        if slot.letter in self.always_heavy:
            return True
        if slot.letter is L.RA:
            return self._raa(near, slot, plan, boundaries)
        if slot.letter is L.LAM:
            return _is_divine_lam(near, slot, plan)
        return False

    def _raa(self, near, slot, plan, boundaries) -> bool:
        own = None if _silenced(plan, slot) else _quality(slot)
        if own is not None:
            return own in (Quality.A, Quality.U)
        word = near.word_of(slot.id)
        disputed = None if word is None else self.raa.of(
            vocalised_word(near.score.words[word]),
            boundaries.stopped_on(word),
            near.score.selection,
        )
        if disputed is not None:
            return disputed
        return _raa_is_heavy(near, slot, plan, self.always_heavy)


@dataclass(frozen=True, slots=True)
class Emphasis:
    weight: Weight = field(default_factory=Weight)
    rule: Rule = Rule.TAFKHEEM
    phase: Phase = Phase.COLOUR
    triggers: frozenset = field(default=frozenset())

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "triggers", frozenset(self.weight.always_heavy | CONDITIONAL)
        )

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if slot is None:
            return None
        if not self.weight.is_heavy(near, slot, plan, boundaries):
            return None
        effects = [Recolour(at, Aspect.CONSONANT, SoundFeature.EMPHATIC, True)]
        if _quality(slot) is Quality.A and not _silenced(plan, slot):
            effects.append(
                Recolour(at, Aspect.VOWEL, SoundFeature.EMPHATIC, True)
            )
        return Verdict(
            Occurrence(mint(Rule.TAFKHEEM, at), Rule.TAFKHEEM,
                       Participants(at)),
            tuple(effects),
        )


def _raa_is_heavy(near, slot, plan, always_heavy) -> bool:
    """The quiescent raa, whose vowel is gone or was never there."""
    before = near.before(slot.id)
    if (
        before is not None
        and before.letter is L.YA
        and before.nucleus.is_silent
    ):
        # A raa after a leen yaa follows the yaa and stays light.
        return False
    if before is not None and before.onset is Onset.WASL:
        # Only an original kasra lightens. A prosthetic hamza's is aridah --
        # it exists to be started on and is gone the moment the word is
        # joined to -- so `ٱرْتَبْتُمْ` is heavy started on and `أَمِ ٱرْتَابُوٓا۟`
        # is heavy joined, where the kasra heard before the raa is the one
        # the previous word grew to meet it.
        return True
    following = near.after(slot.id)
    if (
        following is not None
        and not near.crosses_word(slot.id)
        and following.letter in always_heavy
    ):
        # A letter of istilaa after a quiescent raa wins over whatever
        # precedes it: `قِرْطَاسٍ` is heavy despite its kasra. Only inside the
        # word: `تُصَعِّرْ خَدَّكَ` and `فَٱصْبِرْ صَبْرًا` keep a light raa, because
        # the letter that would weigh it belongs to the next word.
        return True
    governing = _governing(near, slot, plan)
    if governing is None:
        return False
    return _quality(governing) in (Quality.A, Quality.U)


def _silenced(plan, slot) -> bool:
    """A nucleus a BOUNDARY rule removed. COLOUR runs after BOUNDARY, so a raa
    that lost its kasra at a stop is governed by the vowel before it."""
    return plan.merged_away(slot.id, Aspect.VOWEL)


def _is_divine_lam(near: Neighbourhood, slot, plan) -> bool:
    """The lam of `ٱللَّه`: heavy after a fatha or damma, light after a kasra.

    Which lam it is was decided once at build time; this reads the tag rather
    than matching the word's shape a second time.
    """
    if Annotation.DIVINE_NAME not in slot.annotations:
        return False
    governing = _governing(near, slot, plan)
    quality = None if governing is None else _quality(governing)
    return quality in (Quality.A, Quality.U)


def _governing(near: Neighbourhood, slot, plan):
    """The slot carrying the vowel actually heard before this one.

    Skips a canonically silent slot and one a BOUNDARY rule elided: the wasl
    hamza's helping vowel is not spoken mid-word.
    """
    before = near.before(slot.id)
    for _ in range(MAX_LOOKBACK):
        if before is None:
            return None
        silent = before.nucleus.is_silent
        if not (silent or _silenced(plan, before)):
            return before
        before = near.before(before.id)
    return None


def _quality(slot):
    return slot.nucleus.quality
