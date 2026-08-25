"""Naql: a qata hamza's vowel moves back onto the quiescent host before it.

Joined-only transfer reads the plan; the carried shape holds in every state."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Realize, Silence, Verdict, mint
from ..model.address import BoundaryPlan, Junction, Location, SlotId
from ..model.canon import Annotation, CanonLetter, Onset, Rule
from ..model.performance import Aspect, Occurrence, Vowel
from .ownership import is_quiescent


@dataclass(frozen=True, slots=True)
class Naql:
    """Joined speech only: the host takes exactly the qata's vowel and the
    qata onset is silent. The subject order is the qata, then its host."""

    excluded: frozenset[Location] = frozenset()
    """Authored boundaries the riwayah reads with tahqiq instead; the qata
    word's location keys each one."""

    rule: Rule = Rule.NAQL
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.HAMZA})
    emits: frozenset = frozenset({Rule.NAQL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or not word:
            return None
        if slot.letter is not CanonLetter.HAMZA or slot.onset is not Onset.PLAIN:
            return None
        if slot.nucleus.is_silent or not near.first_of_word(at):
            return None
        if boundaries.after(word - 1) is not Junction.JOIN:
            return None
        host = near.before(at)
        # A spelled opening ends as it would at a pause, so it hosts nothing.
        if host is None or not is_quiescent(host) or host.spelled:
            return None
        if near.score.words[word].location in self.excluded:
            return None
        vowel = Vowel(slot.nucleus.quality, long=slot.nucleus.sounds_long)
        return Verdict(
            Occurrence(
                mint(Rule.NAQL, at), Rule.NAQL, (at, host.id),
                boundary=word - 1,
            ),
            (
                Realize(host.id, Aspect.VOWEL, vowel),
                Silence(at, Aspect.CONSONANT),
                Silence(at, Aspect.VOWEL),
            ),
        )


@dataclass(frozen=True, slots=True)
class CarriedNaql:
    """A host whose canonical vowel already is the transferred one: the
    article family and authored lexical sites. The qata never returns, so
    the occurrence names the host and its carried vowel in every state."""

    rule: Rule = Rule.NAQL
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Annotation.NAQL})
    emits: frozenset = frozenset({Rule.NAQL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None or Annotation.NAQL not in slot.annotations:
            return None
        # Effect-free: the carried vowel is already canonical, so the
        # classification-only machinery names it without claiming the slot.
        return Verdict(Occurrence(mint(Rule.NAQL, at), Rule.NAQL, (at,)), ())
