"""Validation the bundle must pass before a result exposes it.

Every published id resolves and back-references agree both ways; boundary
cardinality and state are exact; each merger crosses one adjacent boundary.
"""
from __future__ import annotations

from . import ids
from .catalogue import rule_definitions
from .dtos import AnalysisBundle, BoundaryState


class ValidationError(ValueError):
    """A bundle whose ids or structure do not close."""


def validate(bundle: AnalysisBundle) -> None:
    word_ids = {word.id for word in bundle.words}
    boundary_ids = {boundary.id for boundary in bundle.boundaries}
    sound_ids = {sound.id for sound in bundle.sounds}
    occ_ids = {occurrence.id for occurrence in bundle.rule_occurrences}
    rule_ids = {definition.id for definition in rule_definitions()}

    _check_boundaries(bundle, word_ids)
    _check_words(bundle, boundary_ids, sound_ids)
    _check_sounds(bundle, word_ids, occ_ids)
    _check_sound_occurrence_inverse(bundle)
    _check_occurrences(bundle, word_ids, boundary_ids, sound_ids, rule_ids)
    _check_mergers(bundle, word_ids, boundary_ids, sound_ids, occ_ids)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _check_boundaries(bundle: AnalysisBundle, word_ids: set) -> None:
    boundaries = bundle.boundaries
    _require(
        len(boundaries) == len(bundle.words) + 1,
        "there must be one more boundary than words",
    )
    _require(boundaries[0].state is BoundaryState.START, "the lead is not a start")
    _require(boundaries[-1].state is BoundaryState.STOP, "the tail is not a stop")
    last = len(boundaries) - 1
    for i, boundary in enumerate(boundaries):
        _require(boundary.id == ids.BoundaryId(i), "boundary ids are not positional")
        expect_before = None if i == 0 else ids.WordId(i - 1)
        expect_after = None if i == last else ids.WordId(i)
        _require(boundary.before == expect_before, f"boundary {i} before is wrong")
        _require(boundary.after == expect_after, f"boundary {i} after is wrong")
        _require(expect_before is None or expect_before in word_ids,
                 f"boundary {i} names a missing word")
        _require(
            i in (0, last) or boundary.state is not BoundaryState.START,
            f"internal boundary {i} resolves to start",
        )


def _check_words(bundle: AnalysisBundle, boundary_ids: set, sound_ids: set) -> None:
    for i, word in enumerate(bundle.words):
        _require(word.id == ids.WordId(i), "word ids are not positional")
        _require(
            word.before_boundary_id == ids.BoundaryId(i)
            and word.after_boundary_id == ids.BoundaryId(i + 1),
            f"word {i} boundary ids are wrong",
        )
        _require(
            bundle.boundaries[i].after == word.id
            and bundle.boundaries[i + 1].before == word.id,
            f"word {i} and its boundaries disagree",
        )
        for sound in word.sound_ids:
            _require(sound in sound_ids, f"word {i} names a missing sound")


def _check_sounds(bundle: AnalysisBundle, word_ids: set, occ_ids: set) -> None:
    for i, sound in enumerate(bundle.sounds):
        _require(sound.id == ids.SoundId(i) and sound.order == i,
                 "sound order is not its position")
        _require(sound.word_id in word_ids, f"sound {i} names a missing word")
        for occ in sound.rule_occurrence_ids:
            _require(occ in occ_ids, f"sound {i} names a missing occurrence")


def _check_sound_occurrence_inverse(bundle: AnalysisBundle) -> None:
    """Word.sound_ids and Sound.word_id are exact ordered inverses, and
    Sound.rule_occurrence_ids and RuleOccurrence.sound_ids agree."""
    allocation: dict = {}
    for word in bundle.words:
        for order, sound in enumerate(word.sound_ids):
            allocation[sound] = (word.id, order)
    for sound in bundle.sounds:
        held = allocation.get(sound.id)
        _require(
            held is not None and held[0] == sound.word_id,
            f"sound {sound.order} allocation disagrees with its word",
        )
    per_occ = {occ.id: set(occ.sound_ids) for occ in bundle.rule_occurrences}
    for sound in bundle.sounds:
        for occ in sound.rule_occurrence_ids:
            _require(sound.id in per_occ[occ],
                     f"sound {sound.order} and occurrence disagree")


def _check_occurrences(
    bundle: AnalysisBundle, word_ids, boundary_ids, sound_ids, rule_ids
) -> None:
    per_sound = {sound.id: set(sound.rule_occurrence_ids) for sound in bundle.sounds}
    for occurrence in bundle.rule_occurrences:
        _require(occurrence.rule_id in rule_ids, "occurrence names an unknown rule")
        for word in occurrence.word_ids:
            _require(word in word_ids, "occurrence names a missing word")
        for boundary in occurrence.boundary_ids:
            _require(boundary in boundary_ids, "occurrence names a missing boundary")
        for sound in occurrence.sound_ids:
            _require(sound in sound_ids, "occurrence names a missing sound")
            _require(occurrence.id in per_sound[sound],
                     "occurrence and sound disagree")


def _check_mergers(
    bundle: AnalysisBundle, word_ids, boundary_ids, sound_ids, occ_ids
) -> None:
    for merger in bundle.mergers:
        _require(merger.boundary_id in boundary_ids, "merger names a missing boundary")
        _require(merger.before_word_id in word_ids and merger.after_word_id in word_ids,
                 "merger names a missing word")
        _require(merger.sound_id in sound_ids, "merger names a missing sound")
        before, after = merger.before_word_id.value, merger.after_word_id.value
        _require(abs(before - after) == 1, "merger does not cross one boundary")
        _require(merger.boundary_id == ids.BoundaryId(max(before, after)),
                 "merger boundary is not the crossed one")
        for occ in merger.rule_occurrence_ids:
            _require(occ in occ_ids, "merger names a missing occurrence")


__all__ = ["ValidationError", "validate"]
