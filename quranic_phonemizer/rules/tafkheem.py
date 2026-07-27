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
from ..model.canon import NucleusKind, Onset, Phase, Quality, Rule
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
        del boundaries
        slot = near.slot(at)
        if slot is None:
            return None
        heavy = slot.letter in ALWAYS_HEAVY or _conditionally_heavy(
            near, slot, plan
        )
        if not heavy:
            return None
        effects = [
            Recolour(at, Aspect.ONSET, SoundFeature.EMPHATIC, True)
        ]
        if _quality(slot) is Quality.A and not _silenced(plan, slot):
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


def _conditionally_heavy(near: Neighbourhood, slot, plan) -> bool:
    if slot.letter is L.RA:
        own = None if _silenced(plan, slot) else _quality(slot)
        if own is not None:
            return own in (Quality.A, Quality.U)
        before = _before(near, slot)
        if (
            before is not None
            and before.letter is L.YA
            and before.nucleus.kind is NucleusKind.SILENT
        ):
            # A rāʾ after a leen yāʾ follows the yāʾ and stays light.
            # Looking past the yāʾ to the fatha calls it heavy.
            return False
        following = near.after(slot.id)
        if following is not None and following.letter in ALWAYS_HEAVY:
            # A quiescent rāʾ followed by a letter of istiʿlāʾ is heavy
            # whatever precedes it: `قِرْطَاسٍ` has a genuine kasra before the
            # rāʾ and is still heavy, because the qāf behind it wins.
            # docs/hafs/research/tafkheem_tarqeeq.md documents this and the
            # rule was written without it.
            return True
        # A quiescent rāʾ takes its weight from the vowel before it: `ٱلْأَرْضَ`
        # is heavy after a fatha, `قَدِيرٌ` light after a long ī. Without the
        # look-back the rule sees no vowel at all and calls every sākin rāʾ
        # light.
        governing = _governing(near, slot, plan)
        if governing is None:
            return False
        if _quality(governing) is Quality.I and governing.onset is Onset.WASL:
            # Only an *original* kasra lightens. The waṣl hamza's is ʿāriḍ --
            # it exists to be started on and vanishes at a join -- so
            # `ٱرْتَبْتُمْ` is heavy. This belongs to the rāʾ and not to
            # `_governing`: the divine lām is heavy *because of* a waṣl fatha
            # in `ٱللَّهُ`, and hiding the waṣl vowel from every caller made
            # 2,413 words light that are not.
            return True
        return _quality(governing) in (Quality.A, Quality.U)
    if slot.letter is L.LAM:
        return _is_divine_lam(near, slot, plan)
    return False


def _silenced(plan, slot) -> bool:
    """A nucleus a `BOUNDARY` rule removed.

    `COLOUR` runs after `BOUNDARY`, so a rāʾ that lost its kasra at a stop is
    governed by the vowel before it instead.
    """
    return plan.merged_away(slot.id, Aspect.NUCLEUS)


def _is_divine_lam(near: Neighbourhood, slot, plan) -> bool:
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
    if slot.nucleus.kind is not NucleusKind.LONG:
        # The name carries a **long** ā. A geminate lām with a short a and a
        # following hāʾ is an ordinary verb, and requiring only "an a" made
        # every one of them heavy.
        return False
    if _quality(slot) is not Quality.A:
        return False
    following = near.after(slot.id)
    if following is None or following.letter is not L.HEH:
        return False
    if not _doubled(near, slot):
        return False
    before = _before(near, slot)
    if before is None or before.letter not in (L.LAM, L.HAMZA):
        # The name is `ٱللَّه` or `لِلَّه`: the lām is always preceded by the
        # article's lām or by the waṣl hamza. `فَدَلَّىٰهُمَا` satisfies every
        # other clause -- geminate lām, long ā, following hāʾ, fatha before --
        # and is the verb *dallā*. Measured: one word made heavy by the whole
        # rule's absence of this test.
        #
        # It is the same condition `canon/derive/lexeme.py::allah_long_a` uses
        # to decide the lexeme at build time, restated here because `rules/`
        # may not import `canon/`. Two statements of one fact is the price of
        # that boundary; the alternative is a rule coupled to a canon module.
        return False
    return _preceding_quality(near, slot, plan) in (Quality.A, Quality.U)


def _doubled(near: Neighbourhood, slot) -> bool:
    if slot.onset is Onset.GEMINATE:
        return True
    before = _before(near, slot)
    return (
        before is not None
        and before.letter is L.LAM
        and before.nucleus.kind is NucleusKind.SILENT
    )


def _preceding_quality(near: Neighbourhood, slot, plan):
    """The vowel actually *heard* before this slot.

    Skips a canonically silent slot, and skips one a `BOUNDARY` rule elided:
    the waṣl hamza has a canonical helping vowel that is not spoken mid-word,
    and reading it makes the rāʾ light where the preceding fatha governs.
    """
    governing = _governing(near, slot, plan)
    return None if governing is None else _quality(governing)


def _governing(near: Neighbourhood, slot, plan):
    """The slot carrying the vowel actually *heard* before this one.

    Skips a canonically silent slot, and skips one a `BOUNDARY` rule elided:
    the waṣl hamza has a canonical helping vowel that is not spoken mid-word,
    and reading it makes the rāʾ light where the preceding fatha governs.
    """
    before = _before(near, slot)
    for _ in range(3):
        if before is None:
            return None
        silent = before.nucleus.kind is NucleusKind.SILENT
        if not (silent or _silenced(plan, before)):
            return before
        before = _before(near, before)
    return None


def _before(near: Neighbourhood, slot):
    flat = near.score.slots()
    for index, other in enumerate(flat):
        if other.id == slot.id:
            return flat[index - 1] if index else None
    return None


def _quality(slot):
    return getattr(slot.nucleus, "quality", None)
