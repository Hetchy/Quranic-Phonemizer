"""The final glide a stop turns into its vowel's length."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Quality, Rule
from ..model.performance import Aspect, Occurrence, Vowel

#: Which glide lengthens which vowel.
GLIDE_OF = {Quality.U: L.WAW, Quality.I: L.YA}


@dataclass(frozen=True, slots=True)
class PausalGlide:
    rule: Rule = Rule.MADD_TABII
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})
    emits: frozenset = frozenset({Rule.MADD_TABII})

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
                (at,),
            ),
            (
                # The merged sound lets both halves share one occurrence.
                Realize(
                    before.id,
                    Aspect.VOWEL,
                    Vowel(before.nucleus.quality, long=True),
                ),
                MergeInto(at, Aspect.CONSONANT, before.id, Aspect.VOWEL),
            ),
        )


__all__ = ["GLIDE_OF", "PausalGlide"]
