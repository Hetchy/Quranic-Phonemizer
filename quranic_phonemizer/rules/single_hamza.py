"""Generic classification of a script-supplied lexical hamza replacement."""

from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Classify,
    MergeInto,
    Phase,
    Plan,
    Realize,
    Silence,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import Annotation, CanonLetter, Onset, Rule
from ..model.performance import Aspect, Occurrence, Vowel


@dataclass(frozen=True, slots=True)
class SuppliedIbdal:
    """Name the replacement already carried by the canonical slot."""

    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Annotation.IBDAL})
    emits: frozenset = frozenset({Rule.IBDAL_HAMZA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None or Annotation.IBDAL not in slot.annotations:
            return None
        # A BADAL long belongs to the carrier after the changed hamza.  When
        # the selected-script projection folds both into one slot (as in
        # `يُوَ۬اخِذُ`), ibdal still names the replacement consonant, not
        # that following long vowel.
        aspect = (
            Aspect.CONSONANT
            if Annotation.BADAL in slot.annotations
            else Aspect.VOWEL if slot.nucleus.is_long else Aspect.CONSONANT
        )
        return Verdict(
            Occurrence(mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA, (at,)),
            (Classify(at, aspect),),
        )


@dataclass(frozen=True, slots=True)
class JoinedIbdal:
    """Replace a sakin qata exposed when its prosthetic hamza elides."""

    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Onset.PLAIN})
    emits: frozenset = frozenset({Rule.IBDAL_HAMZA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if (
            slot is None
            or word is None
            or slot.letter is not CanonLetter.HAMZA
            or slot.onset is not Onset.PLAIN
            or not slot.nucleus.is_silent
            or boundaries.started_on(word)
        ):
            return None
        wasl = near.before(at)
        if wasl is None or wasl.onset is not Onset.WASL:
            return None
        carrier = near.before(wasl.id)
        if carrier is None or carrier.nucleus.quality is None:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA, (at,),
                boundary=word - 1,
            ),
            (
                Realize(
                    at,
                    Aspect.VOWEL,
                    Vowel(carrier.nucleus.quality, long=True),
                ),
                MergeInto(
                    carrier.id,
                    Aspect.VOWEL,
                    at,
                    Aspect.VOWEL,
                ),
                Silence(at, Aspect.CONSONANT),
            ),
        )


@dataclass(frozen=True, slots=True)
class JoinedIbdalMadd:
    """Name the natural length created by connected single-hamza ibdal."""

    rule: Rule = Rule.MADD_TABII
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({CanonLetter.HAMZA})
    emits: frozenset = frozenset({Rule.MADD_TABII})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del boundaries
        slot = near.slot(at)
        if (
            slot is None
            or slot.letter is not CanonLetter.HAMZA
            or not plan.joined_ibdal_length(at)
        ):
            return None
        return Verdict(
            Occurrence(mint(Rule.MADD_TABII, at), Rule.MADD_TABII, (at,)),
            (Classify(at, Aspect.VOWEL),),
        )


__all__ = ["JoinedIbdal", "JoinedIbdalMadd", "SuppliedIbdal"]
