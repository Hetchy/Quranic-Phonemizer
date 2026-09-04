"""Invariant checks over a completed `Performance`.

Every failure raises, naming the address and the two disagreeing sources;
none returns a sentinel.
"""
from __future__ import annotations

from collections.abc import Iterable

from ..model.address import SlotId
from ..model.canon import CLASSIFICATION_ONLY, Rule, Score
from ..model.inscription import (
    Attests,
    Decorates,
    Evidences,
    GraphemeId,
    Inscription,
)
from ..model.performance import (
    Aspect,
    Hosts,
    Inserted,
    MergedInto,
    Performance,
    Recolours,
    SetsLength,
    effect_targets,
)
from .run import has_content


class LawError(AssertionError):
    """Names the address and both sources. Loud beats silent."""


def check_performance(performance: Performance, score: Score) -> None:
    _every_sound_is_hosted_once(performance)
    _every_attribution_resolves(performance)
    _every_aspect_with_content_is_accounted_for(performance, score)
    _every_merge_has_its_host(performance)
    _every_occurrence_produced_or_declared(performance)
    _every_modifier_resolves(performance)


def _every_sound_is_hosted_once(performance: Performance) -> None:
    owned: dict[object, int] = {}
    for attribution in performance.attributions:
        if isinstance(attribution, (Hosts, Inserted)):
            owned[attribution.sound] = owned.get(attribution.sound, 0) + 1
    for sound_id, _ in performance.sounds:
        count = owned.get(sound_id, 0)
        if count != 1:
            raise LawError(
                f"P1: sound {sound_id} appears in {count} Hosts/Inserted "
                f"edges; every sound is owned exactly once"
            )


def _every_attribution_resolves(performance: Performance) -> None:
    known = {occurrence.id for occurrence in performance.occurrences}
    if len(known) != len(performance.occurrences):
        seen: dict[object, int] = {}
        for occurrence in performance.occurrences:
            seen[occurrence.id] = seen.get(occurrence.id, 0) + 1
        clash = next(i for i, n in seen.items() if n > 1)
        raise LawError(
            f"P2: occurrence id {clash} was minted twice. Two classifiers "
            f"sharing a Rule must pass different `variant`s to `mint`, or "
            f"every attribution citing the id is ambiguous about which one "
            f"produced it."
        )
    for attribution in performance.attributions:
        if attribution.by is not None and attribution.by not in known:
            raise LawError(
                f"P2: attribution cites occurrence {attribution.by}, which "
                f"does not exist. No sound exists except as the output of a "
                f"named occurrence, or as the Score's own unclaimed default."
            )


def _every_aspect_with_content_is_accounted_for(
    performance: Performance, score: Score
) -> None:
    covered: set[tuple[SlotId, Aspect]] = set()
    for attribution in performance.attributions:
        slots = getattr(attribution, "slots", ())
        for slot in slots:
            covered.add((slot, attribution.aspect))
    for slot in score.slots():
        for aspect in Aspect:
            if has_content(slot, aspect) and (slot.id, aspect) not in covered:
                raise LawError(
                    f"P3: {slot.id} {aspect.value} has canonical content "
                    f"({slot.letter.value}, {slot.nucleus.joined.form.value}) "
                    f"but no attribution and no explicit Silent edge"
                )


def _every_merge_has_its_host(performance: Performance) -> None:
    hosted = {
        (attribution.sound, attribution.by)
        for attribution in performance.attributions
        if isinstance(attribution, Hosts)
    }
    for attribution in performance.attributions:
        if isinstance(attribution, MergedInto):
            if (attribution.sound, attribution.by) not in hosted:
                raise LawError(
                    f"P4: {attribution.slots} merges into sound "
                    f"{attribution.sound} with no Hosts edge sharing its "
                    f"occurrence. A merger *is* the pair of edges."
                )


def _every_occurrence_produced_or_declared(performance: Performance) -> None:
    # A `Silent` edge counts as production: deleting a sound for a stated
    # reason (waqf ending, wasl elision) is a legitimate output. A modifier
    # counts too: a `Recolours`/`SetsLength`/`Classifies` edge is the rule's
    # own output just as much as a `Hosts` edge is.
    producing = {attribution.by for attribution in performance.attributions}
    producing |= {modifier.by for modifier in performance.modifiers}
    for occurrence in performance.occurrences:
        if occurrence.id in producing:
            continue
        if occurrence.rule in CLASSIFICATION_ONLY:
            continue
        raise LawError(
            f"E4: occurrence {occurrence.id} ({occurrence.rule.value}) left no "
            f"attribution at all and is not declared classification-only"
        )


def _every_modifier_resolves(performance: Performance) -> None:
    # `Classifies` is exempt from the one-edge-per-sound count below: unlike
    # a `Recolour`/`Relength`, which the Plan's own conflict detection keeps
    # to one per (slot, aspect), independent facts may classify one sound
    # more than once -- an imala vowel that is also `madd_arid_lissukun`.
    known_sounds = {sound_id for sound_id, _ in performance.sounds}
    known_occurrences = {occurrence.id for occurrence in performance.occurrences}
    seen: dict[tuple[type, object], int] = {}
    for modifier in performance.modifiers:
        if modifier.sound not in known_sounds:
            raise LawError(
                f"P5: modifier cites sound {modifier.sound}, which does not "
                f"exist"
            )
        if modifier.by not in known_occurrences:
            raise LawError(
                f"P5: modifier cites occurrence {modifier.by}, which does "
                f"not exist"
            )
        if isinstance(modifier, (Recolours, SetsLength)):
            key = (type(modifier), modifier.sound)
            seen[key] = seen.get(key, 0) + 1
    for (kind, sound_id), count in seen.items():
        if count != 1:
            raise LawError(
                f"P5: sound {sound_id} carries {count} {kind.__name__} "
                f"edges; an applied recolour or length change retains "
                f"exactly one"
            )


def check_inscription(inscription: Inscription, score: Score) -> None:
    """Every slot must be the target of at least one `Spelling`.

    Complements the check that catches a carrier wrongly promoted to a slot;
    this instead catches a slot that no grapheme reaches at all.
    """
    reached: set[SlotId] = set()
    for spelling in inscription.spellings:
        match spelling:
            case Evidences(slot=slot) | Decorates(slot=slot):
                reached.add(slot)
            case Attests(anchor=anchor):
                reached.add(anchor)
    for word in score.words:
        for slot in word.slots:
            if slot.id not in reached:
                raise LawError(
                    f"I7: slot {slot.id} ({slot.letter.value}, "
                    f"origin={slot.origin.value}) is the target of no Spelling "
                    f"in {inscription.script.value} — no grapheme accounts for "
                    f"it, so no projection can point at it"
                )


def check_graphemes_spelt(inscription: Inscription) -> None:
    """Every grapheme must be the source of at least one `Spelling`.

    The converse of `check_inscription`: a grapheme reaching no slot is one no
    projection can place and no alignment can show."""
    spelt: set[GraphemeId] = {
        spelling.grapheme for spelling in inscription.spellings
    }
    for grapheme in inscription.graphemes:
        if grapheme.id not in spelt:
            raise LawError(
                f"I8: grapheme {grapheme.id} ({grapheme.char!r}) is the source "
                f"of no Spelling in {inscription.script.value} — the script "
                f"wrote it and the Score accounts for it nowhere"
            )


#: What a written shadda can witness: every merger the model recognises.
#: `Attests` names no rule of its own, so the completeness law checks
#: against this closed set instead of a model-level family.
MERGER_RULES: frozenset[Rule] = frozenset({
    Rule.IDGHAM_BI_GHUNNAH,
    Rule.IDGHAM_BILA_GHUNNAH,
    Rule.IDGHAM_SHAFAWI,
    Rule.IDGHAM_MUTAMATHILAYN,
    Rule.IDGHAM_MUTAQARIBAYN,
    Rule.IDGHAM_MUTAJANISAYN_KAMIL,
    Rule.IDGHAM_MUTAJANISAYN_NAQIS,
    Rule.LAM_SHAMSIYYAH,
    Rule.LAM_QAMARIYYAH,
})


def check_attestations(
    attested: Iterable[SlotId],
    performance: Performance,
) -> list[str]:
    """Every slot a script attests must be produced by some merger occurrence:
    its subject, and whatever its own edges name beside it. One-directional,
    and disagreements are returned rather than raised one at a time."""
    targets = effect_targets(performance)
    produced: set[SlotId] = set()
    for occurrence in performance.occurrences:
        if occurrence.rule in MERGER_RULES:
            produced.update(occurrence.subjects)
            produced.update(targets.get(occurrence.id, ()))
    return [
        f"A1: {slot} is attested but no merger occurrence names it"
        for slot in attested
        if slot not in produced
    ]
