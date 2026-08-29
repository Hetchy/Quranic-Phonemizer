"""Boundary realization of two adjacent moving qata hamzas."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Classify,
    Length,
    MergeInto,
    Phase,
    Plan,
    Realize,
    Relength,
    Silence,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, Location, SlotId
from ..model.canon import Annotation, CanonLetter, Onset, Quality, Rule
from ..model.performance import Aspect, Consonant, Occurrence

_BARE_ANTA = frozenset({Location(5, 116, 7), Location(21, 62, 2)})

#: The fixed face an unbound selector owner realizes, matching the reading
#: each register row was reviewed against.
_UNBOUND = {
    "hamza_dhat_fath": "ibdal",
    "hamza_muttafiq": "ibdal",
    "hamza_damm_kasr": "ibdal",
    "jaa_aal": "tashil",
    "hamza_kasr_yaa": "ibdal",
}


#: Selector owner tags in the authored register, with the face each option
#: realizes. `merge` folds the second qata into the first vowel's long;
#: `moving` replaces it with a consonantal carrier keeping its own vowel.
_SELECTOR_FACES = {
    "hamza_dhat_fath": {"ibdal": "merge", "tashil": "tashil"},
    "hamza_muttafiq": {"ibdal": "merge", "tashil": "tashil"},
    "hamza_damm_kasr": {"ibdal": "moving", "tashil": "tashil"},
    "jaa_aal": {"ibdal": "merge", "tashil": "tashil"},
    "hamza_kasr_yaa": {
        "ibdal": "merge", "tashil": "tashil", "yaa": "moving",
    },
}


@dataclass(frozen=True, slots=True)
class HamzaMeetings:
    rows: Mapping[Location, object]
    choices: Mapping[str, object] = field(default_factory=dict)
    """Selector owner tag to its `VariantDefinition`; an unbound owner
    realizes the fixed face its register row implies."""

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
        if (
            left.location != row.previous
            or not left.slots
            or left.slots[-1].letter is not CanonLetter.HAMZA
            or near.after(left.slots[-1].id) is None
        ):
            return None, None
        return row, word

    def _chosen(self, owner: str, near: Neighbourhood, fixed: str) -> str:
        definition = self.choices.get(owner)
        if definition is None:
            return fixed
        return definition.choose(near.score.selection)

    def _face(self, row, word, near, boundaries) -> str:
        if row.owner == "fixed_tashil":
            if row.exception == "aimma":
                chosen = self._chosen("hamza_aimma", near, "tashil")
                return "tashil" if chosen == "tashil" else "moving"
            return "tashil"
        if row.owner == "fixed_ibdal":
            return "moving"
        face = _SELECTOR_FACES[row.owner][
            self._chosen(row.owner, near, _UNBOUND[row.owner])
        ]
        if (
            face == "merge"
            and row.canonical in _BARE_ANTA
            and boundaries.stopped_on(word)
        ):
            # The ibdal face would end three sakins deep at a full stop, so
            # the selection is masked to tashil in that one boundary state.
            return "tashil"
        return face

    def look(self, near: Neighbourhood, plan: Plan, at: SlotId, boundaries: BoundaryPlan) -> Verdict | None:
        del plan
        row, word = self._row_at(near, at)
        if row is None:
            return None
        slot = near.slot(at)
        if slot is None:
            return None
        face = self._face(row, word, near, boundaries)
        boundary = word - 1 if row.scope != "one_word" else None
        if face == "tashil":
            if slot.onset is Onset.TASHIL:
                return None
            return Verdict(
                Occurrence(mint(Rule.TASHIL, at), Rule.TASHIL, (at,), boundary=boundary),
                (Realize(at, Aspect.CONSONANT, Consonant(CanonLetter.HAMZA, eased=True)),),
            )
        if face == "moving":
            letter = (
                CanonLetter.YA
                if row.exception == "aimma" or row.first is Quality.I
                else CanonLetter.WAW
            )
            actions = [
                Realize(at, Aspect.CONSONANT, Consonant(letter)),
            ]
            if slot.nucleus.sounds_long:
                actions.append(Relength(at, Length.SHORT))
            return Verdict(
                Occurrence(mint(Rule.IBDAL_HAMZA, at), Rule.IBDAL_HAMZA, (at,), boundary=boundary),
                tuple(actions),
            )
        previous = near.before(at)
        if previous is None:
            return None
        actions = (
            MergeInto(previous.id, Aspect.VOWEL, at, Aspect.VOWEL),
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
