"""The phase driver: run the rules, then turn the Plan into a Performance.

Phases are closed and ordered; within a phase, rules are unordered and any
conflict between them raises rather than resolving silently.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import BoundaryPlan, SlotId, SoundId, VariantSelection
from ..model.canon import (
    CLASSIFICATION_ONLY,
    Onset,
    Rule,
    Score,
    Slot,
    VowelForm,
)
from ..model.performance import (
    Aspect,
    Attribution,
    Classifies,
    Consonant,
    Hosts,
    Inserted,
    MergedInto,
    Modifier,
    Occurrence,
    Performance,
    Recolours,
    Release,
    SetsLength,
    Silent,
    Sound,
    Vowel,
)
from .classifier import RuleSet
from .neighbourhood import Neighbourhood
from .plan import (
    Classify,
    Insert,
    Length,
    MergeInto,
    Phase,
    Plan,
    Realize,
    Recolour,
    Relength,
    Silence,
    SoundFeature,
)

#: Which aspect a rule's `Classifies` edge names.
#: `ishmam` names a consonant: either the merged noon whose rounding is shown
#: without sound, or the first consonant whose vowel begins with partial damma.
_CLASSIFIES_ASPECT: dict[Rule, Aspect] = {
    Rule.TARQEEQ: Aspect.CONSONANT,
    Rule.ISHMAM: Aspect.CONSONANT,
    Rule.GHUNNAH_MUSHADDADAH: Aspect.CONSONANT,
    Rule.TASHIL: Aspect.CONSONANT,
    Rule.HAMZA_WASL_FATHA: Aspect.CONSONANT,
    Rule.HAMZA_WASL_KASRA: Aspect.CONSONANT,
    Rule.HAMZA_WASL_DAMMA: Aspect.CONSONANT,
    Rule.IDGHAM_MUTAJANISAYN_NAQIS: Aspect.CONSONANT,
    Rule.IZHAR: Aspect.CONSONANT,
    Rule.IZHAR_SHAFAWI: Aspect.CONSONANT,
    Rule.LAM_QAMARIYYAH: Aspect.CONSONANT,
    Rule.TAQLIL: Aspect.VOWEL,
    Rule.IMALA: Aspect.VOWEL,
    Rule.MADD_BADAL: Aspect.VOWEL,
    Rule.MADD_SILAH: Aspect.VOWEL,
    Rule.MADD_MIM_AL_JAM: Aspect.VOWEL,
    Rule.MADD_YAA_ZAWAID: Aspect.VOWEL,
    Rule.MADD_MUTTASIL: Aspect.VOWEL,
    Rule.MADD_MUNFASIL: Aspect.VOWEL,
    Rule.MADD_LAZIM: Aspect.VOWEL,
    Rule.MADD_ARID_LISSUKUN: Aspect.VOWEL,
    Rule.MADD_TABII: Aspect.VOWEL,
    Rule.IBDAL_HAMZA: Aspect.VOWEL,
    Rule.NAQL: Aspect.VOWEL,
    #: The waw or yaa this rule names has no vowel; it classifies the consonant.
    Rule.MADD_LEEN: Aspect.CONSONANT,
}

class MaterialisationError(AssertionError):
    """A Plan that cannot become a Performance. Names both addresses."""


PHASE_ORDER = (
    Phase.BOUNDARY,
    Phase.MERGE,
    Phase.LENGTH,
    Phase.COLOUR,
    Phase.RELEASE,
)


@dataclass(slots=True)
class _Mint:
    """Request-local identity. A `SoundId` is meaningless outside the
    `Performance` that carries the selection and plan which produced it."""

    verse: object
    sounds: int = 0

    def sound(self) -> SoundId:
        self.sounds += 1
        return SoundId(self.verse, self.sounds)


def perform(
    score: Score,
    rules: RuleSet,
    boundaries: BoundaryPlan,
    *,
    selection: VariantSelection = VariantSelection(),
) -> Performance:
    plan = Plan()
    slots = score.slots()

    near = Neighbourhood(score, boundaries)
    for phase in PHASE_ORDER:
        classifiers = rules.for_phase(phase)
        if not classifiers:
            continue
        for slot in slots:
            for classifier in classifiers:
                if not _triggered(classifier, slot):
                    continue
                verdict = classifier.look(near, plan, slot.id, boundaries)
                if verdict is not None:
                    plan.record(phase, verdict)

    return _materialise(plan, score, boundaries, selection)


def _fill_plain(plan: Plan, score: Score) -> list[tuple]:
    """Every (slot, aspect) no verdict claimed, filled from the Score itself."""
    # Only effects that produce or remove a sound claim the slot; Recolour
    # and Relength modify an existing one and must not count as claiming it.
    # A release is an addition beside the consonant, not a replacement of
    # it, so it must not count as claiming the slot either.
    claimed = {
        (effect.slot, effect.aspect)
        for effect in plan.effects()
        if isinstance(effect, (MergeInto, Silence))
        or (isinstance(effect, Realize) and not isinstance(effect.sound, Release))
    }
    filled = []
    for slot in score.slots():
        for aspect in Aspect:
            if not has_content(slot, aspect) or (slot.id, aspect) in claimed:
                continue
            filled.append((slot, aspect))
    return filled


def _triggered(classifier, slot: Slot) -> bool:
    """Whether a slot matches a classifier's declared trigger set.

    Checks letter, nucleus kind, onset, and quality; no triggers declared
    means the classifier always fires.
    """
    triggers = classifier.triggers
    if not triggers:
        return True
    nucleus = slot.nucleus
    return (
        slot.letter in triggers
        or nucleus.joined.form in triggers
        or nucleus.stopped.form in triggers
        or slot.onset in triggers
        or nucleus.quality in triggers
        or bool(slot.annotations & triggers)
    )


def _materialise(
    plan: Plan,
    score: Score,
    boundaries: BoundaryPlan,
    selection: VariantSelection,
) -> Performance:
    mint = _Mint(score.words[0].location.verse if score.words else None)
    sounds: list[tuple[SoundId, Sound]] = []
    attributions: list[Attribution] = []
    occurrences: list[Occurrence] = []
    colours = _colours(plan)
    hosted: dict[tuple[SlotId, Aspect], SoundId] = {}

    for _, verdict in plan.entries:
        occurrences.append(verdict.occurrence)

    _realize(plan, mint, colours, sounds, attributions, hosted)
    _fill(
        plan, score, boundaries, mint, colours, sounds, attributions, hosted
    )
    _resolve_merges(plan, hosted, attributions)

    return Performance(
        riwayah=score.riwayah,
        sounds=tuple(sounds),
        attributions=tuple(attributions),
        modifiers=tuple(_modifiers(plan, hosted)),
        occurrences=tuple(occurrences),
        selection=selection,
        boundaries=boundaries,
    )


def _plain_sound(
    slot: Slot, aspect: Aspect, colours, state, lengths=None
) -> Sound:
    features = colours.get((slot.id, aspect), {})
    emphatic = bool(features.get(SoundFeature.EMPHATIC, False))
    if aspect is Aspect.CONSONANT:
        return Consonant(
            slot.letter,
            geminate=slot.onset is Onset.GEMINATE,
            emphatic=emphatic,
            eased=slot.onset is Onset.TASHIL,
        )
    long = state.form is VowelForm.LONG
    override = (lengths or {}).get(slot.id)
    if override is not None:
        long = override is Length.LONG
    return Vowel(state.quality, long=long, emphatic=emphatic)



def _realize(plan, mint, colours, sounds, attributions, hosted) -> None:
    """Sounds a rule names outright. Merges wait: a merge target is usually
    realized by the plain fill, so merging first would leave it half-hosted."""
    for _, verdict in plan.entries:
        for effect in verdict.effects:
            if isinstance(effect, Realize):
                sound_id = mint.sound()
                sound = _apply_colours(effect, colours)
                sounds.append((sound_id, sound))
                # A release shares its slot and aspect with the consonant it
                # echoes, so it must not be the one `hosted` remembers there:
                # the plain fill still owns that key for its own sound.
                if not isinstance(sound, Release):
                    hosted[(effect.slot, effect.aspect)] = sound_id
                attributions.append(
                    Hosts((effect.slot,), effect.aspect, sound_id,
                          verdict.occurrence.id)
                )
            elif isinstance(effect, Insert):
                sound_id = mint.sound()
                sounds.append((sound_id, effect.sound))
                attributions.append(
                    Inserted(effect.anchor, effect.aspect, sound_id,
                             verdict.occurrence.id)
                )


def _fill(
    plan, score, boundaries, mint, colours, sounds, attributions, hosted
) -> None:
    """Every aspect no rule spoke for, said as the Score writes it."""
    lengths = {
        e.slot: e.length for e in plan.effects() if isinstance(e, Relength)
    }
    words = {
        slot.id: word
        for word, score_word in enumerate(score.words)
        for slot in score_word.slots
    }
    for slot, aspect in _fill_plain(plan, score):
        state = (
            slot.nucleus.stopped
            if boundaries.stopped_on(words[slot.id])
            else slot.nucleus.joined
        )
        sound_id = mint.sound()
        sounds.append(
            (sound_id, _plain_sound(slot, aspect, colours, state, lengths))
        )
        hosted[(slot.id, aspect)] = sound_id
        attributions.append(Hosts((slot.id,), aspect, sound_id, None))


def _resolve_merges(plan, hosted, attributions) -> None:
    for _, verdict in plan.entries:
        for effect in verdict.effects:
            if isinstance(effect, MergeInto):
                host = hosted.get((effect.host, effect.host_aspect))
                if host is None:
                    raise MaterialisationError(
                        f"{effect.slot} merges into {effect.host} "
                        f"{effect.host_aspect.value}, which hosts no sound. "
                        f"A merger is a pair of edges; half of one is a bug."
                    )
                attributions.append(
                    MergedInto((effect.slot,), effect.aspect, host,
                               verdict.occurrence.id)
                )
            elif isinstance(effect, Silence):
                attributions.append(
                    Silent((effect.slot,), effect.aspect, verdict.occurrence.id)
                )


def _modifiers(plan: Plan, hosted) -> list[Modifier]:
    """The edge each applied `Recolour`/`Relength` leaves, plus one
    `Classifies` per classification-only occurrence naming a sound."""
    out: list[Modifier] = []
    for _, verdict in plan.entries:
        out.extend(_modifiers_for(verdict.occurrence, verdict.effects, hosted))
    return out


def _modifiers_for(occurrence: Occurrence, effects, hosted) -> list[Modifier]:
    out: list[Modifier] = []
    for effect in effects:
        if isinstance(effect, Recolour):
            sound_id = hosted.get((effect.slot, effect.aspect))
            if sound_id is not None:
                out.append(Recolours(sound_id, occurrence.id))
        elif isinstance(effect, Relength):
            sound_id = hosted.get((effect.slot, Aspect.VOWEL))
            if sound_id is not None:
                out.append(SetsLength(sound_id, occurrence.id, effect.length))
        elif isinstance(effect, Classify):
            sound_id = hosted.get((effect.slot, effect.aspect))
            if sound_id is not None:
                out.append(Classifies(sound_id, occurrence.id))
    aspect = _CLASSIFIES_ASPECT.get(occurrence.rule)
    if aspect is not None and _names_its_sound(occurrence, effects, aspect):
        for subject in occurrence.subjects:
            sound_id = hosted.get((subject, aspect))
            if sound_id is not None:
                out.append(Classifies(sound_id, occurrence.id))
    return out


def _names_its_sound(occurrence: Occurrence, effects, aspect: Aspect) -> bool:
    """A rule names a sound it leaves alone, or the single one it realizes."""
    if not effects:
        return occurrence.rule in CLASSIFICATION_ONLY
    if len(effects) != 1 or not isinstance(effects[0], Realize):
        return False
    return (
        effects[0].slot in occurrence.subjects
        and effects[0].aspect is aspect
    )


def _colours(plan: Plan) -> dict[tuple[SlotId, Aspect], dict[SoundFeature, bool]]:
    out: dict[tuple[SlotId, Aspect], dict[SoundFeature, bool]] = {}
    for effect in plan.effects():
        if isinstance(effect, Recolour):
            out.setdefault((effect.slot, effect.aspect), {})[effect.feature] = (
                effect.value
            )
    return out


def _apply_colours(effect: Realize, colours) -> Sound:
    """A rule names the sound; a later phase may still colour it."""
    sound = effect.sound
    emphatic = (colours.get((effect.slot, effect.aspect)) or {}).get(
        SoundFeature.EMPHATIC
    )
    if emphatic is None:
        return sound
    match sound:
        case Consonant():
            return Consonant(
                sound.letter, sound.geminate, emphatic, sound.ghunnah, sound.eased
            )
        case Vowel():
            return Vowel(sound.quality, sound.long, emphatic)
    return sound


def has_content(slot: Slot, aspect: Aspect) -> bool:
    """`CONSONANT` always has canonical content; `VOWEL` has it unless the
    nucleus is silent. A canonically absent nucleus needs no Silent edge."""
    if aspect is Aspect.CONSONANT:
        return True
    return not slot.nucleus.is_silent
