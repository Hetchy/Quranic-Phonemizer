"""The article's lam: assimilated into a sun letter, or pronounced.

Both outcomes are named, so a projection can answer the qamariyyah question
as readily as the shamsiyyah one.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from collections.abc import Callable

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import ABJAD
from ..model.canon import CanonLetter as L
from ..model.canon import CanonLetter, NucleusKind, Onset, Phase, Quality, Rule
from ..model.performance import Aspect, Consonant, Occurrence, Participants


def _never(_skeleton: str) -> bool:
    return False


@dataclass(frozen=True, slots=True)
class ArticleShape:
    """Is this vowelless lam the article's? Asked of the Score, never of a
    glyph, so the answer holds in any script.

    Held by both rules that need it, so the shape is stated once.
    """

    prefixes: frozenset[CanonLetter] = frozenset()
    """Letters that may stand between the word's head and the lam proclitic."""

    is_form_eight_lam: Callable[[str], bool] = _never
    """Takes the one lexeme fact it needs as a predicate rather than importing
    `Lexicon`: rules/ may not depend on canon/."""

    def __call__(self, near: Neighbourhood, at: SlotId) -> bool:
        word = near.word_of(at)
        slots = () if word is None else near.score.words[word].slots
        index = next((i for i, slot in enumerate(slots) if slot.id == at), 0)
        if index == 0 or slots[index].letter is not L.LAM:
            return False
        before = slots[index - 1]
        if before.onset is Onset.WASL:
            # Form VIII lam-initial verbs are the same shape and the same
            # Score -- `ٱلْتَقَى` against `ٱلتَّقْوَىٰ` -- because the shadda
            # of an assimilation is attested, not canonical. Read from the
            # article's own slot so a proclitic does not hide the stem.
            return not self.is_form_eight_lam(_skeleton(slots[index - 1:]))
        if _is_ibdal_alif(before):
            # `ءَآلذَّكَرَيْنِ`: after an interrogative hamza the article's own
            # hamza is not written as one, it is the length that replaced it.
            return True
        if before.letter is not L.LAM or before.nucleus.kind is NucleusKind.SILENT:
            return False
        # `لِلنَّاسِ` writes no hamza: the lam proclitic swallows the article's
        # alif. `يُضْلِلْ` is the same pair of lams inside a stem, so what
        # separates them is whether the first lam heads the word.
        return all(slot.letter in self.prefixes for slot in slots[: index - 1])


@dataclass(frozen=True, slots=True)
class ArticleLam:
    sun: frozenset[CanonLetter] = frozenset()
    """The letters the article's lam assimilates into."""

    article: ArticleShape = field(default_factory=ArticleShape)
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
        if not self.article(near, at):
            return None
        following = near.after(at)
        if following is None:
            return None

        if following.letter not in self.sun:
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
                    Consonant(
                        following.letter,
                        geminate=True,
                        nasal=following.letter in (L.NOON, L.MEEM),
                    ),
                ),
                MergeInto(at, Aspect.ONSET, following.id, Aspect.ONSET),
            ),
        )


def _is_ibdal_alif(slot) -> bool:
    return (
        slot.letter is L.HAMZA
        and slot.nucleus.kind is NucleusKind.LONG
        and slot.nucleus.quality is Quality.A
    )


def _skeleton(slots) -> str:
    return "".join(ABJAD[slot.letter.value] for slot in slots)
