"""The idghām families that are not the nūn's: like into like, near into near.

The old implementation collapsed four named rules into one condition — a bare
consonant followed by a silent one — and the rule names were lost. Each is
separate here, because a projection that cannot say *which* idghām fired is
not a tajweed projection, and because the four have different outcomes.

Only cross-boundary assimilation lives here. A geminate written in the rasm is
canonical (`Onset.GEMINATE`) and needs no rule at all.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Phase, Rule
from ..model.performance import Aspect, Consonant, Occurrence, Participants
from .lam_shamsiyyah import is_article_lam

#: Pairs that share a place of articulation and merge completely.
KAMIL: dict[tuple[L, L], Rule] = {
    (L.DAL, L.TA): Rule.IDGHAM_MUTAJANISAYN_KAMIL,
    (L.TA, L.TAH): Rule.IDGHAM_MUTAJANISAYN_KAMIL,
    (L.THAL, L.ZAH): Rule.IDGHAM_MUTAJANISAYN_KAMIL,
    (L.THA, L.THAL): Rule.IDGHAM_MUTAJANISAYN_KAMIL,
    (L.BA, L.MEEM): Rule.IDGHAM_MUTAJANISAYN_KAMIL,
}

#: Pairs that merge while the first keeps a trace of itself.
NAQIS: dict[tuple[L, L], Rule] = {
    (L.TAH, L.TA): Rule.IDGHAM_MUTAJANISAYN_NAQIS,
}

#: Neighbours in place, not identical: lām into rāʾ, and the qāf of `نَخْلُقكُّم`.
MUTAQARIBAYN: dict[tuple[L, L], Rule] = {
    (L.LAM, L.RA): Rule.IDGHAM_MUTAQARIBAYN,
    (L.QAF, L.KAF): Rule.IDGHAM_MUTAQARIBAYN,
}


@dataclass(frozen=True, slots=True)
class Idgham:
    """One classifier, three tables — the shape is identical, so the code is.

    Which table a pair falls in is data. Giving each family its own `look`
    would reintroduce the per-letter dispatch that ADR-004 §1 removes.
    """

    rule: Rule = Rule.IDGHAM_MUTAMATHILAYN
    phase: Phase = Phase.MERGE
    triggers: frozenset = frozenset(
        {letter for pair in (*KAMIL, *NAQIS, *MUTAQARIBAYN) for letter in pair}
        | {L.DAL, L.TA, L.TAH, L.THAL, L.THA, L.BA, L.LAM, L.QAF, L.MEEM}
    )

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        here = near.slot(at)
        if here is None or here.nucleus.kind is not NucleusKind.SILENT:
            return None
        if is_article_lam(near, at):
            # `ٱللَّهِ` is lām shamsiyyah, not like-into-like. The two families
            # must be mutually exclusive rather than ranked — E1 exists to
            # catch the day they overlap, and it did.
            return None
        following = near.after(at)
        if following is None:
            return None

        pair = (here.letter, following.letter)
        if here.letter is following.letter:
            rule = Rule.IDGHAM_MUTAMATHILAYN
        elif pair in KAMIL:
            rule = KAMIL[pair]
        elif pair in NAQIS:
            rule = NAQIS[pair]
        elif pair in MUTAQARIBAYN:
            rule = MUTAQARIBAYN[pair]
        else:
            return None

        if rule is Rule.IDGHAM_MUTAJANISAYN_NAQIS:
            # The first letter survives as a colour on the second rather than
            # vanishing into it, so nothing merges and the pair is recorded
            # for the projection alone.
            return Verdict(
                Occurrence(mint(rule, at), rule, Participants((at, following.id))),
                (),
            )
        return Verdict(
            Occurrence(mint(rule, at), rule, Participants((at, following.id))),
            (
                Realize(
                    following.id,
                    Aspect.ONSET,
                    (Consonant(following.letter, geminate=True),),
                ),
                MergeInto(at, Aspect.ONSET, following.id, Aspect.ONSET),
            ),
        )
