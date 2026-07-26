"""Ghunnah on a doubled nūn or mīm, and the mīm sākinah family.

`GHUNNAH_MUSHADDADAH` is not an idghām and never was: nothing merges. A nūn or
mīm carrying `Onset.GEMINATE` is nasalized wherever it stands, which is why it
is a rule of its own rather than a branch inside one.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Phase, Rule
from ..model.performance import Aspect, Consonant, Occurrence, Participants

NASAL_LETTERS = frozenset({L.NOON, L.MEEM})


@dataclass(frozen=True, slots=True)
class GhunnahMushaddadah:
    rule: Rule = Rule.GHUNNAH_MUSHADDADAH
    phase: Phase = Phase.MERGE
    triggers: frozenset = frozenset(NASAL_LETTERS)

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None or slot.letter not in NASAL_LETTERS:
            return None
        if slot.onset is not Onset.GEMINATE:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.GHUNNAH_MUSHADDADAH, at),
                Rule.GHUNNAH_MUSHADDADAH,
                Participants((at,)),
            ),
            (
                Realize(
                    at,
                    Aspect.ONSET,
                    (Consonant(slot.letter, geminate=True, nasal=True),),
                ),
            ),
        )
