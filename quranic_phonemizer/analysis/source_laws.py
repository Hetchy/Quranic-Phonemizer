"""Validation the source view must pass before a consumer reads it.

Characters cover the text and each is one kind; a unit's ranges reproduce its
characters; sounds have one owner; a silent unit names a rule or the orthographic.
"""
from __future__ import annotations

from .checks import requirer
from .dtos import AnalysisBundle
from .source_dtos import CharacterKind, LiteralSilence, SourceView


class SourceValidationError(ValueError):
    """A source view whose characters, units or placements do not close."""


_require = requirer(SourceValidationError)


def _check_characters(view: SourceView, unit_ids: set, word_ids: set) -> None:
    _require(
        "".join(c.text for c in view.characters) == view.text,
        "characters do not concatenate to the text",
    )
    for i, char in enumerate(view.characters):
        _require(char.index == i and char.id.value == i,
                 f"character {i} is out of order")
        if char.kind is CharacterKind.LEXICAL:
            _require(
                char.word_id in word_ids and char.letter_unit_id in unit_ids
                and char.boundary_id is None,
                f"lexical character {i} is not unit-owned",
            )
        else:
            _require(
                char.boundary_id is not None and char.word_id is None
                and char.letter_unit_id is None,
                f"boundary character {i} names a word or unit",
            )


def _check_ranges(view: SourceView) -> None:
    for unit in view.units:
        ids = [c.value for c in unit.character_ids]
        spanned = [i for lo, hi in unit.ranges for i in range(lo, hi)]
        _require(sorted(ids) == sorted(spanned),
                 f"unit {unit.id.value} ranges do not reproduce its characters")
        _require(
            unit.text == "".join(view.characters[i].text for i in sorted(ids)),
            f"unit {unit.id.value} text is not its characters",
        )


def _check_membership(view: SourceView, unit_ids: set) -> None:
    for char in view.characters:
        if char.kind is not CharacterKind.LEXICAL:
            continue
        unit = view.units[char.letter_unit_id.value]
        _require(char.id in unit.character_ids,
                 f"character {char.id.value} is not held by its unit")
    for unit in view.units:
        _require(
            unit.written_on_unit_id is None or unit.written_on_unit_id in unit_ids,
            f"unit {unit.id.value} rides a missing unit",
        )


def _check_ownership(view: SourceView, sound_count: int) -> None:
    owned: set[int] = set()
    for unit in view.units:
        own = {s.value for s in unit.owned_sound_ids}
        present = {s.value for s in unit.presented_sound_ids}
        _require(not (own & present),
                 f"unit {unit.id.value} owns and presents one sound")
        for sound in own:
            _require(sound not in owned, f"sound {sound} has two owners")
            owned.add(sound)
    _require(owned == set(range(sound_count)),
             "the owned sounds are not exactly the result's sounds")


def _check_silence(view: SourceView, occ_ids: set) -> None:
    for unit in view.units:
        if unit.silence is None:
            continue
        _require(not unit.owned_sound_ids and not unit.presented_sound_ids,
                 f"silent unit {unit.id.value} still sounds")
        if isinstance(unit.silence, LiteralSilence):
            continue
        _require(unit.silence in occ_ids,
                 f"unit {unit.id.value} names a missing silence occurrence")
        _require(unit.silence in unit.rule_occurrence_ids,
                 f"unit {unit.id.value} does not carry its silencer")


def _check_placements(view: SourceView, bundle: AnalysisBundle, unit_ids: set) -> None:
    by_unit: dict[int, set[int]] = {u.id.value: set() for u in view.units}
    for placement in view.rule_placements:
        for unit in placement.unit_ids:
            _require(unit in unit_ids, "a rule placement names a missing unit")
            by_unit[unit.value].add(placement.rule_occurrence_id.value)
    _require(
        len(view.rule_placements) == len(bundle.rule_occurrences),
        "there is not one rule placement per occurrence",
    )
    for unit in view.units:
        _require(
            {o.value for o in unit.rule_occurrence_ids} == by_unit[unit.id.value],
            f"unit {unit.id.value} rule queries disagree with its placements",
        )
    _check_mergers(view, bundle, unit_ids)


def _check_mergers(view: SourceView, bundle: AnalysisBundle, unit_ids: set) -> None:
    _require(
        len(view.merger_placements) == len(bundle.mergers),
        "there is not one merger placement per merger",
    )
    for placement in view.merger_placements:
        _require(0 <= placement.merger_id.value < len(bundle.mergers),
                 "a merger placement names a missing merger")
        _require(bool(placement.after_unit_ids),
                 f"merger {placement.merger_id.value} hosts on no unit")
        for unit in (*placement.before_unit_ids, *placement.after_unit_ids):
            _require(unit in unit_ids, "a merger placement names a missing unit")


def validate_source_view(view: SourceView, bundle: AnalysisBundle) -> None:
    unit_ids = {unit.id for unit in view.units}
    word_ids = {word.id for word in bundle.words}
    occ_ids = {occ.id for occ in bundle.rule_occurrences}
    for i, unit in enumerate(view.units):
        _require(unit.id.value == i, "unit ids are not positional")
    _check_characters(view, unit_ids, word_ids)
    _check_ranges(view)
    _check_membership(view, unit_ids)
    _check_ownership(view, len(bundle.sounds))
    _check_silence(view, occ_ids)
    _check_placements(view, bundle, unit_ids)


__all__ = ["SourceValidationError", "validate_source_view"]
