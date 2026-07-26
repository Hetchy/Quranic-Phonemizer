"""The nūn family — one rule, one trigger, five outcomes.

This is the slice ADR-004 §8 is about. Under A1's ruling the tanwīn nūn is its
own slot, so **nūn sākinah and tanwīn are literally the same rule on the same
trigger**: a `NOON` slot whose nucleus is `Silent`, merging its `ONSET`. That
is what domain-facts §5.1 says they are — "tanween *is* a short vowel + noon" —
and the old implementation's two separate shapes were the asymmetry.

The five outcomes are mutually exclusive by construction: the trigger letter
falls in exactly one of the five sets below, so E1 can never fire here and a
sixth branch would be a partition error rather than a precedence question.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Phase, Rule, Score
from ..model.performance import (
    Aspect,
    Consonant,
    Nasal,
    NasalPlace,
    Occurrence,
    Participants,
)
from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Plan, Realize, Verdict, mint
from .ownership import is_quiescent

#: The six throat letters. The nūn stays itself.
IZHAR = frozenset({L.HAMZA, L.HEH, L.AIN, L.HA, L.GHAIN, L.KHA})

#: `يرملون` minus the two that carry no ghunnah.
IDGHAM_GHUNNAH = frozenset({L.YA, L.NOON, L.MEEM, L.WAW})
IDGHAM_NO_GHUNNAH = frozenset({L.LAM, L.RA})

#: One letter, and the only one that turns the nūn into a mīm.
IQLAB = frozenset({L.BA})

#: Everything else — the fifteen.
IKHFAA = frozenset(set(L) - IZHAR - IDGHAM_GHUNNAH - IDGHAM_NO_GHUNNAH - IQLAB)


@dataclass(frozen=True, slots=True)
class NoonSakinah:
    """One classifier for the whole family, because the family has one shape."""

    rule: Rule = Rule.IKHFAA_HAQIQI
    phase: Phase = Phase.MERGE
    triggers: frozenset = frozenset({L.NOON})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del boundaries  # `near` already refuses to look across a junction
        here = near.slot(at)
        if not is_quiescent(here):
            return None
        following = near.after(at)
        if following is None:
            return None

        letter = following.letter

        if letter in IZHAR:
            return _classification(Rule.IZHAR_HALQI, at, following.id)
        if letter in IQLAB:
            return _nasal(Rule.IQLAB, at, following.id, NasalPlace.ASSIMILATED)
        if letter in IDGHAM_GHUNNAH and near.crosses_word(at):
            pass
        elif letter in IDGHAM_GHUNNAH:
            # Izhar mutlaq: a nun sakinah before waw or yaa **inside one
            # word** does not assimilate. The four idgham letters merge only
            # across a word boundary, and دنيا، بنيان، قنوان، صنوان are the
            # measured cases. Without this the same nun assimilates in a word
            # where the reading keeps it.
            return _classification(Rule.IZHAR_MUTLAQ, at, following.id)
        if letter in IDGHAM_GHUNNAH:
            return _merge(Rule.IDGHAM_BI_GHUNNAH, at, following, nasal=True)
        if letter in IDGHAM_NO_GHUNNAH:
            return _merge(Rule.IDGHAM_BILA_GHUNNAH, at, following, nasal=False)
        del plan  # pure by signature; this family needs no accumulated plan
        return _nasal(Rule.IKHFAA_HAQIQI, at, following.id, NasalPlace.ASSIMILATED)


def _classification(rule: Rule, at: SlotId, other: SlotId) -> Verdict:
    """Iẓhār produces no sound of its own — the nūn is realized plainly by the
    engine's default. The occurrence still exists, because every attribution
    must have a `by` and a projection must be able to find the iẓhār."""
    return Verdict(Occurrence(mint(rule, at), rule, Participants((at, other))), ())


def _nasal(rule: Rule, at: SlotId, other: SlotId, place: NasalPlace) -> Verdict:
    """Iqlāb and ikhfāʾ replace the nūn's onset with a nasal.

    **The Hafs default is `ASSIMILATED` for both**, which is what the frozen
    snapshot contains; `BILABIAL` is selectable at the 986 measured sites
    once `VariantSelection` reaches this rule.

    `place` is the whole content of the realization khilāf (ADR-006 §3): the
    caller's choice between a hidden mīm and the generic nasal is a
    `NasalPlace`, which is a Sound feature, so it is decided here and never in
    the renderer.
    """
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, other))),
        (Realize(at, Aspect.ONSET, (Nasal(place),)),),
    )


def _merge(rule: Rule, at: SlotId, host, *, nasal: bool) -> Verdict:
    """Idghām: the nūn's onset *is* the following onset, geminated.

    The rule realizes **both** halves. The merged sound belongs to the idghām,
    not to plain realization — that is what P4 means by "a merger is the pair
    of edges sharing a `SoundId` and an `OccurrenceId`", and it is also the
    truth of the matter: the gemination exists *because* of the idghām and
    would otherwise appear from nowhere.

    `nasal` is the bi-/bila-ghunnah split, carried as a Sound feature rather
    than inferred later from the rule name.
    """
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, host.id))),
        (
            Realize(
                host.id,
                Aspect.ONSET,
                (Consonant(host.letter, geminate=True, nasal=nasal),),
            ),
            MergeInto(at, Aspect.ONSET, host.id, Aspect.ONSET),
        ),
    )
