"""Naql: a qata hamza's vowel moves back onto the quiescent host before it.

Joined-only transfer reads the plan; the carried shape holds in every state."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Phase, Plan, Realize, Silence, Verdict, mint
from ..model.address import BoundaryPlan, Junction, Location, SlotId
from ..model.canon import Annotation, CanonLetter, Onset, Rule
from ..model.performance import Aspect, Occurrence, Vowel
from .ownership import is_quiescent


@dataclass(frozen=True, slots=True)
class Naql:
    """Joined speech only: the host takes the qata's short vowel and the
    qata onset is silent. The subject order is the qata, then its host."""

    excluded: frozenset[Location] = frozenset()
    """Authored boundaries the riwayah reads with tahqiq instead; the qata
    word's location keys each one."""

    ibdal_meetings: frozenset[Location] = frozenset()
    """One-word meetings whose default ibdal supplies the post-naql long."""

    rule: Rule = Rule.NAQL
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.HAMZA})
    emits: frozenset = frozenset({Rule.NAQL})

    def _ibdal_carrier(
        self, near: Neighbourhood, at: SlotId, word: int
    ):
        following = near.after(at)
        if (
            near.score.words[word].location in self.ibdal_meetings
            and following is not None
            and near.word_of(following.id) == word
            and following.letter is CanonLetter.HAMZA
        ):
            return following
        return None

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
        if slot.nucleus.is_silent:
            return None
        if not near.first_of_word(at):
            return None
        if boundaries.after(word - 1) is not Junction.JOIN:
            return None
        host = near.before(at)
        # A spelled opening ends as it would at a pause, so it hosts nothing.
        if host is None or not is_quiescent(host) or host.spelled:
            return None
        if near.score.words[word].location in self.excluded:
            return None
        effects = [Silence(at, Aspect.CONSONANT)]
        ibdal_carrier = self._ibdal_carrier(near, at, word)
        if ibdal_carrier is not None:
            effects.append(
                MergeInto(
                    host.id, Aspect.VOWEL, ibdal_carrier.id, Aspect.VOWEL
                )
            )
        elif slot.nucleus.sounds_long:
            # In badal mughayyar bin-naql the carrier still owns the one long
            # vowel. The preceding sakin presents that same sound through a
            # bridge; realizing a separate short vowel here would produce
            # the impossible sequence /a a:/ (and likewise for /u/ and /i/).
            effects.append(
                MergeInto(host.id, Aspect.VOWEL, at, Aspect.VOWEL)
            )
        else:
            effects.extend((
                Realize(host.id, Aspect.VOWEL, Vowel(slot.nucleus.quality)),
                Silence(at, Aspect.VOWEL),
            ))
        return Verdict(
            Occurrence(
                mint(Rule.NAQL, at), Rule.NAQL, (at, host.id),
                boundary=word - 1,
            ),
            tuple(effects),
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
