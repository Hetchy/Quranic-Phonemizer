"""Tanwīn is two slots (A1, ADR-001 §3.5b).

One grapheme evidences facts on two: a `Short(q)` nucleus on the base slot, and
`LETTER = NOON` + `NUCLEUS = Silent` on a new following slot. The nūn sounds as
a plain *n* at its own position wherever iẓhār applies — `عَذَابٌ` →
`ʕ a ð aː b u n` — so by the unit-hood criterion it always was a slot.

What that buys: the nūn family gets **one shape**, since tanwīn and nūn sākinah
become literally the same rule on the same trigger; the iltiqāʾ kasra stops
being a slot-less insertion; and IndoPak's `ࣙ` becomes ordinary evidence.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Onset, Quality, Short, Silent
from ...model.inscription import SlotFact
from . import Absent, AddsSlot, Context, Outcome, Sets, Target, register

_QUALITY = {"fathatan": Quality.A, "dammatan": Quality.U, "kasratan": Quality.I}


def _nunate(quality: Quality) -> AddsSlot:
    return AddsSlot(
        fact=SlotFact.NUCLEUS,
        value=Short(quality),
        letter=CanonLetter.NOON,
        onset=Onset.PLAIN,
        nucleus=Silent(),
    )


@register("tanween")
def tanween(context: Context) -> Outcome:
    for role, quality in _QUALITY.items():
        if context.cluster.has(role):
            return _nunate(quality)
    raise ValueError(
        f"cluster {context.index} was routed to the tanwīn derivation but "
        f"carries no tanwīn mark: {[m.role for m in context.cluster.marks]}"
    )


@register("iwad_carrier")
def iwad_carrier(context: Context) -> Outcome:
    """The ālif written after a fathatan.

    It is not a fourth slot and not a length carrier in waṣl; at waqf it is the
    ʿiwaḍ, which is a `Relength` on the base plus a `Silence` on the nūn slot.
    `role` reports it as **madd** — what it contributes — while
    `Grapheme.cls` keeps `TANWEEN`, which is what it is (ADR-007 §6.1).
    """
    return Absent(shows=Target.PREVIOUS)


@register("cross_word_noon")
def cross_word_noon(context: Context) -> Outcome:
    """IndoPak's `ࣙ` U+08D9 — a nūn with a kasra drawn on the *following* word.

    IndoPak splits the tanwīn across the boundary: the vowel stays on word *n*
    with the tanwīn mark dropped, and the nūn is depicted on word *n+1*. Under
    A1 that is not an attestation at all but ordinary evidence, because the
    tanwīn nūn is a slot. IndoPak was writing the correct model all along.

    Measured: 54 sites, of which 34 are inside a verse and **20 cross a verse
    boundary** — which is why `read` is verse-scoped *and* why `canon.build`
    takes one word of right context.
    """
    return Sets(SlotFact.LETTER, CanonLetter.NOON)
