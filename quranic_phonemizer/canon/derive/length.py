"""Length: which clusters are carriers, and where a dagger's alif lands.

The length clause of the unit-hood criterion (ADR-001 §3.1): *contributing
length to a neighbouring slot's nucleus is not sound at its own position*. So a
carrier is not a slot, and the same glyph is decided by the preceding nucleus —
a sākin wāw after a fatha is a leen glide and sounds; after a damma it carries
length and does not.
"""
from __future__ import annotations

from ...model.canon import CanonLetter, Long, NucleusKind, PausalLong, Quality
from ...model.inscription import SlotFact
from . import Absent, Context, Outcome, Sets, Shows, Target, register

CARRIER_OF: dict[Quality, CanonLetter] = {
    Quality.A: CanonLetter.ALIF,
    Quality.U: CanonLetter.WAW,
    Quality.I: CanonLetter.YA,
}
CARRIERS = frozenset(CARRIER_OF.values())

#: Roles that give a cluster a vowel of its own, so it cannot be a carrier.
VOWEL_ROLES = frozenset(
    {
        "fatha",
        "damma",
        "kasra",
        "fathatan",
        "dammatan",
        "kasratan",
        "shadda",
        "silah_waw",
        "silah_ya",
    }
)
LONG_KINDS = frozenset(
    {NucleusKind.LONG, NucleusKind.PAUSAL_LONG, NucleusKind.SILAH}
)


@register("length_a")
def dagger(context: Context) -> Outcome:
    """The superscript alif.

    On a glyph the script declares as rasm — Uthmani's tatweel seat, its alif
    maqṣūra and its wāw — it lengthens the open short *a* of the previous slot.
    On any other host the dagger's own cluster is the slot and the alif is its
    nucleus. Measured: Uthmani writes alif+dagger **0** times and IndoPak
    **1,543**, where it is always madd badal, never a carrier.
    """
    cluster = context.cluster
    previous = context.previous_nucleus
    carries_for_previous = (
        cluster.dagger_host
        and not cluster.has(*VOWEL_ROLES)
        and previous is not None
        and previous.kind is NucleusKind.SHORT
        and previous.quality is Quality.A
    )
    if carries_for_previous:
        return Sets(SlotFact.NUCLEUS, Long(Quality.A), Target.PREVIOUS)
    return Sets(SlotFact.NUCLEUS, Long(Quality.A))


@register("carrier")
def carrier(context: Context) -> Outcome:
    """Is this bare ālif/wāw/yāʾ a slot, or does it lengthen the previous one?

    `canon.build` names this derivation itself, because the length clause is a
    property of the canonical layer rather than of any one script.
    """
    cluster = context.cluster
    letter = cluster.letter
    previous = context.previous_nucleus
    if letter is None or letter not in CARRIERS or previous is None:
        return Sets(SlotFact.LETTER, letter) if letter else Absent()
    if letter is CanonLetter.ALIF and cluster.has("sukun"):
        # A carrier bears no mark of its own. IndoPak writes `اْ` for a hamza
        # whose seat Uthmani precomposes.
        return Sets(SlotFact.LETTER, letter)

    if previous.kind is NucleusKind.SHORT:
        if letter is CARRIER_OF[previous.quality]:
            return Sets(SlotFact.NUCLEUS, Long(previous.quality), Target.PREVIOUS)
        if cluster.bare_rasm and context.word_final and previous.quality is Quality.A:
            # IndoPak writes the alif maqṣūra as a plain yāʾ; Uthmani writes
            # `ى`. Both stand for an alif nobody wrote.
            return Sets(SlotFact.NUCLEUS, Long(Quality.A), Target.PREVIOUS)
    if previous.kind in LONG_KINDS:
        return Absent()
    if previous.kind is NucleusKind.SILENT and letter is not CanonLetter.ALIF:
        return Absent()
    return Sets(SlotFact.LETTER, letter)


@register("pausal_length")
def pausal_length(context: Context) -> Outcome:
    """Uthmani's `۠`, on the ālif of the seven alifs.

    Like the dagger, the mark sits on a carrier and the length belongs to the
    slot before it. Uthmani writes it at 66 sites and IndoPak at none — which
    is why the canonical supplier is the lexeme list and this mark is the
    witness that agrees with it (L2).
    """
    del context
    return Sets(SlotFact.NUCLEUS, PausalLong(Quality.A), Target.PREVIOUS)


@register("shows_long")
def shows_long(context: Context) -> Outcome:
    """The maddah. It supplies nothing the rules do not already have, and it
    is still the grapheme a reader points at to see a madd — 5,044 cells in the
    frozen baseline give it a long vowel and a madd tag (ADR-003 §4.0)."""
    return Shows(Target.HERE)
