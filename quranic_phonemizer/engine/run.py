"""The phase driver: run the rules, then turn the Plan into a Performance.

Phases are closed and ordered; within a phase, rules are unordered and any
conflict between them raises rather than resolving silently.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..model.address import (
    BoundaryPlan,
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
from .plan import mint as plan_mint

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
    """Realize every (slot, aspect) no verdict claimed, tagged `Rule.PLAIN`.

    `PLAIN` can't be a classifier: it would conflict with every claiming rule.
    """
    # Only effects that produce or remove a sound claim the slot; Recolour
    # and Relength modify an existing one and must not count as claiming it.
    claimed = {
        (effect.slot, effect.aspect)
        for effect in plan.effects()
        if isinstance(effect, (Realize, MergeInto, Silence))
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
    """Whether a slot matches a classifier's declared trigger set.

    Checks letter, nucleus kind, onset, and quality; no triggers declared
    means the classifier always fires.
    """
    triggers = classifier.triggers
    if not triggers:
        return True
    return (
        slot.letter in triggers
        or slot.nucleus.kind in triggers
        or slot.onset in triggers
        or getattr(slot.nucleus, "quality", None) in triggers
        or bool(slot.annotations & triggers)
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
    # Minted through the same `plan_mint` scheme as every other occurrence,
    # so its id cannot collide with one a rule mints independently.
    plain = Occurrence(
        plan_mint(Rule.PLAIN, SlotId(score.words[0].location.verse, 0)),
        Rule.PLAIN,
        Participants(),
    )
    sounds: list[tuple[SoundId, Sound]] = []
    attributions: list[Attribution] = []
    occurrences: list[Occurrence] = []
    colours = _colours(plan)
    hosted: dict[tuple[SlotId, Aspect], SoundId] = {}

    for _, verdict in plan.entries:
        occurrences.append(verdict.occurrence)
    occurrences.append(plain)

    # Merges resolve last: a merge target is usually realized by the plain
    # fill, so merging first would leave it half-hosted.
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

    lengths = {e.slot: e.length for e in plan.effects() if isinstance(e, Relength)}
    for slot, aspect in _fill_plain(plan, score, mint):
        sound_id = mint.sound()
        sounds.append((sound_id, _plain_sound(slot, aspect, colours, lengths)))
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


def _plain_sound(slot: Slot, aspect: Aspect, colours, lengths=None) -> Sound:
    features = colours.get((slot.id, aspect), {})
    emphatic = bool(features.get(SoundFeature.EMPHATIC, False))
    if aspect is Aspect.ONSET:
        return Consonant(
            slot.letter,
            geminate=slot.onset is Onset.GEMINATE,
            emphatic=emphatic,
            nasal=bool(features.get(SoundFeature.NASAL, False)),
        )
    long = slot.nucleus.kind in (
        NucleusKind.LONG, NucleusKind.SILAH, NucleusKind.PAUSAL_LONG
    )
    override = (lengths or {}).get(slot.id)
    if override is not None:
        long = override is Length.LONG
    return Vowel(slot.nucleus.quality, long=long, emphatic=emphatic)


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


def has_content(slot: Slot, aspect: Aspect) -> bool:
    """`ONSET` always has canonical content; `NUCLEUS` has it unless the
    nucleus is `Silent`. A canonically absent nucleus needs no Silent edge."""
    if aspect is Aspect.ONSET:
        return True
    return slot.nucleus.kind is not NucleusKind.SILENT
