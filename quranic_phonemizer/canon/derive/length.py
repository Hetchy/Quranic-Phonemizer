"""Length: which clusters are carriers, and where a dagger's alif lands.

A carrier contributes length to the slot before it rather than sounding
at its own position, decided by the preceding nucleus, not the glyph.
"""
from __future__ import annotations

from ...model.canon import (
    CARRIER_OF,
    CARRIERS,
    CanonLetter,
    Nucleus,
    Quality,
)
from ...model.inscription import SlotFact
from .vocabulary import Absent, Context, Outcome, Sets, Shows, Target, register
from .silah import carries_silah

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


@register("length_a", requires=(
    "fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan",
        "shadda", "silah_waw", "silah_ya",
))
def dagger(context: Context) -> Outcome:
    """The superscript alif.

    Lengthens the previous slot's quality when it sits on bare rasm;
    otherwise it is its own slot's whole vowel, so it is a quality fact."""
    cluster = context.cluster
    previous = context.previous_nucleus
    if not (cluster.dagger_host and not cluster.has(*VOWEL_ROLES)):
        return Sets(SlotFact.VOWEL_QUALITY, Nucleus.long(Quality.A))
    if previous is None:
        return Sets(SlotFact.VOWEL_QUALITY, Nucleus.long(Quality.A))
    if previous.is_short and previous.quality is Quality.A:
        return Sets(SlotFact.VOWEL_LENGTH, Nucleus.long(Quality.A), Target.PREVIOUS)
    if previous.sounds_long:
        # The rasm carrier of a length already written: `مَجْر۪ىٰهَا` puts the
        # imala on the raa and draws the yaa that carries it.
        return Absent()
    return Sets(SlotFact.VOWEL_QUALITY, Nucleus.long(Quality.A))


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

    if previous.is_short:
        if letter is CARRIER_OF[previous.quality]:
            # The pronoun haa's vowel is absent when the word is stopped on,
            # so the carrier the rasm omits there spells a conditional length.
            length = Nucleus.joined_only_long if carries_silah(context) else Nucleus.long
            return Sets(SlotFact.VOWEL_LENGTH, length(previous.quality), Target.PREVIOUS)
        if (
            cluster.bare_rasm
            and context.word_final
            and previous.quality is Quality.A
            and not cluster.has("sukun")
        ):
            # IndoPak writes the alif maqsura as a plain yaa; Uthmani writes
            # `ى`. Both stand for an alif nobody wrote - unless a sukun says
            # the yaa is the consonant of a diphthong, as in `ٱثْنَىْ`.
            return Sets(SlotFact.VOWEL_LENGTH, Nucleus.long(Quality.A), Target.PREVIOUS)
    if previous.sounds_long:
        return Absent()
    if previous.is_silent and letter is not CanonLetter.ALIF:
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
    return Sets(SlotFact.VOWEL_LENGTH, Nucleus.pausal_long(Quality.A), Target.PREVIOUS)


@register("shows_long")
def shows_long(context: Context) -> Outcome:
    """The maddah: supplies nothing the rules do not already have, but is
    still the grapheme a reader points at to see a madd."""
    return Shows(Target.HERE)
