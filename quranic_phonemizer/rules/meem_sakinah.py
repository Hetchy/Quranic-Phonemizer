"""Ghunnah on a doubled noon or meem, and the meem sakinah family."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, KhilafId, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Rule
from ..model.performance import (
    Aspect,
    Consonant,
    Nasal,
    Occurrence,
    Participants,
)
from .ownership import is_quiescent
from .khilaf import nasal_place
from .tables import Followers

NASAL_LETTERS = frozenset({L.NOON, L.MEEM})


@dataclass(frozen=True, slots=True)
class GhunnahMushaddadah:
    """A doubled noon or meem is nasalized wherever it stands. Nothing merges,
    so this is not an idgham."""

    rule: Rule = Rule.GHUNNAH_MUSHADDADAH
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=NASAL_LETTERS)

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
                Participants(at),
            ),
            (
                Realize(
                    at,
                    Aspect.CONSONANT,
                    Consonant(slot.letter, geminate=True, nasal=True),
                ),
            ),
        )


@dataclass(frozen=True, slots=True)
class MeemSakinah:
    """One classifier for the whole family, because the family has one shape."""

    followers: Followers
    rule: Rule = Rule.IZHAR_SHAFAWI
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=frozenset({L.MEEM}))

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries  # `near` already refuses to look across a junction
        if not is_quiescent(near.slot(at)):
            return None
        following = near.after(at)
        if following is None:
            return None

        match self.followers.of(following.letter):
            case Rule.IKHFAA_SHAFAWI:
                # Hidden with ghunnah, not replaced.
                return _verdict(
                    Rule.IKHFAA_SHAFAWI, at, following.id,
                    (
                        Realize(
                            at,
                            Aspect.CONSONANT,
                            Nasal(nasal_place(
                                near.score.selection,
                                KhilafId.IKHFAA_SHAFAWI_NASAL,
                            )),
                        ),
                    ),
                )
            case Rule.IDGHAM_SHAFAWI:
                return _verdict(
                    Rule.IDGHAM_SHAFAWI, at, following.id,
                    (
                        Realize(
                            following.id,
                            Aspect.CONSONANT,
                            Consonant(L.MEEM, geminate=True, nasal=True),
                        ),
                        MergeInto(at, Aspect.CONSONANT, following.id, Aspect.CONSONANT),
                    ),
                )
        # Izhar shafawi produces no sound of its own; the occurrence exists so
        # a projection can find it.
        return _verdict(Rule.IZHAR_SHAFAWI, at, following.id, ())


def _verdict(rule: Rule, at: SlotId, other: SlotId, effects: tuple) -> Verdict:
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants(at, other)), effects
    )
