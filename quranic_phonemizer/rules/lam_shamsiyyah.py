"""The article's lām: assimilated into a sun letter, or pronounced.

Both members exist. The first draft of the rule vocabulary named
`LAM_QAMARIYYAH` only in prose while the enum had no member, so a projection
could answer the shamsiyyah question and not its complement (ADR-002 §5.1).
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

#: The fourteen sun letters. The article's lām assimilates into each.
SUN = frozenset(
    {
        L.TA, L.THA, L.DAL, L.THAL, L.RA, L.ZAY, L.SEEN, L.SHEEN,
        L.SAD, L.DAD, L.TAH, L.ZAH, L.LAM, L.NOON,
    }
)


@dataclass(frozen=True, slots=True)
class ArticleLam:
    """The one lexeme class this rule needs arrives as a predicate.

    A predicate rather than the `Lexicon` itself, because `rules/` may not
    import `canon/` — the import guard caught the first attempt, correctly.
    What crosses the boundary is a question the rule can ask, not a canon
    type it would then be coupled to. `riwayat/hafs/rules.py` binds it,
    because a riwayah owns its lexicon as well as its rules.

    The default answers "no", which keeps the rule usable on its own and
    makes the untuned behaviour the pre-existing one.
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


def is_article_lam(
    near: Neighbourhood,
    at: SlotId,
    is_form_eight_lam: Callable[[str], bool] | None = None,
) -> bool:
    """A lām immediately after a waṣl hamza, at the head of its word.

    Asked of the Score, not of a glyph: `Onset.WASL` is canonical, so this
    holds identically in both scripts and would hold in a third.

    Two shapes are excluded, and both were wrong in the measured output.
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
            # `بِٱللَّهِ`'s article at index 2, not 1. But form VIII with lām as
            # first radical is shaped identically -- `ٱلْتَقَى` against
            # `ٱلتَّوْبَة` -- and the difference is the shadda, which sits on a
            # slot whose own nucleus is silent and therefore reaches the
            # adapter as an attestation rather than as `Onset.GEMINATE`.
            # Nothing in the Score separates them, so a lexeme does.
            return not (
                is_form_eight_lam is not None
                and is_form_eight_lam(_skeleton(slots))
            )
        # `لِلنَّاسِ` writes no hamza at all -- the lām proclitic swallows it and
        # the article survives only as a quiescent lām. **Only** the lām does
        # this, because only لـ + ال collapses to لل. Accepting the other five
        # proclitics assimilated a root lām in `بَلْدَةً`, `كِلْتُمْ`, `وِلْدَٰنٌ` and
        # the imperative lām of `وَلْتَكُن` -- nine words, all of them ordinary.
        return (
            index == 1
            and before.letter is L.LAM
            and before.nucleus.kind is not NucleusKind.SILENT
        )
    return False


def _skeleton(slots) -> str:
    return "".join(ABJAD[slot.letter.value] for slot in slots)
