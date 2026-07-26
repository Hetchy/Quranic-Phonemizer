"""Totality and agreement, asserted over a completed `Performance`.

These are the domain-facts invariants made structural. Every failure names the
address and the two disagreeing sources; none returns a sentinel.
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
    # A `Silent` edge counts. Deletion-with-a-reason is a legitimate output —
    # `WAQF_ENDING` and `WASL_ELISION` exist to remove sounds, and excluding
    # them here made E4 fire on rules that were working correctly. What E4 is
    # for is a rule that fires and leaves no edge of any kind.
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
    """I7 and I8 (ADR-003 §4.0): the Score is **reachable from the writing**.

    Every slot must be the target of at least one `Spelling`. This is the law
    that makes a grapheme-anchored projection possible at all — a slot no
    grapheme reaches is a sound the consumer cannot point at in the text.

    It is the direction S1 cannot cover. S1 catches a carrier wrongly promoted
    to slot-hood, because such a slot hosts nothing; it cannot catch a slot
    that no writing accounts for. The tanwīn nūn was exactly that for the whole
    first draft — the projection spike measured 5,831 unreached Uthmani slots
    and every one was this — and it is reached now because the tanwīn mark
    evidences both the host's vowel and the nūn, which is what A1's ruling says
    it does.
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
    """The attestation law (A1), one-directional.

    If a script attests family `F` at slot `s`, the engine must produce an
    occurrence of *some* rule in `F` with `s` among its participants. Never the
    reverse: word-initial shadda ʿāriḍah is 3,722 Uthmani against 5,761
    IndoPak, agreeing on 3,534, and neither inventory is a superset — a
    bidirectional law fails on 2,415 words.

    Returns the disagreements rather than raising, so a caller can report them
    all at once.
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
