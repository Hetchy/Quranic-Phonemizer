"""The idgham families that are not the noon's: like into like, near into near.

Only cross-boundary assimilation. A geminate written in the rasm is canonical
and needs no rule.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import CanonLetter, Rule
from ..model.performance import Aspect, Consonant, Occurrence, Participants
from .lam_shamsiyyah import ArticleShape
from .meem_sakinah import NASAL_LETTERS
from .tables import Pairs


#: Noon and meem have their own families, which handle their same-letter case.
OWNED_ELSEWHERE = frozenset({L.NOON, L.MEEM})


@dataclass(frozen=True, slots=True)
class Idgham:
    """One classifier over the pair table; which family a pair falls in is
    data, so a per-family `look` would be the same body three times."""

    pairs: Pairs
    never_follows: frozenset[CanonLetter] = frozenset()
    article: ArticleShape = field(default_factory=ArticleShape)
    rule: Rule = Rule.IDGHAM_MUTAMATHILAYN
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=frozenset())

    def __post_init__(self) -> None:
        # Like into like fires on any repeated letter, so the trigger set is
        # the alphabet rather than whatever letters the pair table mentions.
        object.__setattr__(
            self,
            "triggers",
            frozenset(set(CanonLetter) - OWNED_ELSEWHERE - self.never_follows),
        )

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        here = near.slot(at)
        if here is None or not here.nucleus.is_silent:
            return None
        if self.article(near, at):
            return None  # lam shamsiyyah owns this slot
        following = near.after(at)
        if following is None:
            return None

        if here.letter is following.letter:
            rule = Rule.IDGHAM_MUTAMATHILAYN
        else:
            rule = self.pairs.of(here.letter, following.letter)
            if rule is None:
                return None

        occurrence = Occurrence(
            mint(rule, at), rule, Participants(at, following.id)
        )
        if rule is Rule.IDGHAM_MUTAJANISAYN_NAQIS:
            # The first letter survives as a colour on the second, so nothing
            # merges and the pair is recorded for the projection alone.
            return Verdict(occurrence, ())
        return Verdict(
            occurrence,
            (
                Realize(
                    following.id,
                    Aspect.CONSONANT,
                    Consonant(
                        following.letter,
                        geminate=True,
                        # A doubled noon or meem is held on its ghunnah
                        # wherever it stands, and one the idgham doubled is
                        # no different: the meem of `ٱرْكَب مَّعَنَا` is nasal,
                        # exactly as `GhunnahMushaddadah` would have made it
                        # had the rasm written the shadda for itself.
                        nasal=following.letter in NASAL_LETTERS,
                    ),
                ),
                MergeInto(at, Aspect.CONSONANT, following.id, Aspect.CONSONANT),
            ),
        )
