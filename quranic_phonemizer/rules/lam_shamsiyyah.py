"""The article's lam: assimilated into a sun letter, or pronounced.

Both outcomes are named, so a projection can answer the qamariyyah question
as readily as the shamsiyyah one.
"""
from __future__ import annotations

from dataclasses import dataclass

from collections.abc import Callable

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import ABJAD
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Onset, Phase, Rule
from ..model.performance import Aspect, Consonant, Occurrence, Participants

#: The fourteen sun letters. The article's lam assimilates into each.
SUN = frozenset(
    {
        L.TA, L.THA, L.DAL, L.THAL, L.RA, L.ZAY, L.SEEN, L.SHEEN,
        L.SAD, L.DAD, L.TAH, L.ZAH, L.LAM, L.NOON,
    }
)


@dataclass(frozen=True, slots=True)
class ArticleLam:
    """Takes the one lexeme fact it needs as a predicate rather than
    importing `Lexicon` directly -- rules/ may not depend on canon/.

    Defaults to "no", so the rule works untuned on its own.
    """

    is_form_eight_lam: Callable[[str], bool] = lambda _skeleton: False
    rule: Rule = Rule.LAM_SHAMSIYYAH
    phase: Phase = Phase.MERGE
    triggers: frozenset = frozenset({L.LAM})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None or slot.nucleus.kind is not NucleusKind.SILENT:
            return None
        if not is_article_lam(near, at, self.is_form_eight_lam):
            return None
        following = near.after(at)
        if following is None:
            return None

        if following.letter not in SUN:
            # Izhar of the lam: realized by the default; the occurrence names
            # it so a projection can find it.
            return Verdict(
                Occurrence(
                    mint(Rule.LAM_QAMARIYYAH, at),
                    Rule.LAM_QAMARIYYAH,
                    Participants((at, following.id)),
                ),
                (),
            )
        return Verdict(
            Occurrence(
                mint(Rule.LAM_SHAMSIYYAH, at),
                Rule.LAM_SHAMSIYYAH,
                Participants((at, following.id)),
            ),
            (
                Realize(
                    following.id,
                    Aspect.ONSET,
                    (
                        Consonant(
                            following.letter,
                            geminate=True,
                            nasal=following.letter in (L.NOON, L.MEEM),
                        ),
                    ),
                ),
                MergeInto(at, Aspect.ONSET, following.id, Aspect.ONSET),
            ),
        )


def is_article_lam(
    near: Neighbourhood,
    at: SlotId,
    is_form_eight_lam: Callable[[str], bool] | None = None,
) -> bool:
    """A lam immediately after a wasl hamza, at the head of its word.

    Asked of the Score, not of a glyph, so this holds in any script;
    two shapes are excluded below.
    """
    word = near.word_of(at)
    if word is None:
        return False
    slots = near.score.words[word].slots
    for index, slot in enumerate(slots):
        if slot.id != at:
            continue
        if index == 0:
            return False
        before = slots[index - 1]
        if before.onset is Onset.WASL:
            # The ordinary shape, wherever the word starts. Form VIII
            # lam-initial verbs look identical -- `ٱلْتَقَى` vs `ٱلتَّوْبَة` --
            # so a lexeme predicate is what tells them apart.
            return not (
                is_form_eight_lam is not None
                and is_form_eight_lam(_skeleton(slots))
            )
        # `لِلنَّاسِ` has no hamza -- the lam proclitic swallows it. Only the
        # lam does this, since لـ + ال alone collapses to لل.
        return (
            index == 1
            and before.letter is L.LAM
            and before.nucleus.kind is not NucleusKind.SILENT
        )
    return False


def _skeleton(slots) -> str:
    return "".join(ABJAD[slot.letter.value] for slot in slots)
