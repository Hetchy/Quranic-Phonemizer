"""Madd classification and pausal lengthening."""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Classify,
    Length,
    Phase,
    Plan,
    Realize,
    Relength,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, Junction, KhilafId, Location, SlotId
from ..model.canon import Annotation, Onset, Quality, Rule, SlotOrigin, VowelForm
from ..model.canon import CanonLetter as L
from ..model.performance import Aspect, Occurrence, Vowel


def _badal_slot(slot) -> bool:
    return (
        slot.letter is L.HAMZA
        or Annotation.BADAL in slot.annotations
        or (Annotation.NAQL in slot.annotations and slot.nucleus.sounds_long)
    )
@dataclass(frozen=True, slots=True)
class MaddLazimIbdal:
    """Name the hamza replaced by the long alif at madd-tasheel sites."""

    locations: frozenset[Location]
    default: str
    khilaf: KhilafId = KhilafId.ISTIFHAM_ARTICLE
    rule: Rule = Rule.IBDAL_HAMZA
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})
    emits: frozenset = frozenset({Rule.IBDAL_HAMZA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        word = near.word_of(at)
        if word is None or not near.first_of_word(at):
            return None
        if near.score.words[word].location not in self.locations:
            return None
        chosen = near.score.selection.chosen(self.khilaf) or self.default
        if chosen != "ibdal":
            return None
        return _classify(Rule.IBDAL_HAMZA, at, None)


@dataclass(frozen=True, slots=True)
class IltiqaShortening:
    """Two sakins meet, so the madd letter shortens.

    Emits `Relength`, not a realization: the vowel is still plainly
    produced, only its length changes, so this rule owns no sound.
    """

    rule: Rule = Rule.ILTIQA_SHORTENING
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG})
    emits: frozenset = frozenset({Rule.ILTIQA_SHORTENING})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del boundaries
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if not (slot.nucleus.is_long or slot.nucleus.is_joined_only_long):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        following = near.after(at)
        if following is None:
            # `after` already refuses to look across a stop, so at a pause
            # there is no second sakin to meet and the madd stands.
            return None
        behind_wasl = False
        if following.onset is Onset.WASL:
            # A joined wasl hamza vanishes, so the sakin the madd meets is
            # the consonant behind it -- read from the Score, since
            # `Onset.WASL` means exactly "absent when joined to".
            following = near.after(following.id)
            if following is None:
                return None
            behind_wasl = True
        if plan.removed_by(
            following.id, Aspect.CONSONANT, Rule.IBDAL_HAMZA
        ):
            return None
        if not (
            _opens_on_a_sakin(following)
            or behind_wasl and Annotation.NAQL in following.annotations
        ):
            return None
        inclined = slot.nucleus.quality in {Quality.TAQLIL, Quality.KUBRA}
        effect = (Realize(at, Aspect.VOWEL, Vowel(Quality.A))
                  if inclined else Relength(at, Length.SHORT))
        return Verdict(
            Occurrence(
                mint(Rule.ILTIQA_SHORTENING, at),
                Rule.ILTIQA_SHORTENING,
                (at,),
                (following.id,),
            ),
            (effect,),
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
    if plan.merged_away(at, Aspect.VOWEL):
        return None  # a vowel a boundary rule deleted has no length left
    slots = near.score.words[word].slots
    final = bool(slots) and slots[-1].id == at

    if final and boundaries.stopped_on(word):
        # A stopped silah is absent rather than long and takes no instance.
        return None if slot.nucleus.is_joined_only_long else (Rule.MADD_TABII, None)
    if final and boundaries.after(word) is Junction.SAKT:
        return (Rule.MADD_TABII, None)
    if final and all(item.spelled for item in slots):
        # A named-letter opening is insulated from the next word, while a
        # final long vowel in its name still carries its natural madd.
        return (Rule.MADD_TABII, None)

    following = near.after(at)
    while following is not None and (
        plan.removed_by(following.id, Aspect.CONSONANT, Rule.IBDAL_HAMZA)
        or plan.removed_by(following.id, Aspect.CONSONANT, Rule.TASHIL)
    ):
        # A consonant a hamza face silenced is a carrier, not a stop.
        following = near.after(following.id)
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
        # Muttasil within a word, munfasil across a semantic boundary.
        rule = (
            Rule.MADD_MUNFASIL
            if final or Annotation.JOINED_PARTICLE in slot.annotations
            else Rule.MADD_MUTTASIL
        )
        return (rule, following.id)

    if _opens_on_a_sakin(following) and _still_a_sakin(plan, following):
        # A Score sakin is permanent: a sukun or first half of a shadda.
        return (Rule.MADD_LAZIM, following.id)

    if _stop_makes_quiescent(near, following, boundaries, plan):
        # Voweled in the Score, sakin only because the stop lands here.
        return (Rule.MADD_ARID_LISSUKUN, following.id)
    # None of the five special outcomes: an ordinary long vowel.
    return (Rule.MADD_TABII, following.id)


@dataclass(frozen=True, slots=True)
class MaddClass:
    """Name plain or contextual length independently of `MaddBadal`."""

    rule: Rule = Rule.MADD_LAZIM
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG, Onset.WASL})
    additive_arid: bool = False
    badal_is_effective: bool = False
    emits: frozenset = frozenset({
        Rule.MADD_TABII, Rule.MADD_MUTTASIL, Rule.MADD_MUNFASIL,
        Rule.MADD_LAZIM, Rule.MADD_ARID_LISSUKUN,
    })

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if not self.additive_arid and slot is not None and plan.relengthened_long(at):
            if Annotation.BADAL in slot.annotations:
                return None
            if self.badal_is_effective and _is_started_badal(
                near, plan, slot, boundaries
            ):
                return None
            return _tabii(slot, at, None, _stopped_on(near, boundaries, at))
        found = _madd_of(near, plan, at, boundaries)
        if self.additive_arid:
            if found is None or found[0] is not Rule.MADD_MUTTASIL:
                return None
            following = near.slot(found[1])
            if following is None or not _stop_makes_quiescent(
                near, following, boundaries, plan
            ):
                return None
            return _classify(Rule.MADD_ARID_LISSUKUN, at, following.id)
        if found is None:
            return None
        rule, other = found
        if (
            self.badal_is_effective
            and rule is Rule.MADD_TABII
            and slot is not None
            and (
                _badal_slot(slot)
                or _is_started_badal(near, plan, slot, boundaries)
            )
        ):
            return None
        if rule is not Rule.MADD_TABII:
            return _classify(rule, at, other)
        return _tabii(slot, at, other, _stopped_on(near, boundaries, at))

@dataclass(frozen=True, slots=True)
class MaddBadal:
    """A long vowel on a hamza standing in for a second hamza. It names the
    length, so a contextual madd may name the same vowel beside it."""

    rule: Rule = Rule.MADD_BADAL
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({VowelForm.LONG, Onset.WASL, Annotation.BADAL})
    emits: frozenset = frozenset({Rule.MADD_BADAL})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if slot is None or (
            not _badal_slot(slot)
        ):
            return None
        # the ibdal case: the plan carries a length the Score does not
        if _madd_of(near, plan, at, boundaries) is None and not plan.relengthened_long(at):
            return None
        return Verdict(
            Occurrence(mint(Rule.MADD_BADAL, at), Rule.MADD_BADAL, (at,)), ()
        )


def _is_started_badal(near, plan: Plan, slot, boundaries: BoundaryPlan) -> bool:
    word = near.word_of(slot.id)
    if (
        word is None
        or slot.onset is not Onset.WASL
        or not boundaries.started_on(word)
        or not near.first_of_word(slot.id)
        or not plan.relengthened_long(slot.id)
    ):
        return False
    root = near.after(slot.id)
    return bool(
        root is not None
        and root.letter is L.HAMZA
        and root.nucleus.is_silent
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
    emits: frozenset = frozenset({Rule.MADD_SILAH})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        if (
            slot is None
            or slot.letter is not L.HEH
            or not slot.nucleus.is_joined_only_long
        ):
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
    mahmuz_is_distinct: bool = False
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})
    emits: frozenset = frozenset({Rule.MADD_LEEN, Rule.MADD_LAZIM})

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
        if self.mahmuz_is_distinct and following.letter is L.HAMZA:
            return None
        if following.nucleus.is_silent:
            # `عٓ` has a permanent sakin, so its length is obligatory.
            return _classify(Rule.MADD_LAZIM, at, following.id, Aspect.CONSONANT)
        if not _stop_makes_quiescent(near, following, boundaries, plan):
            # Only the letter the stop actually silences counts.
            return None
        return _classify(Rule.MADD_LEEN, at, following.id)


def _stop_makes_quiescent(
    near: Neighbourhood, slot, boundaries, plan: Plan
) -> bool:
    """Is this the letter the stop silences? Last in its word but for a
    tanween noon -- `عَظِيمٌ` stops on the meem -- and left bare by the
    boundary phase rather than lengthened into an iwad."""
    word = near.word_of(slot.id)
    if word is None or not boundaries.stopped_on(word):
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
    # BOUNDARY runs before LENGTH, so the drop it made or withheld is the
    # answer: a fathatan lengthens into the iwad alif instead of dropping.
    return plan.merged_away(slot.id, Aspect.VOWEL)


def _stopped_on(near: Neighbourhood, boundaries, at: SlotId) -> bool:
    word = near.word_of(at)
    return word is not None and boundaries.stopped_on(word)


def _classify(rule: Rule, at: SlotId, other: SlotId | None,
              aspect: Aspect | None = None) -> Verdict:
    effects = () if aspect is None else (Classify(at, aspect),)
    return Verdict(Occurrence(mint(rule, at), rule, (at,), _context(other)), effects)


def _context(other: SlotId | None) -> tuple[SlotId, ...]:
    """The letter whose own shape decided which madd this is, untouched."""
    return () if other is None else (other,)


def _tabii(slot, at: SlotId, other: SlotId | None, stopped: bool) -> Verdict:
    """Realize plain madd, or only lengthen an already realized pausal alif."""
    occurrence = Occurrence(
        mint(Rule.MADD_TABII, at), Rule.MADD_TABII, (at,), _context(other)
    )
    if slot.nucleus.is_pausal_long:
        return Verdict(occurrence, (Relength(at, Length.LONG),))
    state = slot.nucleus.stopped if stopped else slot.nucleus.joined
    return Verdict(
        occurrence,
        (Realize(at, Aspect.VOWEL, Vowel(state.quality, long=True)),),
    )
