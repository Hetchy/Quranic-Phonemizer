"""Length at the edges: the glide that becomes the vowel before it.

`هُوَ` at a stop: the fatha drops and the waw merges into the damma before
it, so the word ends long. A final yaa after a kasra does the same.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Length,
    MergeInto,
    Phase,
    Plan,
    Realize,
    Relength,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import Annotation
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Quality, Rule, SlotOrigin, VowelForm
from ..model.performance import Aspect, Occurrence, Vowel

#: Which glide lengthens which vowel.
GLIDE_OF = {Quality.U: L.WAW, Quality.I: L.YA}


@dataclass(frozen=True, slots=True)
class PausalGlide:
    rule: Rule = Rule.MADD_TABII
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        if plan.merged_away(at, Aspect.CONSONANT):
            # A glide the stop removed outright lengthens nothing.
            return None
        if slot.onset is Onset.GEMINATE:
            # A doubled glide is a consonant -- `ٱلْعَلِىُّ` ends `-iyy`, not `-ii`.
            return None
        if slot.nucleus.sounds_long:
            # A glide the stop cannot strip still carries its own vowel, so it
            # is a consonant: `نَسِيَا` ends `-iyaa`, not `-iiaa`.
            return None
        before = near.before(at)
        if before is None or not before.nucleus.is_short:
            return None
        if GLIDE_OF.get(before.nucleus.quality) is not slot.letter:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_TABII, at),
                Rule.MADD_TABII,
                (at,),
            ),
            (
                # Realizes the merged sound itself, so both halves share one occurrence.
                Realize(
                    before.id,
                    Aspect.VOWEL,
                    Vowel(before.nucleus.quality, long=True),
                ),
                MergeInto(at, Aspect.CONSONANT, before.id, Aspect.VOWEL),
            ),
        )


@dataclass(frozen=True, slots=True)
class IltiqaShortening:
    """Two sakins meet, so the madd letter shortens.

    Emits `Relength`, not a realization: the vowel is still plainly
    produced, only its length changes, so this rule owns no sound.
    """

    rule: Rule = Rule.ILTIQA_SHORTENING
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not (slot.nucleus.is_long or slot.nucleus.is_silah):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        following = near.after(at)
        if following is None:
            # `after` already refuses to look across a stop, so at a pause
            # there is no second sakin to meet and the madd stands.
            return None
        if following.onset is Onset.WASL:
            # A joined wasl hamza vanishes, so the sakin the madd meets is
            # the consonant behind it -- read from the Score, since
            # `Onset.WASL` means exactly "absent when joined to".
            following = near.after(following.id)
            if following is None:
                return None
        if not _opens_on_a_sakin(following):
            return None
        return Verdict(
            Occurrence(
                mint(Rule.ILTIQA_SHORTENING, at),
                Rule.ILTIQA_SHORTENING,
                (at,),
                (following.id,),
            ),
            (Relength(at, Length.SHORT),),
        )


def _opens_on_a_sakin(slot) -> bool:
    """A geminate consonant is a sakin plus a voweled one, so `ٱلَّذِى` meets a
    preceding madd with a sakin exactly as a written sukun would."""
    return slot.nucleus.is_silent or slot.onset is Onset.GEMINATE


def _still_a_sakin(plan: Plan, slot) -> bool:
    """A repair that vowels a sakin leaves nothing to stop the madd -- joined
    to `ٱللَّهُ` the meem of `الٓمٓ` takes a fatha. A geminate's sakin is its
    first half, so a vowel on the letter's own nucleus leaves it standing."""
    return slot.onset is Onset.GEMINATE or not plan.voweled(slot.id)


def _madd_of(
    near: Neighbourhood, plan: Plan, at: SlotId, boundaries: BoundaryPlan
) -> tuple[Rule, SlotId | None] | None:
    """Which madd this long vowel is, and the letter that decided it.

    `MADD_TABII` holds wherever none of the other five applies: an
    ordinary canonically long vowel, and the seven alifs at a stop.
    """
    slot, word = near.slot(at), near.word_of(at)
    if slot is None or word is None or not slot.nucleus.sounds_long:
        return None
    slots = near.score.words[word].slots
    final = bool(slots) and slots[-1].id == at

    if final and boundaries.stopped_on(word):
        # Nothing follows inside the word and the stop ends it; a silah's stopped form is absent rather than long, and takes no instance.
        return None if slot.nucleus.is_silah else (Rule.MADD_TABII, None)

    following = near.after(at)
    if following is None:
        return None

    if following.onset is Onset.WASL:
        # A joined wasl hamza is not there to lengthen for: the two sakins
        # that meet behind it are `IltiqaShortening`'s, and it shortens.
        return None

    if slot.nucleus.is_pausal_long:
        # Joined, a pausal alif's own vowel is canonically short, so there
        # is no length here to classify -- `وَأَنَا۠ أَوَّلُ` separates
        # nothing. `PausalAlif` owns the stopped reading.
        return None
    return _in_context(near, plan, slot, following, final, boundaries)


def _in_context(
    near: Neighbourhood, plan: Plan, slot, following, final: bool,
    boundaries: BoundaryPlan,
) -> tuple[Rule, SlotId | None]:
    """The outcome the letter after a long vowel decides."""
    if following.letter is L.HAMZA:
        # Muttasil in the same word, munfasil across a boundary -- and a particle the rasm joined is a boundary the writing does not show.
        rule = (
            Rule.MADD_JAIZ_MUNFASIL
            if final or Annotation.JOINED_PARTICLE in slot.annotations
            else Rule.MADD_WAJIB_MUTTASIL
        )
        return (rule, following.id)

    if _opens_on_a_sakin(following) and _still_a_sakin(plan, following):
        # A sakin already in the Score is permanent -- a written sukun in `الٓمٓ`, the first half of the shadda in `ٱلضَّآلِّينَ`. Lazim.
        return (Rule.MADD_LAZIM, following.id)

    if _stop_makes_quiescent(near, following, boundaries, plan):
        # Voweled in the Score, sakin only because the stop lands here -- aridah lissukun, same shape as lazim.
        return (Rule.MADD_ARID_LISSUKUN, following.id)
    # None of the five special outcomes: an ordinary long vowel.
    return (Rule.MADD_TABII, following.id)


@dataclass(frozen=True, slots=True)
class MaddClass:
    """Which madd this long vowel is -- six outcomes, one classifier.

    A plain length on a hamza is `MaddBadal`'s instead; the five
    contextual outcomes are named here whatever letter carries them.
    """

    rule: Rule = Rule.MADD_LAZIM
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        found = _madd_of(near, plan, at, boundaries)
        if found is None:
            return None
        rule, other = found
        if rule is not Rule.MADD_TABII:
            return _classify(rule, at, other)
        slot = near.slot(at)
        if slot.letter is L.HAMZA:
            return None
        return _tabii(slot, at, other)


@dataclass(frozen=True, slots=True)
class MaddBadal:
    """A long vowel on a hamza, standing in for a second hamza the reading
    does not say twice. It names the length rather than producing it, so a
    contextual madd may name the same vowel beside it."""

    rule: Rule = Rule.MADD_BADAL
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if slot is None or slot.letter is not L.HAMZA:
            return None
        if _madd_of(near, plan, at, boundaries) is None:
            return None
        return Verdict(
            Occurrence(mint(Rule.MADD_BADAL, at), Rule.MADD_BADAL, (at,)), ()
        )


@dataclass(frozen=True, slots=True)
class MaddSilah:
    """The pronoun haa drawn out because the word is joined to.

    The madd beside it says how long it is held: the plain two counts, or
    the longer count a hamza opening the next word calls for.
    """

    rule: Rule = Rule.MADD_SILAH
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if slot is None or not slot.nucleus.is_silah:
            return None
        if _madd_of(near, plan, at, boundaries) is None:
            return None
        return Verdict(
            Occurrence(mint(Rule.MADD_SILAH, at), Rule.MADD_SILAH, (at,)), ()
        )


@dataclass(frozen=True, slots=True)
class MaddLeen:
    """A waw or yaa sakin after a fatha, before a letter the stop makes sakin.

    Not a long vowel -- `خَوْف`, `بَيْت` -- so `MaddClass` does not trigger on
    it; the diphthong lengthens only at a pause.
    """

    rule: Rule = Rule.MADD_LEEN
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not slot.nucleus.is_silent:
            return None
        if slot.onset is Onset.GEMINATE:
            return None
        before = near.before(at)
        if before is None or not before.nucleus.is_short:
            return None
        if before.nucleus.quality is not Quality.A:
            return None
        following = near.after(at)
        if following is None:
            return None
        if following.nucleus.is_silent:
            # `عٓ` spells out as a leen before a sakin the Score holds for
            # good, so the length is obligatory rather than the stop's.
            return _classify(Rule.MADD_LAZIM, at, following.id)
        if not _stop_makes_quiescent(near, following, boundaries, plan):
            # Only the letter the stop actually silences counts.
            return None
        return _classify(Rule.MADD_LEEN, at, following.id)


def _stop_makes_quiescent(
    near: Neighbourhood, slot, boundaries, plan: Plan
) -> bool:
    """Is this the letter the stop silences? Last in its word but for a
    tanween noon -- `عَظِيمٌ` stops on the meem -- and holding a short vowel
    the stop takes rather than lengthens."""
    word = near.word_of(slot.id)
    if word is None or not boundaries.stopped_on(word):
        return False
    if not slot.nucleus.is_short:
        return False
    slots = near.score.words[word].slots
    # The written last letter need not be the one stopped on: the boundary
    # phase silences the pronoun yaa of `ءَاتَىٰنِ` and hands the stop back.
    letters = [
        s for s in slots
        if s.origin is not SlotOrigin.NUNATION
        and not plan.merged_away(s.id, Aspect.CONSONANT)
    ]
    if not letters or letters[-1].id != slot.id:
        return False
    if slots[-1].origin is SlotOrigin.NUNATION:
        # A tanween fath lengthens into the iwad alif rather than dropping, so `مِهَـٰدًا` silences nothing behind it. Damm and kasr simply go.
        return slot.nucleus.quality is not Quality.A
    return True


def _classify(rule: Rule, at: SlotId, other: SlotId | None) -> Verdict:
    return Verdict(Occurrence(mint(rule, at), rule, (at,), _context(other)), ())


def _context(other: SlotId | None) -> tuple[SlotId, ...]:
    """The letter whose own shape decided which madd this is, untouched."""
    return () if other is None else (other,)


def _tabii(slot, at: SlotId, other: SlotId | None) -> Verdict:
    """`MADD_TABII` cannot be classification-only, so it realizes the sound
    the plain fill would have given it -- except a pausal alif, whose own
    rule realizes it already, and only takes a length here."""
    occurrence = Occurrence(
        mint(Rule.MADD_TABII, at), Rule.MADD_TABII, (at,), _context(other)
    )
    if slot.nucleus.is_pausal_long:
        return Verdict(occurrence, (Relength(at, Length.LONG),))
    return Verdict(
        occurrence,
        (Realize(at, Aspect.VOWEL, Vowel(slot.nucleus.quality, long=True)),),
    )
