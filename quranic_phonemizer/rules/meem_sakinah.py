"""Ghunnah on a doubled nūn or mīm, and the mīm sākinah family.

`GHUNNAH_MUSHADDADAH` is not an idghām and never was: nothing merges. A nūn or
mīm carrying `Onset.GEMINATE` is nasalized wherever it stands, which is why it
is a rule of its own rather than a branch inside one.

`MeemSakinah` has the same shape as `NoonSakinah` — one classifier, one
trigger, a partition of the alphabet — because it is the same kind of fact.
Giving the two families different shapes was the asymmetry the nūn's docstring
already argues against; the module was named for this family and shipped
without it, so all three of its `Rule` members were dead.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Phase, Rule
from ..model.performance import (
    Aspect,
    Consonant,
    Nasal,
    NasalPlace,
    Occurrence,
    Participants,
)
from .ownership import is_quiescent

NASAL_LETTERS = frozenset({L.NOON, L.MEEM})

#: The mīm hides before a bāʾ and merges into another mīm. Everything else is
#: iẓhār. Three sets, disjoint by construction, so E1 cannot fire inside the
#: family and a fourth branch would be a partition error.
IKHFAA_SHAFAWI = frozenset({L.BA})
IDGHAM_SHAFAWI = frozenset({L.MEEM})
IZHAR_SHAFAWI = frozenset(set(L) - IKHFAA_SHAFAWI - IDGHAM_SHAFAWI)


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


@dataclass(frozen=True, slots=True)
class MeemSakinah:
    """One classifier for the whole family, because the family has one shape."""

    rule: Rule = Rule.IZHAR_SHAFAWI
    phase: Phase = Phase.MERGE
    triggers: frozenset = frozenset({L.MEEM})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries  # `near` already refuses to look across a junction
        here = near.slot(at)
        if not is_quiescent(here):
            return None
        following = near.after(at)
        if following is None:
            return None

        letter = following.letter
        if letter in IKHFAA_SHAFAWI:
            # The mīm is hidden with ghunnah, not replaced. `ASSIMILATED` is
            # the same default the nūn's ikhfāʾ takes and what the frozen
            # oracle contains; `BILABIAL` is arguably the better *phonetic*
            # description of lips meeting lightly for the bāʾ, and the render
            # map has a symbol for it. Changing it is a deliberate notation
            # decision with 495 sites behind it, not something to slip in
            # while restoring a missing family.
            return Verdict(
                Occurrence(
                    mint(Rule.IKHFAA_SHAFAWI, at),
                    Rule.IKHFAA_SHAFAWI,
                    Participants((at, following.id)),
                ),
                (Realize(at, Aspect.ONSET, (Nasal(NasalPlace.ASSIMILATED),)),),
            )
        if letter in IDGHAM_SHAFAWI:
            return Verdict(
                Occurrence(
                    mint(Rule.IDGHAM_SHAFAWI, at),
                    Rule.IDGHAM_SHAFAWI,
                    Participants((at, following.id)),
                ),
                (
                    Realize(
                        following.id,
                        Aspect.ONSET,
                        (Consonant(L.MEEM, geminate=True, nasal=True),),
                    ),
                    MergeInto(at, Aspect.ONSET, following.id, Aspect.ONSET),
                ),
            )
        # Iẓhār shafawī produces no sound of its own — the mīm is realized
        # plainly by the engine's default. The occurrence still exists so that
        # a projection can find it, which is the point of the family.
        return Verdict(
            Occurrence(
                mint(Rule.IZHAR_SHAFAWI, at),
                Rule.IZHAR_SHAFAWI,
                Participants((at, following.id)),
            ),
            (),
        )
