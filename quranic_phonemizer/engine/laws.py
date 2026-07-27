"""Invariant checks over a completed `Performance`.

Every failure raises, naming the address and the two disagreeing sources;
none returns a sentinel.
"""
from __future__ import annotations

from collections.abc import Iterable

from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CLASSIFICATION_ONLY, FAMILY_OF, RuleFamily, Score
from ..model.inscription import Attests, Decorates, Evidences, Inscription
from ..model.performance import (
    Aspect,
    Hosts,
    Inserted,
    MergedInto,
    Performance,
    Silent,
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
        if attribution.by not in known:
            raise LawError(
                f"P2: attribution cites occurrence {attribution.by}, which "
                f"does not exist. No sound exists except as the output of a "
                f"named occurrence."
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
                    f"({slot.letter.value}, {slot.nucleus.kind.value}) but no "
                    f"attribution and no explicit Silent edge"
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
    # reason (waqf ending, wasl elision) is a legitimate output.
    producing = {attribution.by for attribution in performance.attributions}
    for occurrence in performance.occurrences:
        if occurrence.id in producing:
            continue
        if occurrence.rule in CLASSIFICATION_ONLY:
            continue
        raise LawError(
            f"E4: occurrence {occurrence.id} ({occurrence.rule.value}) left no "
            f"attribution at all and is not declared classification-only"
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


def check_attestations(
    attested: Iterable[tuple[SlotId, RuleFamily]],
    performance: Performance,
    boundaries: BoundaryPlan,
) -> list[str]:
    """Every family a script attests must be produced by some occurrence.

    One-directional: an occurrence family with no matching attestation is
    not an error. Returns disagreements instead of raising them individually.
    """
    del boundaries
    produced: dict[SlotId, set[RuleFamily]] = {}
    for occurrence in performance.occurrences:
        family = FAMILY_OF[occurrence.rule]
        for slot in occurrence.parts.slots:
            produced.setdefault(slot, set()).add(family)
    return [
        f"A1: {slot} attests {family.value} but no occurrence of that family "
        f"names it (produced: {sorted(f.value for f in produced.get(slot, ()))})"
        for slot, family in attested
        if family not in produced.get(slot, set())
    ]
