"""Generic classification of a script-supplied lexical hamza replacement."""

from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Classify,
    Length,
    MergeInto,
    Phase,
    Plan,
    Realize,
    Relength,
    Silence,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, Location, SlotId
from ..model.canon import Annotation, CanonLetter, Onset, Rule
from ..model.inscription import SilenceReason
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
class AraytaIbdal:
    """The arayta family's ibdal face folds the eased qata into a long.

    At a complete stop on a bare unsuffixed form the fold would end three
    sakins deep, so the selection is masked to the eased face there."""

    locations: frozenset[Location]
    bare: frozenset[Location]
    choice: object | None = None
    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.HAMZA})
    emits: frozenset = frozenset({Rule.IBDAL_HAMZA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.letter is not CanonLetter.HAMZA or slot.onset is not Onset.TASHIL:
            return None
        location = near.score.words[word].location
        if location not in self.locations:
            return None
        chosen = (
            self.choice.choose(near.score.selection)
            if self.choice is not None
            else "ibdal"
        )
        if chosen != "ibdal":
            return None
        if location in self.bare and boundaries.stopped_on(word):
            return None
        previous = near.before(at)
        if previous is None:
            return None
        return Verdict(
            Occurrence(mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA, (at,)),
            (
                MergeInto(previous.id, Aspect.VOWEL, at, Aspect.VOWEL),
                Silence(at, Aspect.CONSONANT),
                Relength(at, Length.LONG),
            ),
        )


@dataclass(frozen=True, slots=True)
class AllaiFaces:
    """The allai continuation deletes the written yaa behind the eased
    qata; the waqf ibdal face replaces that qata with the sakin yaa."""

    locations: frozenset[Location]
    choice: object | None = None
    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.HAMZA})
    emits: frozenset = frozenset({Rule.IBDAL_HAMZA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.letter is not CanonLetter.HAMZA or slot.onset is not Onset.TASHIL:
            return None
        if near.score.words[word].location not in self.locations:
            return None
        following = near.raw_after(at)
        if following is None or following.letter is not CanonLetter.YA:
            return None
        chosen = (
            self.choice.choose(near.score.selection)
            if self.choice is not None
            else "tashil"
        )
        if chosen == "ibdal_yaa" and boundaries.stopped_on(word):
            return Verdict(
                Occurrence(
                    mint(Rule.IBDAL_HAMZA, following.id), Rule.IBDAL_HAMZA,
                    (following.id,),
                ),
                (
                    Silence(at, Aspect.CONSONANT),
                    Silence(at, Aspect.VOWEL),
                    Classify(following.id, Aspect.CONSONANT),
                ),
            )
        return Verdict(
            Occurrence(
                mint(SilenceReason.VARIANT, following.id),
                SilenceReason.VARIANT,
                (following.id,),
            ),
            (Silence(following.id, Aspect.CONSONANT),),
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
