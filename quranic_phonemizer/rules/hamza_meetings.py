"""Boundary realization of two adjacent moving qata hamzas."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Classify, Length, Phase, Plan, Realize, Relength, Silence, Verdict, mint
from ..model.address import BoundaryPlan, Location, SlotId
from ..model.canon import Annotation, CanonLetter, Onset, Quality, Rule
from ..model.performance import Aspect, Consonant, Occurrence


_BARE_ANTA = frozenset({Location(5, 116, 7), Location(21, 62, 2)})


@dataclass(frozen=True, slots=True)
class HamzaMeetings:
    rows: Mapping[Location, object]
    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset({CanonLetter.HAMZA})
    emits: frozenset = frozenset({Rule.IBDAL_HAMZA, Rule.TASHIL})

    def _row_at(self, near: Neighbourhood, at: SlotId):
        word = near.word_of(at)
        if word is None:
            return None, None
        location = near.score.words[word].location
        row = self.rows.get(location)
        if row is None:
            return None, None
        slots = near.score.words[word].slots
        if row.scope == "one_word":
            hamzas = [slot for slot in slots if slot.letter is CanonLetter.HAMZA]
            return (row, word) if len(hamzas) >= 2 and hamzas[1].id == at else (None, None)
        if not slots or slots[0].id != at or word == 0:
            return None, None
        left = near.score.words[word - 1]
        if left.location != row.previous or near.after(left.slots[-1].id) is None:
            return None, None
        return row, word

    def look(self, near: Neighbourhood, plan: Plan, at: SlotId, boundaries: BoundaryPlan) -> Verdict | None:
        del plan
        row, word = self._row_at(near, at)
        if row is None:
            return None
        slot = near.slot(at)
        if slot is None:
            return None
        tashil = (
            row.owner == "fixed_tashil"
            or row.owner == "jaa_aal"
            or (row.scope == "one_word" and row.canonical in _BARE_ANTA and boundaries.stopped_on(word))
        )
        boundary = word - 1 if row.scope != "one_word" else None
        if tashil:
            if slot.onset is Onset.TASHIL:
                return None
            return Verdict(
                Occurrence(mint(Rule.TASHIL, at), Rule.TASHIL, (at,), boundary=boundary),
                (Realize(at, Aspect.CONSONANT, Consonant(CanonLetter.HAMZA, eased=True)),),
            )
        moving = row.owner == "fixed_ibdal" or row.owner == "hamza_damm_kasr"
        if moving:
            letter = CanonLetter.YA if row.first is Quality.I else CanonLetter.WAW
            return Verdict(
                Occurrence(mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA, (at,), boundary=boundary),
                (Realize(at, Aspect.CONSONANT, Consonant(letter)),),
            )
        previous = near.before(at)
        if previous is None:
            return None
        actions = (
            Silence(previous.id, Aspect.VOWEL),
            Silence(at, Aspect.CONSONANT),
            Relength(at, Length.LONG),
        )
        following = near.after(at)
        if row.exception == "fused_badal" and following is not None:
            actions += (Silence(following.id, Aspect.CONSONANT),)
        return Verdict(
            Occurrence(mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA, (at,), boundary=boundary),
            actions,
        )


@dataclass(frozen=True, slots=True)
class HamzaMeetingMadd:
    """Classify the incidental long made by a meeting's ibdal face."""

    rule: Rule = Rule.MADD_LAZIM
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({Quality.A, Quality.I, Quality.U})
    emits: frozenset = frozenset({Rule.MADD_LAZIM, Rule.MADD_TABII})

    def look(self, near: Neighbourhood, plan: Plan, at: SlotId, boundaries: BoundaryPlan) -> Verdict | None:
        del boundaries
        if not plan.hamza_meeting_length(at):
            return None
        slot = near.slot(at)
        if slot is not None and Annotation.BADAL in slot.annotations:
            return None
        following = near.after(at)
        lazim = following is not None and (
            following.nucleus.is_silent or following.onset is Onset.GEMINATE
        )
        rule = Rule.MADD_LAZIM if lazim else Rule.MADD_TABII
        context = (following.id,) if following is not None else ()
        return Verdict(
            Occurrence(mint(rule, at), rule, (at,), context),
            (Classify(at, Aspect.VOWEL),),
        )


__all__ = ["HamzaMeetingMadd", "HamzaMeetings"]
