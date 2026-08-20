"""Fakk al-idgham: a word-initial shadda the rasm owes to the word before it.

Starting the reading there instead of joining into it means the merger that
would have written it never fired, so the letter is said plain.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Phase, Plan, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Rule, Slot, SlotOrigin
from ..model.performance import Occurrence
from .ownership import is_quiescent
from .tables import Followers, Pairs


@dataclass(frozen=True, slots=True)
class FakkIdgham:
    """The converse of every cross-word merger family at once: same table,
    read from the following word looking back instead of forward."""

    pairs: Pairs
    followers_of_noon: Followers
    followers_of_meem: Followers
    never_follows: frozenset = frozenset()
    rule: Rule = Rule.FAKK_IDGHAM
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=frozenset())

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not (boundaries.started_on(word) and near.first_of_word(at)):
            return None
        before = near.before(at)
        if before is None or before.origin is SlotOrigin.SPELLED:
            return None
        if not self._would_merge(before, slot.letter):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.FAKK_IDGHAM, at), Rule.FAKK_IDGHAM, (at,),
                (before.id,), boundary=word - 1 if word else None,
            ),
            (),
        )

    def _would_merge(self, before: Slot, letter: L) -> bool:
        if before.letter is L.NOON:
            return is_quiescent(before) and self.followers_of_noon.of(letter) in (
                Rule.IDGHAM_BI_GHUNNAH, Rule.IDGHAM_BILA_GHUNNAH,
            )
        if before.letter is L.MEEM:
            return (
                is_quiescent(before)
                and self.followers_of_meem.of(letter) is Rule.IDGHAM_SHAFAWI
            )
        if before.letter in self.never_follows or not before.nucleus.is_silent:
            return False
        if before.letter is letter:
            return True
        return self.pairs.of(before.letter, letter) not in (
            None, Rule.IDGHAM_MUTAJANISAYN_NAQIS,
        )
