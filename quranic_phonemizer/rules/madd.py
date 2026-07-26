"""Length at the edges: the glide that becomes the vowel before it.

`هُوَ` is R5's case. At a stop the fatha drops and Hafs does not leave a bare
glide — the wāw merges into the damma before it and the word ends long. A final
yāʾ after a kasra does the same.

It is a `MergedInto` rather than a `Relength` plus a `Silence`, because the two
sounds are one: the pair of edges sharing a `SoundId` *is* the merger, and a
projection asking which letters produced the long vowel gets both of them.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Onset, Phase, Quality, Rule
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
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        if slot.onset is Onset.GEMINATE:
            # A doubled glide is a consonant — `ٱلْعَلِىُّ` ends `-iyy`, not
            # `-ii`. Only a single glide carries the vowel before it.
            return None
        before = _before(near, at)
        if before is None or before.nucleus.kind is not NucleusKind.SHORT:
            return None
        if GLIDE_OF.get(before.nucleus.quality) is not slot.letter:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_TABII, at),
                Rule.MADD_TABII,
                Participants((before.id, at)),
            ),
            (
                # The rule realizes the merged sound itself. `Relength` would
                # leave the long vowel owned by plain realization, and then
                # the two halves of the merger would not share an occurrence
                # — which is exactly what P4 asserts they must.
                Realize(
                    before.id,
                    Aspect.NUCLEUS,
                    (Vowel(before.nucleus.quality, long=True),),
                ),
                MergeInto(at, Aspect.ONSET, before.id, Aspect.NUCLEUS),
            ),
        )


def _before(near: Neighbourhood, at: SlotId):
    flat = near.score.slots()
    for index, slot in enumerate(flat):
        if slot.id == at:
            return flat[index - 1] if index else None
    return None
