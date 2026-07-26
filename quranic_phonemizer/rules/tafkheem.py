"""Tafkheem and tarqeeq: which sounds are heavy.

The `COLOUR` phase decides emphasis and ghunnah quality and nothing else.
Imāla, tashīl and ishmām are **canonical Score facts** supplied by
`canon.build` and the Ledger; this phase emits their occurrences so that every
attribution has a `by`, but it does not decide them (ADR-004 §3).

Emphasis spreads onto a following *a* and not onto *i* or *u*, which is why
the frozen alphabet gives the emphatic *a* tokens of its own and gives the
other two none.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Plan, Recolour, SoundFeature, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Phase, Quality, Rule
from ..model.performance import Aspect, Occurrence, Participants

#: The seven letters of istiʿlāʾ, which are heavy wherever they occur.
ALWAYS_HEAVY = frozenset({L.KHA, L.SAD, L.DAD, L.TAH, L.ZAH, L.GHAIN, L.QAF})

#: Rāʾ and the lām of the divine name are heavy conditionally — which is the
#: asymmetry the old implementation encoded by giving rāʾ a module and leaving
#: the lām an inline branch (ADR-004 §1).
CONDITIONAL = frozenset({L.RA, L.LAM})


@dataclass(frozen=True, slots=True)
class Emphasis:
    rule: Rule = Rule.TAFKHEEM
    phase: Phase = Phase.COLOUR
    triggers: frozenset = frozenset(ALWAYS_HEAVY | CONDITIONAL)

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None:
            return None
        heavy = slot.letter in ALWAYS_HEAVY or _conditionally_heavy(near, slot)
        if not heavy:
            return None
        effects = [
            Recolour(at, Aspect.ONSET, SoundFeature.EMPHATIC, True)
        ]
        if _quality(slot) is Quality.A:
            # Emphasis spreads onto a following `a` only. The frozen alphabet
            # has emphatic `a` tokens and no emphatic `i` or `u`.
            effects.append(
                Recolour(at, Aspect.NUCLEUS, SoundFeature.EMPHATIC, True)
            )
        return Verdict(
            Occurrence(mint(Rule.TAFKHEEM, at), Rule.TAFKHEEM,
                       Participants((at,))),
            tuple(effects),
        )


def _conditionally_heavy(near: Neighbourhood, slot) -> bool:
    if slot.letter is L.RA:
        # Heavy with fatha or damma, light with kasra. The pausal cases and
        # the look-back through a sākin belong to phase 5's fuller treatment.
        return _quality(slot) in (Quality.A, Quality.U)
    if slot.letter is L.LAM:
        return _is_divine_lam(near, slot)
    return False


def _is_divine_lam(near: Neighbourhood, slot) -> bool:
    """The lām of `ٱللَّه`, heavy after a fatha or a damma and light after a
    kasra — `بِٱللَّهِ` is the light case.

    Recognised from the Score: a doubled lām carrying a long ā and followed by
    a hāʾ. "Doubled" is two shapes, because a shadda after a *silent* slot
    attests an assimilation rather than stating a gemination (ADR-003 §4.1) —
    so `ٱللَّه` shows as a silent article lām plus a plain one, and `لِلَّه` as a
    genuine `Onset.GEMINATE`. Reading only the second was the bug: it looked
    for a performance fact on the Score.

    The single lām of `إِلَٰه` matches neither, which is what keeps it light.
    """
    if _quality(slot) is not Quality.A:
        return False
    following = near.after(slot.id)
    if following is None or following.letter is not L.HEH:
        return False
    if not _doubled(near, slot):
        return False
    return _preceding_quality(near, slot) in (Quality.A, Quality.U)


def _doubled(near: Neighbourhood, slot) -> bool:
    from ..model.canon import Onset

    if slot.onset is Onset.GEMINATE:
        return True
    before = _before(near, slot)
    return (
        before is not None
        and before.letter is L.LAM
        and before.nucleus.kind is NucleusKind.SILENT
    )


def _preceding_quality(near: Neighbourhood, slot):
    """The vowel actually heard before the lām, skipping the silent article."""
    before = _before(near, slot)
    if before is not None and before.nucleus.kind is NucleusKind.SILENT:
        before = _before(near, before)
    return _quality(before) if before is not None else None


def _before(near: Neighbourhood, slot):
    flat = near.score.slots()
    for index, other in enumerate(flat):
        if other.id == slot.id:
            return flat[index - 1] if index else None
    return None


def _quality(slot):
    return getattr(slot.nucleus, "quality", None)
