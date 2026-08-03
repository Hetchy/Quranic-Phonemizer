"""Anchors performed sounds and silent letters back onto the written text.

A lookup only, traversing `sound -> attribution -> (slot, aspect) ->
Spelling`: every edge here was recorded by the layer that decided it.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ..model.address import GraphemeId, SlotId, SoundId
from ..model.canon import Rule
from ..model.inscription import (
    Attests,
    Decorates,
    Evidences,
    Grapheme,
    Inscription,
    SlotFact,
)
from ..model.performance import (
    Aspect,
    Hosts,
    Inserted,
    MergedInto,
    Performance,
    Silent,
)
from .alphabet import Alphabet
from .recite import sounds_in_order

#: Which `SlotFact`s count as writing each `Aspect`. `Decorates` and
#: `Attests` don't name an aspect, so they satisfy either one.
_FACT_OF_ASPECT = {
    Aspect.CONSONANT: (SlotFact.LETTER, SlotFact.ONSET),
    Aspect.VOWEL: (SlotFact.NUCLEUS,),
}


@dataclass(frozen=True, slots=True)
class AnchoredSound:
    """One sound, and everything a consumer can ask about it."""

    sound: SoundId
    token: str
    slots: tuple[SlotId, ...]
    """Every slot that produced it. More than one is a merger."""
    graphemes: tuple[GraphemeId, ...]
    rule: Rule | None
    """`None` where the Score's own default filled the sound: no rule
    claimed it."""
    merged_from: tuple[SlotId, ...] = ()
    """Slots whose own sound was folded into this one."""


@dataclass(frozen=True, slots=True)
class SilentLetter:
    """A slot that produced no sound, and the rule that says why."""

    slot: SlotId
    graphemes: tuple[GraphemeId, ...]
    rule: Rule | None


@dataclass(frozen=True, slots=True)
class AnchoredView:
    sounds: tuple[AnchoredSound, ...]
    silent: tuple[SilentLetter, ...]

    def by_grapheme(self) -> dict[GraphemeId, tuple[SoundId, ...]]:
        """The inverse: which sounds each written grapheme produced.

        Empty for a grapheme that produced nothing, such as a silence sign
        or a stop mark.
        """
        out: dict[GraphemeId, list[SoundId]] = {}
        for anchored in self.sounds:
            for grapheme in anchored.graphemes:
                out.setdefault(grapheme, []).append(anchored.sound)
        return {grapheme: tuple(ids) for grapheme, ids in out.items()}


def anchored(
    performance: Performance,
    inscription: Inscription,
    alphabet: Alphabet,
) -> AnchoredView:
    writes = _writers(inscription)
    rule_of = {
        occurrence.id: occurrence.rule for occurrence in performance.occurrences
    }
    by_id = dict(performance.sounds)
    merged: dict[SoundId, list[SlotId]] = defaultdict(list)
    for attribution in performance.attributions:
        if isinstance(attribution, MergedInto):
            merged[attribution.sound].extend(attribution.slots)
    owners = _owners(performance, rule_of)

    sounds = tuple(
        _anchored_sound(sound, owners, merged, writes, by_id, alphabet)
        for sound in sounds_in_order(performance)
    )
    silent = tuple(
        SilentLetter(
            slot=slot,
            graphemes=_graphemes_for(writes, (slot,), attribution.aspect),
            rule=rule_of.get(attribution.by),
        )
        for attribution in performance.attributions
        if isinstance(attribution, Silent)
        for slot in attribution.slots
    )
    return AnchoredView(sounds, silent)


def _owners(performance: Performance, rule_of) -> dict:
    """Which slots each sound is attributed to, and by which rule."""
    out: dict[SoundId, tuple[tuple[SlotId, ...], Aspect, Rule | None]] = {}
    for attribution in performance.attributions:
        match attribution:
            case Hosts(slots=slots, aspect=aspect, sound=sound):
                out[sound] = (slots, aspect, rule_of.get(attribution.by))
            case Inserted(anchor=(slot, _), aspect=aspect, sound=sound):
                out[sound] = ((slot,), aspect, rule_of.get(attribution.by))
    return out


def _anchored_sound(sound, owners, merged, writes, by_id, alphabet):
    slots, aspect, rule = owners[sound]
    graphemes = _graphemes_for(writes, slots, aspect)
    contributors = tuple(merged.get(sound, ()))
    if contributors:
        graphemes = _dedupe(
            graphemes + _graphemes_for(writes, contributors, aspect)
        )
    return AnchoredSound(
        sound=sound,
        token=alphabet.token(by_id[sound]),
        slots=tuple(slots),
        graphemes=graphemes,
        rule=rule,
        merged_from=contributors,
    )


def graphemes_by_id(inscription: Inscription) -> dict[GraphemeId, Grapheme]:
    """So a consumer can turn an id back into the character it wrote."""
    return {grapheme.id: grapheme for grapheme in inscription.graphemes}


def _writers(
    inscription: Inscription,
) -> dict[SlotId, dict[SlotFact | None, list[GraphemeId]]]:
    """Maps slot -> fact -> graphemes that wrote it. `None` is the fact used
    by `Decorates` and `Attests`, which don't name one."""
    out: dict[SlotId, dict[SlotFact | None, list[GraphemeId]]] = {}
    for spelling in inscription.spellings:
        match spelling:
            case Evidences(grapheme=grapheme, slot=slot, fact=fact):
                key: SlotFact | None = fact
            case Decorates(grapheme=grapheme, slot=slot):
                key = None
            case Attests(grapheme=grapheme, anchor=slot):
                key = None
            case _:
                continue
        out.setdefault(slot, {}).setdefault(key, []).append(grapheme)
    return out


def _graphemes_for(writes, slots, aspect: Aspect) -> tuple[GraphemeId, ...]:
    wanted = _FACT_OF_ASPECT[aspect]
    found: list[GraphemeId] = []
    for slot in slots:
        facts = writes.get(slot, {})
        for fact in wanted:
            found.extend(facts.get(fact, ()))
        found.extend(facts.get(None, ()))
    return _dedupe(tuple(found))


def _dedupe(ids: tuple[GraphemeId, ...]) -> tuple[GraphemeId, ...]:
    seen: dict[GraphemeId, None] = {}
    for identifier in ids:
        seen[identifier] = None
    return tuple(seen)
