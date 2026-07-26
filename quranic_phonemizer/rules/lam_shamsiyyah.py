"""The article's lām: assimilated into a sun letter, or pronounced.

Both members exist. The first draft of the rule vocabulary named
`LAM_QAMARIYYAH` only in prose while the enum had no member, so a projection
could answer the shamsiyyah question and not its complement (ADR-002 §5.1).
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Onset, Phase, Rule
from ..model.performance import Aspect, Consonant, Occurrence, Participants

#: The fourteen sun letters. The article's lām assimilates into each.
#: The particles that may carry the article with no hamza written.
PROCLITICS = frozenset({L.LAM, L.BA, L.KAF, L.WAW, L.FA, L.TA})

#: The particles that may carry the article with no hamza written.
PROCLITICS = frozenset({L.LAM, L.BA, L.KAF, L.WAW, L.FA, L.TA})

SUN = frozenset(
    {
        L.TA, L.THA, L.DAL, L.THAL, L.RA, L.ZAY, L.SEEN, L.SHEEN,
        L.SAD, L.DAD, L.TAH, L.ZAH, L.LAM, L.NOON,
    }
)


@dataclass(frozen=True, slots=True)
class ArticleLam:
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
        if not _is_article_lam(near, at):
            return None
        following = near.after(at)
        if following is None:
            return None

        if following.letter not in SUN:
            # Iẓhār of the lām. Classification-only: the lām is realized by
            # the engine's default, and the occurrence exists so a projection
            # can find the qamariyyah as readily as the shamsiyyah.
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


def _is_article_lam(near: Neighbourhood, at: SlotId) -> bool:
    """A lām immediately after a waṣl hamza, at the head of its word.

    Asked of the Score, not of a glyph: `Onset.WASL` is canonical, so this
    holds identically in both scripts and would hold in a third.
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
            # The ordinary shape, wherever the word starts: a proclitic puts
            # `بِٱللَّهِ`'s article at index 2, not 1.
            return True
        # `لِلنَّاسِ` writes no hamza at all — the lām proclitic swallows it and
        # the article survives only as a quiescent lām. The proclitic has to
        # be named, or `قُلْنَا` matches the same shape and assimilates a root
        # lām that never assimilates.
        return (
            index == 1
            and before.letter in PROCLITICS
            and before.nucleus.kind is not NucleusKind.SILENT
        )
    return False
