"""Qalqala: the echo on a quiescent plosive, and its three degrees.

The degrees are separate `Rule` members rather than one collapsed tag. The
frozen vocabulary distinguishes them — measured, 3,413 `qalqala_sughra` against
424 `qalqala_kubra` — and collapsing them would be the same failure this design
indicts at `idgham.py:28`, committed in the opposite direction (ADR-002 §5.1).
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Onset, Phase, Rule
from ..model.performance import (
    Aspect,
    Consonant,
    Occurrence,
    Participants,
    Release,
    ReleaseKind,
)

#: `قطب جد` — the five letters that echo when they close a syllable.
QALQALA = frozenset({L.QAF, L.TAH, L.BA, L.JEEM, L.DAL})


@dataclass(frozen=True, slots=True)
class Qalqala:
    rule: Rule = Rule.QALQALA_SUGHRA
    phase: Phase = Phase.RELEASE
    triggers: frozenset = frozenset(QALQALA)

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if plan.merged_away(at, Aspect.ONSET):
            return None  # nothing to release: the closure did not survive MERGE

        # The echo needs an actual closure, so the slot must end up voiceless.
        # Canonically silent is one way; a `BOUNDARY` rule having silenced it
        # is the other. A long final vowel is neither — reading only the stop
        # made qalqala eat it.
        canonically = slot.nucleus.kind is NucleusKind.SILENT
        silenced = plan.merged_away(at, Aspect.NUCLEUS)
        if not (canonically or silenced):
            return None

        if boundaries.stopped_on(word) and _is_last(near, at, word):
            degree = (
                Rule.QALQALA_AKBAR
                if slot.onset is Onset.GEMINATE
                else Rule.QALQALA_KUBRA
            )
        else:
            degree = Rule.QALQALA_SUGHRA

        return Verdict(
            Occurrence(mint(degree, at), degree, Participants((at,))),
            (
                Realize(
                    at,
                    Aspect.NUCLEUS,
                    (Release(ReleaseKind.QALQALA),),
                ),
            ),
        )


def _is_last(near: Neighbourhood, at: SlotId, word: int) -> bool:
    slots = near.score.words[word].slots
    return bool(slots) and slots[-1].id == at
