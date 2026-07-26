"""The phase driver: run the rules, then turn the Plan into a Performance.

Phases are closed and ordered; within a phase rules are unordered and conflicts
are errors. That turns domain-facts invariant 2 — exactly one rule of a family
fires per trigger — from a comment into something that fails loudly.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import (
    BoundaryPlan,
    OccurrenceId,
    Riwayah,
    SlotId,
    SoundId,
    VariantSelection,
)
from ..model.canon import NucleusKind, Onset, Phase, Rule, Score, Slot
from ..model.performance import (
    Aspect,
    Attribution,
    Consonant,
    Hosts,
    Inserted,
    MergedInto,
    Nasal,
    Occurrence,
    Participants,
    Performance,
    Silent,
    Sound,
    Vowel,
)
from .classifier import RuleSet
from .neighbourhood import Neighbourhood
from .plan import (
    Insert,
    Length,
    MergeInto,
    Plan,
    Realize,
    Recolour,
    Relength,
    Silence,
    SoundFeature,
    Verdict,
)

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
    occurrences: int = 0

    def sound(self) -> SoundId:
        self.sounds += 1
        return SoundId(self.verse, self.sounds)

    def occurrence(self) -> OccurrenceId:
        self.occurrences += 1
        return OccurrenceId(self.verse, self.occurrences)


def perform(
    score: Score,
    rules: RuleSet,
    boundaries: BoundaryPlan,
    *,
    riwayah: Riwayah = Riwayah.HAFS,
    selection: VariantSelection = VariantSelection(),
) -> Performance:
    plan = Plan()
    slots = score.slots()
    index = {slot.id: slot for slot in slots}

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

    return _materialise(plan, index, score, boundaries, riwayah, selection)


def _fill_plain(plan: Plan, score: Score, mint: _Mint) -> list[tuple]:
    """Plain realization, as a default rather than a classifier.

    `PLAIN` cannot be a rule in the phase list: it would collide with every
    merging family on the same conflict key, and resolving that would need an
    ordering *within* a phase, which ADR-004 §3 rules out. So the engine fills
    whatever no verdict claimed and tags it `Rule.PLAIN`.

    The invariant survives intact — no sound exists except as the output of a
    named occurrence — and E1 stays a genuine error rather than a precedence
    question. `PLAIN` occurrences are internable to one object per traversal,
    which is what makes this cheap (ADR-008 §7.7).
    """
    claimed = {
        (getattr(e, "slot", None), getattr(e, "aspect", None))
        for e in plan.effects()
    }
    filled = []
    for slot in score.slots():
        for aspect in Aspect:
            if not has_content(slot, aspect) or (slot.id, aspect) in claimed:
                continue
            filled.append((slot, aspect))
    del mint
    return filled


def _triggered(classifier, slot: Slot) -> bool:
    """One index, keyed on whichever closed set the rule declared."""
    triggers = classifier.triggers
    if not triggers:
        return True
    return (
        slot.letter in triggers
        or slot.nucleus.kind in triggers
        or slot.onset in triggers
    )


def _materialise(
    plan: Plan,
    index: dict[SlotId, Slot],
    score: Score,
    boundaries: BoundaryPlan,
    riwayah: Riwayah,
    selection: VariantSelection,
) -> Performance:
    mint = _Mint(score.words[0].location.verse if score.words else None)
    plain = Occurrence(mint.occurrence(), Rule.PLAIN, Participants())
    sounds: list[tuple[SoundId, Sound]] = []
    attributions: list[Attribution] = []
    occurrences: list[Occurrence] = []
    colours = _colours(plan)
    hosted: dict[tuple[SlotId, Aspect], SoundId] = {}

    for _, verdict in plan.entries:
        occurrences.append(verdict.occurrence)
    occurrences.append(plain)

    # Order matters. Explicit realizations, then the plain default, and only
    # then the merges — a merge target is usually realized by the default, so
    # resolving merges first leaves half a merger behind. P3 caught exactly
    # that, which is the argument for asserting the laws at all.
    for _, verdict in plan.entries:
        for effect in verdict.effects:
            if isinstance(effect, Realize):
                sound_id = mint.sound()
                sounds.append(
                    (sound_id, _apply_colours(effect, colours))
                )
                hosted[(effect.slot, effect.aspect)] = sound_id
                attributions.append(
                    Hosts((effect.slot,), effect.aspect, sound_id,
                          verdict.occurrence.id)
                )
            elif isinstance(effect, Insert):
                sound_id = mint.sound()
                sounds.append((sound_id, effect.sounds[0]))
                attributions.append(
                    Inserted(effect.anchor, effect.aspect, sound_id,
                             verdict.occurrence.id)
                )

    for slot, aspect in _fill_plain(plan, score, mint):
        sound_id = mint.sound()
        sounds.append((sound_id, _plain_sound(slot, aspect, colours)))
        hosted[(slot.id, aspect)] = sound_id
        attributions.append(Hosts((slot.id,), aspect, sound_id, plain.id))

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

    del index
    return Performance(
        riwayah=riwayah,
        sounds=tuple(sounds),
        attributions=tuple(attributions),
        occurrences=tuple(occurrences),
        selection=selection,
        boundaries=boundaries,
    )


def _plain_sound(slot: Slot, aspect: Aspect, colours) -> Sound:
    features = colours.get((slot.id, aspect), {})
    emphatic = bool(features.get(SoundFeature.EMPHATIC, False))
    if aspect is Aspect.ONSET:
        return Consonant(
            slot.letter,
            geminate=slot.onset is Onset.GEMINATE,
            emphatic=emphatic,
            nasal=bool(features.get(SoundFeature.NASAL, False)),
        )
    return Vowel(
        slot.nucleus.quality,
        long=slot.nucleus.kind in (NucleusKind.LONG, NucleusKind.SILAH,
                                   NucleusKind.PAUSAL_LONG),
        emphatic=emphatic,
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
    """A `SoundSpec` is a `Sound` with its context-dependent features unset;
    the materialiser fills them from later-phase `Recolour` effects."""
    sound = effect.sounds[0]
    features = colours.get((effect.slot, effect.aspect))
    if not features:
        return sound
    fields = {
        "emphatic": features.get(SoundFeature.EMPHATIC),
        "nasal": features.get(SoundFeature.NASAL),
    }
    match sound:
        case Consonant():
            return Consonant(
                sound.letter,
                sound.geminate,
                fields["emphatic"] if fields["emphatic"] is not None else sound.emphatic,
                fields["nasal"] if fields["nasal"] is not None else sound.nasal,
            )
        case Vowel():
            return Vowel(
                sound.quality,
                sound.long,
                fields["emphatic"] if fields["emphatic"] is not None else sound.emphatic,
            )
        case Nasal():
            return Nasal(
                sound.place,
                fields["emphatic"] if fields["emphatic"] is not None else sound.emphatic,
            )
    return sound


def lengthened(plan: Plan, slot: SlotId) -> Length | None:
    for effect in plan.effects():
        if isinstance(effect, Relength) and effect.slot == slot:
            return effect.length
    return None


def has_content(slot: Slot, aspect: Aspect) -> bool:
    """ADR-002 §7.4, stated precisely: `ONSET` always has canonical content;
    `NUCLEUS` has it unless the nucleus is `Silent`. A canonically absent
    nucleus is not a silenced one and requires no edge."""
    if aspect is Aspect.ONSET:
        return True
    return slot.nucleus.kind is not NucleusKind.SILENT
