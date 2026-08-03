"""The noon family: one trigger, five outcomes.

A tanween noon is a slot like any other, so noon sakinah and tanween are the
same rule on the same trigger.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, KhilafId, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Rule, SlotOrigin
from ..model.performance import (
    Aspect,
    Consonant,
    Nasal,
    NasalPlace,
    Occurrence,
    Participants,
)
from .ownership import is_quiescent
from .khilaf import DEFAULT_NASAL_PLACE, nasal_place
from .tables import Followers


@dataclass(frozen=True, slots=True)
class NoonSakinah:
    """One classifier for the whole family, because the family has one shape."""

    followers: Followers
    rule: Rule = Rule.IKHFAA_HAQIQI
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=frozenset({L.NOON}))

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
            case Rule.IZHAR:
                return _classification(Rule.IZHAR, at, following.id)
            case Rule.IQLAB:
                return _nasal(
                    Rule.IQLAB, at, following.id,
                    nasal_place(near.score.selection, KhilafId.IQLAB_NASAL),
                )
            case Rule.IDGHAM_BI_GHUNNAH:
                if not near.crosses_word(at) and not _between_names(
                    near.slot(at), following
                ):
                    # Izhar mutlaq: inside one word the noon keeps itself.
                    # دنيا، بنيان، قنوان، صنوان are the only sites.
                    return _classification(Rule.IZHAR, at, following.id)
                return _merge(Rule.IDGHAM_BI_GHUNNAH, at, following, nasal=True)
            case Rule.IDGHAM_BILA_GHUNNAH:
                return _merge(
                    Rule.IDGHAM_BILA_GHUNNAH, at, following, nasal=False
                )
        # Ikhfaa haqiqi has no khilaf: it is not a bilabial hiding.
        return _nasal(
            Rule.IKHFAA_HAQIQI, at, following.id, DEFAULT_NASAL_PLACE
        )


def _between_names(slot, following) -> bool:
    """Letter names are said one after another, so the seam between two of
    them is a word boundary the Score writes inside one word. Every name
    that holds a quiescent noon ends on it, so a spelled pair is that seam."""
    return (
        slot is not None
        and slot.origin is SlotOrigin.SPELLED
        and following.origin is SlotOrigin.SPELLED
    )


def _classification(rule: Rule, at: SlotId, other: SlotId) -> Verdict:
    """Izhar produces no sound of its own; the occurrence exists so a
    projection can find it."""
    return Verdict(Occurrence(mint(rule, at), rule, Participants((at, other))), ())


def _nasal(
    rule: Rule, at: SlotId, other: SlotId, place: NasalPlace
) -> Verdict:
    """Iqlab and ikhfaa replace the noon's onset with a nasal."""
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, other))),
        (Realize(at, Aspect.CONSONANT, Nasal(place)),),
    )


def _merge(rule: Rule, at: SlotId, host, *, nasal: bool) -> Verdict:
    """Idgham: the noon's onset is the following onset, geminated.

    Both halves are realized here. The gemination exists because of the
    idgham, so the merged sound belongs to it and not to plain realization.
    """
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, host.id))),
        (
            Realize(
                host.id,
                Aspect.CONSONANT,
                Consonant(host.letter, geminate=True, nasal=nasal),
            ),
            MergeInto(at, Aspect.CONSONANT, host.id, Aspect.CONSONANT),
        ),
    )
