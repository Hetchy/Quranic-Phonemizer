"""Length at the edges: the glide that becomes the vowel before it.

`هُوَ` at a stop: the fatha drops and the waw merges into the damma before
it, so the word ends long. A final yaa after a kasra does the same.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Length,
    MergeInto,
    Phase,
    Plan,
    Realize,
    Relength,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Quality, Rule, VowelForm
from ..model.performance import Aspect, Occurrence, Participants, Vowel

#: Which glide lengthens which vowel.
GLIDE_OF = {Quality.U: L.WAW, Quality.I: L.YA}


@dataclass(frozen=True, slots=True)
class PausalGlide:
    rule: Rule = Rule.MADD_TABII
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        if plan.merged_away(at, Aspect.CONSONANT):
            # A glide the stop removed outright lengthens nothing.
            return None
        if slot.onset is Onset.GEMINATE:
            # A doubled glide is a consonant -- `ٱلْعَلِىُّ` ends `-iyy`, not `-ii`.
            return None
        if slot.nucleus.sounds_long:
            # A glide the stop cannot strip still carries its own vowel, so it
            # is a consonant: `نَسِيَا` ends `-iyaa`, not `-iiaa`.
            return None
        before = near.before(at)
        if before is None or not before.nucleus.is_short:
            return None
        if GLIDE_OF.get(before.nucleus.quality) is not slot.letter:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_TABII, at),
                Rule.MADD_TABII,
                # The glide is the source; the vowel it merges into is the host.
                Participants(source=at, host=before.id),
            ),
            (
                # Realizes the merged sound itself, so both halves share one occurrence.
                Realize(
                    before.id,
                    Aspect.VOWEL,
                    Vowel(before.nucleus.quality, long=True),
                ),
                MergeInto(at, Aspect.CONSONANT, before.id, Aspect.VOWEL),
            ),
        )


@dataclass(frozen=True, slots=True)
class IltiqaShortening:
    """Two sakins meet, so the madd letter shortens.

    Emits `Relength`, not a realization: the vowel is still plainly
    produced, only its length changes, so this rule owns no sound.
    """

    rule: Rule = Rule.ILTIQA_SHORTENING
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not (slot.nucleus.is_long or slot.nucleus.is_silah):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        following = near.after(at)
        if following is None:
            # `after` already refuses to look across a stop, so at a pause
            # there is no second sakin to meet and the madd stands.
            return None
        if following.onset is Onset.WASL:
            # A joined wasl hamza vanishes, so the sakin the madd meets is
            # the consonant behind it -- read from the Score, since
            # `Onset.WASL` means exactly "absent when joined to".
            following = near.after(following.id)
            if following is None:
                return None
        if not _opens_on_a_sakin(following):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.ILTIQA_SHORTENING, at),
                Rule.ILTIQA_SHORTENING,
                Participants(at, following.id),
            ),
            (Relength(at, Length.SHORT),),
        )


def _opens_on_a_sakin(slot) -> bool:
    """A geminate consonant is a sakin plus a voweled one, so `ٱلَّذِى` meets a
    preceding madd with a sakin exactly as a written sukun would."""
    return slot.nucleus.is_silent or slot.onset is Onset.GEMINATE


@dataclass(frozen=True, slots=True)
class MaddClass:
    """Which madd this long vowel is -- one classifier, five outcomes.

    `MADD_TABII` is deliberately not emitted here: it is the default that
    holds wherever none of the five outcomes applies.
    """

    rule: Rule = Rule.MADD_LAZIM
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not slot.nucleus.sounds_long:
            return None
        slots = near.score.words[word].slots
        final = bool(slots) and slots[-1].id == at

        if final and boundaries.stopped_on(word):
            # Nothing follows inside the word and the stop ends it; `WaqfEnding` owns the letter.
            return None

        following = near.after(at)
        if following is None:
            return None

        if following.letter is L.HAMZA:
            # Muttasil in the same word, munfasil across a boundary -- joined-ness only, so one rule serves both names.
            rule = (
                Rule.MADD_JAIZ_MUNFASIL if final else Rule.MADD_WAJIB_MUTTASIL
            )
            return _classify(rule, at, following.id)

        if following.nucleus.is_silent:
            # A sakin already in the Score is permanent -- `ٱلضَّآلِّينَ` and any muqattaat letter ending in one. Lazim.
            return _classify(Rule.MADD_LAZIM, at, following.id)

        after = near.after(following.id)
        if after is None and boundaries.stopped_on(near.word_of(following.id)):
            # Voweled in the Score, sakin only because the stop lands here -- aridah lissukun, same shape as lazim.
            return _classify(Rule.MADD_ARID_LIL_SUKUN, at, following.id)
        return None


@dataclass(frozen=True, slots=True)
class MaddLeen:
    """A waw or yaa sakin after a fatha, before a letter the stop makes sakin.

    Not a long vowel -- `خَوْف`, `بَيْت` -- so `MaddClass` does not trigger on
    it; the diphthong lengthens only at a pause.
    """

    rule: Rule = Rule.MADD_LEEN
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not slot.nucleus.is_silent:
            return None
        if slot.onset is Onset.GEMINATE:
            return None
        before = near.before(at)
        if before is None or not before.nucleus.is_short:
            return None
        if before.nucleus.quality is not Quality.A:
            return None
        following = near.after(at)
        if following is None or not boundaries.stopped_on(word):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != following.id:
            # Only the letter the stop actually silences counts.
            return None
        return _classify(Rule.MADD_LEEN, at, following.id)


def _classify(rule: Rule, at: SlotId, other: SlotId) -> Verdict:
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants(at, other)), ()
    )
