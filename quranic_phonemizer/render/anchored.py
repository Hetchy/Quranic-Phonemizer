"""The projection the design is actually for: sounds anchored to the writing.

A consumer holding script text wants three answers, and until `Spelling` was
built only two of them existed:

    which rule fired here        -> `Occurrence.parts`      (always worked)
    which letters are silent     -> `Silent(..., by=...)`   (always worked)
    which graphemes made this    -> needed `Spelling`       (this module)

The third is the one that lets an application highlight the letters that
produced a sound, or show why a letter is silent by pointing at the mark that
silenced it. It is a *lookup*, never a second detection: every edge read here
was recorded by the layer that decided it (ADR-002 §5).

The traversal is `sound -> attribution -> (slot, aspect) -> Spelling`, one
direction only, exactly as ADR-002 §5 specifies it.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from ..model.address import GraphemeId, SlotId, SoundId
from ..model.canon import Rule, Score
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

#: Which `SlotFact` a `Spelling` must carry to count as writing a given aspect.
#: A grapheme that evidences the letter is writing the onset; one that
#: evidences the nucleus is writing the nucleus. `Decorates` and `Attests`
#: name a slot without naming an aspect, so they answer for both.
_FACT_OF_ASPECT = {
    Aspect.ONSET: (SlotFact.LETTER, SlotFact.ONSET),
    Aspect.NUCLEUS: (SlotFact.NUCLEUS,),
}


@dataclass(frozen=True, slots=True)
class AnchoredSound:
    """One sound, and everything a consumer can ask about it."""

    sound: SoundId
    token: str
    slots: tuple[SlotId, ...]
    """Every slot that produced it. More than one is a merger."""
    graphemes: tuple[GraphemeId, ...]
    rule: Rule
    merged_from: tuple[SlotId, ...] = ()
    """Slots whose own sound was folded into this one."""


@dataclass(frozen=True, slots=True)
class SilentLetter:
    """A slot that produced no sound, and the rule that says why."""

    slot: SlotId
    graphemes: tuple[GraphemeId, ...]
    rule: Rule


@dataclass(frozen=True, slots=True)
class AnchoredView:
    sounds: tuple[AnchoredSound, ...]
    silent: tuple[SilentLetter, ...]

    def by_grapheme(self) -> dict[GraphemeId, tuple[SoundId, ...]]:
        """The inverse: what each written grapheme ended up producing.

        Empty for a grapheme that produced nothing — a silence sign, a stop
        mark — which is a fact worth having rather than an absence.
        """
        out: dict[GraphemeId, list[SoundId]] = {}
        for anchored in self.sounds:
            for grapheme in anchored.graphemes:
                out.setdefault(grapheme, []).append(anchored.sound)
        return {grapheme: tuple(ids) for grapheme, ids in out.items()}


def anchored(
    performance: Performance,
    score: Score,
    inscription: Inscription,
    alphabet: Alphabet,
) -> AnchoredView:
    del score
    writes = _writers(inscription)
    rule_of = {
        occurrence.id: occurrence.rule for occurrence in performance.occurrences
    }
    by_id = dict(performance.sounds)
    merged: dict[SoundId, list[SlotId]] = defaultdict(list)
    for attribution in performance.attributions:
        if isinstance(attribution, MergedInto):
            merged[attribution.sound].extend(attribution.slots)

    owners: dict[SoundId, tuple[tuple[SlotId, ...], Aspect, Rule]] = {}
    for attribution in performance.attributions:
        match attribution:
            case Hosts(slots=slots, aspect=aspect, sound=sound):
                owners[sound] = (slots, aspect, rule_of[attribution.by])
            case Inserted(anchor=(slot, _), aspect=aspect, sound=sound):
                owners[sound] = ((slot,), aspect, rule_of[attribution.by])

    sounds = []
    for sound in sounds_in_order(performance):
        slots, aspect, rule = owners[sound]
        graphemes = _graphemes_for(writes, slots, aspect)
        contributors = tuple(merged.get(sound, ()))
        if contributors:
            graphemes = _dedupe(
                graphemes + _graphemes_for(writes, contributors, aspect)
            )
        sounds.append(
            AnchoredSound(
                sound=sound,
                token=alphabet.token(by_id[sound]),
                slots=tuple(slots),
                graphemes=graphemes,
                rule=rule,
                merged_from=contributors,
            )
        )

    silent = tuple(
        SilentLetter(
            slot=slot,
            graphemes=_graphemes_for(writes, (slot,), attribution.aspect),
            rule=rule_of[attribution.by],
        )
        for attribution in performance.attributions
        if isinstance(attribution, Silent)
        for slot in attribution.slots
    )
    return AnchoredView(tuple(sounds), silent)


def graphemes_by_id(inscription: Inscription) -> dict[GraphemeId, Grapheme]:
    """So a consumer can turn an id back into the character it wrote."""
    return {grapheme.id: grapheme for grapheme in inscription.graphemes}


def _writers(
    inscription: Inscription,
) -> dict[SlotId, dict[SlotFact | None, list[GraphemeId]]]:
    """slot -> fact -> the graphemes that wrote it. `None` means "names the
    slot without naming a fact", which is what `Decorates` and `Attests` do."""
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
