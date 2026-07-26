"""Waqf and ibtidāʾ: what the edges of a reading do to it.

The module is named for its scope rather than for one term, because it spans
both waqf *and* ibtidāʾ and no single tajweed word covers that. Inventing one
would be worse than an English structural name (ADR-007 §4.0).

Everything here reads the `BoundaryPlan`. The Score is boundary-free, so these
are the only rules that may ask where the reciter stops.
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

    `كِتَٰبٌ` at waqf is the case `Aspect` exists for: the bāʾ's onset still
    sounds and its nucleus drops, and without an aspect the slot would satisfy
    "appears in at least one attribution" through its consonant edge while the
    dropped nucleus went unrecorded (ADR-002 §2).
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
        if not _is_last_of_word(near, at, word):
            return None

        if _followed_by_tanween_noon(near, at, word):
            return None  # TanweenAtWaqf owns this word's ending

        effects = []
        if slot.nucleus.kind is NucleusKind.SHORT:
            effects.append(Silence(at, Aspect.NUCLEUS))
        elif slot.nucleus.kind is NucleusKind.SILAH:
            # Ṣilah is long in waṣl and absent at pause — the mirror of
            # `Onset.WASL`, and canonical rather than a rule's invention.
            effects.append(Silence(at, Aspect.NUCLEUS))
        elif slot.nucleus.kind is NucleusKind.PAUSAL_LONG:
            effects.append(
                Realize(at, Aspect.NUCLEUS, (Vowel(slot.nucleus.quality, True),))
            )
        if slot.onset is Onset.SILAH:
            # 27:36:8: at waqf the pronoun yāʾ's **onset** disappears as well
            # as its nucleus. Silencing only the nucleus leaves a stray glide,
            # which is the error `Onset.SILAH` was added to make expressible.
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

    Its nucleus *is* the helping vowel, supplied by `canon.build` — so at waṣl
    this silences both aspects and at ibtidāʾ it does nothing, because the
    canonical value is already right (ADR-003 §6.3).
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
class TanweenAtWaqf:
    """The tanwīn nūn is silent at a stop; after a fatha it leaves the ʿiwaḍ.

    Under A1 this is two ordinary effects on two slots rather than a special
    case: `Silence` on the nūn slot, and — for fathatan only — `Relength` on
    the base. Dammatan and kasratan are simply two silences (ADR-004 §8.3).
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
    """`ة` is a tāʾ in connection and a hāʾ at pause. Its alternation is
    canonical and rasm-conditioned, which is why the letter survived into
    `CanonLetter` at all (ADR-001 §4)."""

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
        if not _is_last_of_word(near, at, word):
            return None
        return Verdict(
            Occurrence(mint(Rule.WAQF_ENDING, at), Rule.WAQF_ENDING, Participants((at,))),
            (Realize(at, Aspect.ONSET, (Consonant(CanonLetter.HEH),)),),
        )


def _followed_by_tanween_noon(near: Neighbourhood, at: SlotId, word: int) -> bool:
    slots = near.score.words[word].slots
    return (
        len(slots) >= 2
        and slots[-1].id == at
        and slots[-1].origin is SlotOrigin.NUNATION
    )


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
