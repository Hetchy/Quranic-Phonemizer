"""Length: which clusters are carriers, and where a dagger's alif lands.

A carrier contributes length to the slot before it rather than sounding
at its own position, decided by the preceding nucleus, not the glyph.
"""
from __future__ import annotations

from ...model.canon import (
    CanonLetter,
    Long,
    NucleusKind,
    PausalLong,
    Quality,
    Silah,
)
from ...model.inscription import SlotFact
from . import Absent, Context, Outcome, Sets, Shows, Target, register
from .silah import carries_silah

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


@register("length_a", requires=(
    "fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan",
        "shadda", "silah_waw", "silah_ya",
))
def dagger(context: Context) -> Outcome:
    """The superscript alif.

    On a glyph the script declares as rasm, it lengthens the previous
    slot's open short a. On any other host, it is its own slot.
    """
    cluster = context.cluster
    previous = context.previous_nucleus
    if not (cluster.dagger_host and not cluster.has(*VOWEL_ROLES)):
        return Sets(SlotFact.NUCLEUS, Long(Quality.A))
    if previous is None:
        return Sets(SlotFact.NUCLEUS, Long(Quality.A))
    if previous.kind is NucleusKind.SHORT and previous.quality is Quality.A:
        return Sets(SlotFact.NUCLEUS, Long(Quality.A), Target.PREVIOUS)
    if previous.kind in LONG_KINDS:
        # The rasm carrier of a length already written: `مَجْر۪ىٰهَا` puts the
        # imala on the raa and draws the yaa that carries it.
        return Absent()
    return Sets(SlotFact.NUCLEUS, Long(Quality.A))


@register("carrier", requires=(
    "fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan",
        "shadda", "silah_waw", "silah_ya",
    "sukun",
))
def carrier(context: Context) -> Outcome:
    """Is this bare alif/waw/yaa a slot, or does it lengthen the previous one?

    `canon.build` names this derivation itself, because the length clause is a
    property of the canonical layer rather than of any one script.
    """
    cluster = context.cluster
    letter = cluster.letter
    previous = context.previous_nucleus
    if context.word_initial:
        # The slot before it belongs to another word, and no carrier reaches
        # across a boundary to lengthen one.
        return Sets(SlotFact.LETTER, letter) if letter else Absent()
    if letter is None or letter not in CARRIERS or previous is None:
        return Sets(SlotFact.LETTER, letter) if letter else Absent()
    if cluster.rasm_only and not context.word_final:
        # `بِاَيِّىكُمُ` draws with a maqsura the doubling its shadda already
        # spells. Word-finally the same glyph stands for an unwritten alif.
        return Absent()
    if letter is CanonLetter.ALIF and cluster.has("sukun"):
        # A carrier bears no mark of its own. IndoPak writes `اْ` for a hamza
        # whose seat Uthmani precomposes.
        return Sets(SlotFact.LETTER, letter)

    if previous.kind is NucleusKind.SHORT:
        if letter is CARRIER_OF[previous.quality]:
            # The pronoun haa's vowel is absent when the word is stopped on,
            # so the carrier the rasm omits there spells a conditional length.
            length = Silah if carries_silah(context) else Long
            return Sets(SlotFact.NUCLEUS, length(previous.quality), Target.PREVIOUS)
        if (
            cluster.bare_rasm
            and context.word_final
            and previous.quality is Quality.A
            and not cluster.has("sukun")
        ):
            # IndoPak writes the alif maqsura as a plain yaa; Uthmani writes
            # `ى`. Both stand for an alif nobody wrote - unless a sukun says
            # the yaa is the consonant of a diphthong, as in `ٱثْنَىْ`.
            return Sets(SlotFact.NUCLEUS, Long(Quality.A), Target.PREVIOUS)
    if previous.kind in LONG_KINDS:
        return Absent()
    if previous.kind is NucleusKind.SILENT and letter is not CanonLetter.ALIF:
        return Absent()
    return Sets(SlotFact.LETTER, letter)


@register("pausal_length", requires=(
    "fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan",
        "shadda", "silah_waw", "silah_ya",
))
def pausal_length(context: Context) -> Outcome:
    """Uthmani's `۠`, on the alif of the seven alifs.

    Like the dagger, the mark sits on a carrier and the length belongs to
    the slot before it; IndoPak writes no equivalent mark at all.
    """
    del context
    return Sets(SlotFact.NUCLEUS, PausalLong(Quality.A), Target.PREVIOUS)


@register("shows_long")
def shows_long(context: Context) -> Outcome:
    """The maddah: supplies nothing the rules do not already have, but is
    still the grapheme a reader points at to see a madd."""
    return Shows(Target.HERE)
