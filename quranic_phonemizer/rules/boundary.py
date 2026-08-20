"""Waqf: what a stop does to the end of a word.

Everything here reads the `BoundaryPlan`. The Score is boundary-free, so
these are the only rules that may ask where the reciter stops.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Length,
    Phase,
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
    Onset,
    Quality,
    Rule,
    SlotOrigin,
    VowelForm,
)
from ..model.performance import (
    Aspect,
    Consonant,
    Occurrence,
    Vowel,
)
from .khilaf import SitedKhilaf, vocalised_word

#: The glide's own drop, so its occurrence does not collide with the drop
#: of the haraka written on the same letter.
_GLIDE_VARIANT = 1


@dataclass(frozen=True, slots=True)
class WaqfHarakaDrop:
    """The haraka on a letter a stop lands on is written and not said.

    `كِتَٰبٌ` at waqf: the onset still sounds while the nucleus drops, so
    `Aspect` records the two separately.
    """

    yaa: SitedKhilaf = field(default_factory=SitedKhilaf)
    rule: Rule = Rule.WAQF_DIACRITIC_DROP
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset()

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        if not slot.nucleus.is_short:
            return None
        if _followed_by_tanween_noon(near, word):
            # One written tanween, one drop: `TanweenDrop` takes this vowel too.
            return None
        if not _takes_the_stop(near, at, word, _omitted_glide(self.yaa, near, word)):
            return None
        return Verdict(_drop(at, word), (Silence(at, Aspect.VOWEL),))


@dataclass(frozen=True, slots=True)
class WaqfSilahDrop:
    """The length drawing out a pronoun haa is absent at a pause.

    The haa is left bare rather than short, so the whole nucleus goes,
    mirroring `Onset.WASL`.
    """

    rule: Rule = Rule.WAQF_SILAH_DROP
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset()

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        if not slot.nucleus.is_silah or not _is_final_letter(near, at, word):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.WAQF_SILAH_DROP, at), Rule.WAQF_SILAH_DROP, (at,),
                boundary=word,
            ),
            (Silence(at, Aspect.VOWEL),),
        )


@dataclass(frozen=True, slots=True)
class DroppedGlide:
    """The pronoun yaa itself, where the reading leaves it off at a stop.

    The haraka written on it takes its own drop; this owns the letter, so
    the two need distinct occurrences on the one slot.
    """

    yaa: SitedKhilaf = field(default_factory=SitedKhilaf)
    rule: Rule = Rule.WAQF_DIACRITIC_DROP
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({Onset.GLIDE})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        word = near.word_of(at)
        if word is None or not boundaries.stopped_on(word):
            return None
        if _omitted_glide(self.yaa, near, word) != at:
            return None
        return Verdict(
            _drop(at, word, _GLIDE_VARIANT), (Silence(at, Aspect.CONSONANT),)
        )


@dataclass(frozen=True, slots=True)
class PausalAlif:
    """The seven alifs: long at a pause, short when the word is joined to.

    Both readings are this rule's: the stop names the length it says, the
    join names the length it takes away."""

    rule: Rule = Rule.PAUSAL_ALIF
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not slot.nucleus.is_pausal_long:
            return None
        occurrence = Occurrence(
            mint(Rule.PAUSAL_ALIF, at), Rule.PAUSAL_ALIF, (at,), boundary=word,
        )
        if boundaries.stopped_on(word):
            return Verdict(
                occurrence,
                (Realize(at, Aspect.VOWEL, Vowel(slot.nucleus.quality, True)),),
            )
        # Joined, the vowel is still plainly produced and only its length
        # changes, so this half owns no sound.
        return Verdict(occurrence, (Relength(at, Length.SHORT),))


@dataclass(frozen=True, slots=True)
class TanweenDrop:
    """A written tanween is not said at a stop.

    One mark, one drop: the noon goes, and with it the vowel the same mark
    wrote -- unless that vowel is exchanged for the iwad instead.
    """

    rule: Rule = Rule.WAQF_DIACRITIC_DROP
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.NOON})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        base, word = _nunation_base(near, at, boundaries)
        if base is None or word is None:
            return None
        effects = [Silence(at, Aspect.CONSONANT)]
        if not _takes_the_iwad(base):
            effects.append(Silence(base.id, Aspect.VOWEL))
        return Verdict(_drop(at, word), tuple(effects))


@dataclass(frozen=True, slots=True)
class TanweenIwad:
    """A fathatan stopped on is exchanged for a long aa rather than dropped.

    `TanweenDrop` still silences the noon; only the exchange is here.
    """

    rule: Rule = Rule.MADD_IWAD
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.NOON})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        base, word = _nunation_base(near, at, boundaries)
        if base is None or word is None or not _takes_the_iwad(base):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_IWAD, at), Rule.MADD_IWAD, (at,), boundary=word,
            ),
            (Relength(base.id, Length.LONG),),
        )


@dataclass(frozen=True, slots=True)
class TaaMarbutaAtWaqf:
    """`ة` is a taa in connection and a haa at pause -- a canonical,
    rasm-conditioned alternation."""

    rule: Rule = Rule.WAQF_TAA_MARBUTA
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
            Occurrence(mint(Rule.WAQF_TAA_MARBUTA, at), Rule.WAQF_TAA_MARBUTA,
                       (at,), boundary=word),
            (Realize(at, Aspect.CONSONANT, Consonant(CanonLetter.HEH)),),
        )


def _drop(at: SlotId, word: int, variant: int = 0) -> Occurrence:
    return Occurrence(
        mint(Rule.WAQF_DIACRITIC_DROP, at, variant), Rule.WAQF_DIACRITIC_DROP,
        (at,), boundary=word,
    )


def _nunation_base(near: Neighbourhood, at: SlotId, boundaries: BoundaryPlan):
    """The letter a final tanween noon is written over, at a stop."""
    slot, word = near.slot(at), near.word_of(at)
    if slot is None or word is None or not boundaries.stopped_on(word):
        return None, None
    if slot.origin is not SlotOrigin.NUNATION or not near.last_of_word(at):
        return None, None
    base = near.before(at)
    if base is None or not base.nucleus.is_short:
        return None, None
    return base, word


def _takes_the_iwad(base) -> bool:
    """Taa marbuta stops as haa and takes no iwad, so only a fathatan on
    some other letter is exchanged for length."""
    return (
        base.letter is not CanonLetter.TAA_MARBUTA
        and base.nucleus.quality is Quality.A
    )


def _is_final_letter(near: Neighbourhood, at: SlotId, word: int) -> bool:
    """The last slot that is not a tanween noon."""
    slots = [
        slot
        for slot in near.score.words[word].slots
        if slot.origin is not SlotOrigin.NUNATION
    ]
    return bool(slots) and slots[-1].id == at


def _followed_by_tanween_noon(near: Neighbourhood, word: int) -> bool:
    slots = near.score.words[word].slots
    return bool(slots) and slots[-1].origin is SlotOrigin.NUNATION


def _omitted_glide(
    yaa: SitedKhilaf, near: Neighbourhood, word: int
) -> SlotId | None:
    """The final glide this reading leaves off, if it leaves one off.

    Ithbat says the optional yaa anyway, so the stop takes its vowel and
    `PausalGlide` lengthens what is left.
    """
    slots = near.score.words[word].slots
    if not slots or slots[-1].onset is not Onset.GLIDE:
        return None
    kept = yaa.of(
        vocalised_word(near.score.words[word]), True, near.score.selection
    )
    return None if kept else slots[-1].id


def _takes_the_stop(
    near: Neighbourhood, at: SlotId, word: int, omitted: SlotId | None
) -> bool:
    """A letter absent at the pause is not the one stopped on, so the letter
    before it takes the stop instead."""
    if _is_final_letter(near, at, word):
        return True
    following = near.after(at)
    return omitted is not None and following is not None and following.id == omitted
