"""Waqf and ibtidaa: what the edges of a reading do to it.

Everything here reads the `BoundaryPlan`. The Score is boundary-free, so
these are the only rules that may ask where the reciter stops.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Length,
    Plan,
    Realize,
    Relength,
    Silence,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import (
    CanonLetter,
    NucleusKind,
    Onset,
    Phase,
    Quality,
    Rule,
    SlotOrigin,
)
from ..model.performance import (
    Aspect,
    Consonant,
    Occurrence,
    Participants,
    Vowel,
)


@dataclass(frozen=True, slots=True)
class WaqfEnding:
    """The last slot of a word stopped on loses its vowel.

    `كِتَٰبٌ` at waqf: the onset still sounds while the nucleus drops, so
    `Aspect` records the two separately.
    """

    rule: Rule = Rule.WAQF_ENDING
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset()

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot = near.slot(at)
        word = near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        if not _is_final_letter(near, at, word):
            return None
        if _followed_by_tanween_noon(near, at, word) and (
            slot.letter is not CanonLetter.TAA_MARBUTA
        ):
            # TanweenAtWaqf owns the ending; taa marbuta drops its vowel here instead.
            return None

        effects = []
        if slot.nucleus.kind is NucleusKind.SHORT:
            effects.append(Silence(at, Aspect.NUCLEUS))
        elif slot.nucleus.kind is NucleusKind.SILAH:
            # Silah is long in wasl and absent at pause, mirroring `Onset.WASL`.
            effects.append(Silence(at, Aspect.NUCLEUS))
        elif slot.nucleus.kind is NucleusKind.PAUSAL_LONG:
            effects.append(
                Realize(at, Aspect.NUCLEUS, (Vowel(slot.nucleus.quality, True),))
            )
        if slot.onset is Onset.SILAH:
            # The pronoun yaa's onset must go too, or a stray glide remains.
            effects.append(Silence(at, Aspect.ONSET))
        if not effects:
            return None
        return Verdict(
            Occurrence(mint(Rule.WAQF_ENDING, at), Rule.WAQF_ENDING, Participants((at,))),
            tuple(effects),
        )


@dataclass(frozen=True, slots=True)
class WaslHamza:
    """The prosthetic hamza sounds only when started on.

    Its nucleus is the helping vowel: joining silences both aspects,
    starting leaves the canonical value untouched.
    """

    rule: Rule = Rule.WASL_ELISION
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Onset.WASL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or slot.onset is not Onset.WASL:
            return None
        if boundaries.started_on(word) and _is_first_of_word(near, at, word):
            return Verdict(
                Occurrence(mint(Rule.WASL_START, at), Rule.WASL_START, Participants((at,))), ()
            )
        return Verdict(
            Occurrence(mint(Rule.WASL_ELISION, at), Rule.WASL_ELISION, Participants((at,))),
            (Silence(at, Aspect.ONSET), Silence(at, Aspect.NUCLEUS)),
        )


@dataclass(frozen=True, slots=True)
class SoftenedHamza:
    """Two hamzas are not said in a row. Started on, the prosthetic hamza's
    vowel lengthens and carries the quiescent one as its madd letter."""

    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Onset.WASL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or slot.onset is not Onset.WASL:
            return None
        if not (boundaries.started_on(word) and _is_first_of_word(near, at, word)):
            return None   # joined, the prosthetic hamza has no vowel to carry
        following = near.after(at)
        if (
            following is None
            or following.letter is not CanonLetter.HAMZA
            or following.nucleus.kind is not NucleusKind.SILENT
        ):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA,
                Participants((at, following.id)),
            ),
            (
                Relength(at, Length.LONG),
                Silence(following.id, Aspect.ONSET),
            ),
        )


@dataclass(frozen=True, slots=True)
class TanweenAtWaqf:
    """The tanween noon is silent at a stop; after a fatha it leaves the iwad.

    Two effects on two slots: `Silence` on the noon, and -- for fathatan
    only -- `Relength` on the base. Dammatan and kasratan are just silences.
    """

    rule: Rule = Rule.IWAD
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.NOON})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        if not _is_last_of_word(near, at, word):
            return None
        if slot.origin is not SlotOrigin.NUNATION:
            return None
        base = _previous(near, at)
        if base is None or base.nucleus.kind is not NucleusKind.SHORT:
            return None
        effects = [Silence(at, Aspect.ONSET)]
        rule = Rule.WAQF_ENDING
        if base.letter is CanonLetter.TAA_MARBUTA:
            # Taa marbuta stops as haa and takes no iwad, but the noon is still silent.
            return Verdict(
                Occurrence(mint(rule, at), rule, Participants((at, base.id))),
                tuple(effects),
            )
        if base.nucleus.quality is Quality.A:
            rule = Rule.IWAD
            effects.append(Relength(base.id, Length.LONG))
        else:
            effects.append(Silence(base.id, Aspect.NUCLEUS))
        return Verdict(
            Occurrence(mint(rule, at), rule, Participants((at, base.id))),
            tuple(effects),
        )


@dataclass(frozen=True, slots=True)
class TaaMarbutaAtWaqf:
    """`ة` is a taa in connection and a haa at pause -- a canonical,
    rasm-conditioned alternation."""

    rule: Rule = Rule.WAQF_ENDING
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.TAA_MARBUTA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        if not _is_final_letter(near, at, word):
            return None
        # `بِسُورَةٍ` stops as haa with no iwad; "final" here excludes the tanween noon slot.
        return Verdict(
            # variant=1 distinguishes this from `WaqfEnding`, which also
            # fires on this slot, on a different aspect.
            Occurrence(mint(Rule.WAQF_ENDING, at, variant=1), Rule.WAQF_ENDING,
                       Participants((at,))),
            (Realize(at, Aspect.ONSET, (Consonant(CanonLetter.HEH),)),),
        )


def _is_final_letter(near: Neighbourhood, at: SlotId, word: int) -> bool:
    """The last slot that is not a tanween noon."""
    slots = [
        slot
        for slot in near.score.words[word].slots
        if slot.origin is not SlotOrigin.NUNATION
    ]
    return bool(slots) and slots[-1].id == at


def _followed_by_tanween_noon(near: Neighbourhood, at: SlotId, word: int) -> bool:
    del at
    slots = near.score.words[word].slots
    return bool(slots) and slots[-1].origin is SlotOrigin.NUNATION


def _previous(near: Neighbourhood, at: SlotId):
    flat = near.score.slots()
    for index, slot in enumerate(flat):
        if slot.id == at:
            return flat[index - 1] if index else None
    return None


def _is_last_of_word(near: Neighbourhood, at: SlotId, word: int) -> bool:
    slots = near.score.words[word].slots
    return bool(slots) and slots[-1].id == at


def _is_first_of_word(near: Neighbourhood, at: SlotId, word: int) -> bool:
    slots = near.score.words[word].slots
    return bool(slots) and slots[0].id == at
