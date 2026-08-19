"""The noon family: one trigger, five outcomes.

A tanween noon is a slot like any other, so noon sakinah and tanween are the
same rule on the same trigger.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    MergeInto,
    Phase,
    Plan,
    Realize,
    Recolour,
    SoundFeature,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, Junction, KhilafId, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Rule, SlotOrigin
from ..model.performance import Aspect, Consonant, Occurrence, Participants
from .ownership import is_quiescent
from .khilaf import DEFAULT_NASAL_PLACE, nasal_place
from .tables import Followers


@dataclass(frozen=True, slots=True)
class NoonSakinah:
    """One classifier for the whole family, because the family has one shape."""

    followers: Followers
    opening_wasl: object | None = None
    rule: Rule = Rule.IKHFAA_HAQIQI
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=frozenset({L.NOON}))

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        # A repair that broke a meeting of two quiescent letters leaves this one
        # voweled, and a voweled letter is not a sakin at all.
        if not is_quiescent(slot) or plan.voweled(at):
            return None
        opening = self._opening_wasl(near, at, boundaries)
        if opening is not None:
            choice = self.opening_wasl.choose(near.score.selection)
            if choice == "izhar":
                return _classification(Rule.IZHAR, at, None)
            return _merge(Rule.IDGHAM_BI_GHUNNAH, at, opening, ghunnah=True)
        following = near.after(at)
        if following is None:
            if slot.origin is SlotOrigin.SPELLED and near.last_of_word(at):
                # The noon closing a disjoined-letter opening takes its own
                # plain articulation rather than reaching into the next word.
                return _classification(Rule.IZHAR, at, None)
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
                return _merge(Rule.IDGHAM_BI_GHUNNAH, at, following, ghunnah=True)
            case Rule.IDGHAM_BILA_GHUNNAH:
                return _merge(
                    Rule.IDGHAM_BILA_GHUNNAH, at, following, ghunnah=False
                )
        # Ikhfaa haqiqi has no khilaf: it is not a bilabial hiding.
        return _nasal(
            Rule.IKHFAA_HAQIQI, at, following.id, DEFAULT_NASAL_PLACE
        )

    def _opening_wasl(self, near, at, boundaries):
        word = near.word_of(at)
        if self.opening_wasl is None or word is None:
            return None
        if boundaries.after(word) is not Junction.JOIN:
            return None
        location = near.score.words[word].location
        if location not in self.opening_wasl.locations or not near.last_of_word(at):
            return None
        following = near.raw_after(at)
        if following is None or following.letter is not L.WAW:
            return None
        return following


def _between_names(slot, following) -> bool:
    """Letter names are said one after another, so the seam between two of
    them is a word boundary the Score writes inside one word. Every name
    that holds a quiescent noon ends on it, so a spelled pair is that seam."""
    return (
        slot is not None
        and slot.origin is SlotOrigin.SPELLED
        and following.origin is SlotOrigin.SPELLED
    )


def _classification(rule: Rule, at: SlotId, other: SlotId | None) -> Verdict:
    """Izhar produces no sound of its own; the occurrence exists so a
    projection can find it."""
    return Verdict(Occurrence(mint(rule, at), rule, Participants(at, other)), ())


def _nasal(rule: Rule, at: SlotId, other: SlotId, letter: L) -> Verdict:
    """Iqlab and ikhfaa realize the noon as a hum on the letter it rides."""
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants(at, other)),
        (Realize(at, Aspect.CONSONANT, Consonant(letter, ghunnah=True)),),
    )


def _merge(rule: Rule, at: SlotId, host, *, ghunnah: bool) -> Verdict:
    """Idgham: the noon's onset is the following onset, geminated.

    Both halves are realized here. The gemination exists because of the
    idgham, so the merged sound belongs to it and not to plain realization.
    """
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants(at, host.id)),
        (
            Realize(
                host.id,
                Aspect.CONSONANT,
                Consonant(host.letter, geminate=True, ghunnah=ghunnah),
            ),
            MergeInto(at, Aspect.CONSONANT, host.id, Aspect.CONSONANT),
        ),
    )


@dataclass(frozen=True, slots=True)
class IkhfaaWeight:
    """Ikhfaa haqiqi's hum is heavy before an istilaa letter: the same set
    `Weight` reads, naming the same rule it names."""

    followers: Followers
    always_heavy: frozenset[L] = frozenset()
    rule: Rule = Rule.TAFKHEEM
    phase: Phase = Phase.COLOUR
    triggers: frozenset = field(default=frozenset({L.NOON}))

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        if not is_quiescent(near.slot(at)):
            return None
        following = near.after(at)
        if following is None or following.letter not in self.always_heavy:
            return None
        if self.followers.of(following.letter) is not None:
            return None  # izhar, iqlab or idgham owns this pair instead
        return Verdict(
            Occurrence(
                mint(Rule.TAFKHEEM, at), Rule.TAFKHEEM, Participants(at)
            ),
            (Recolour(at, Aspect.CONSONANT, SoundFeature.EMPHATIC, True),),
        )
