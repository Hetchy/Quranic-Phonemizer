"""Validation the highlight groups must pass before a consumer reads them.

Every sound and every lexical unit lands in exactly one ordered group; no group
is silent-only; a group holds one owner unless a shared sound joins a second.
"""
from __future__ import annotations

from .dtos import AnalysisBundle
from .highlight_dtos import HighlightGroup
from .source_dtos import CharacterKind, SourceView


class HighlightValidationError(ValueError):
    """Highlight groups whose coverage or order does not close."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HighlightValidationError(message)


def _check_references(groups, view: SourceView, bundle: AnalysisBundle) -> None:
    unit_ids = {unit.id for unit in view.units}
    sound_ids = {sound.id for sound in bundle.sounds}
    for order, group in enumerate(groups):
        _require(group.id.value == order, "group ids are not positional")
        for unit in group.unit_ids:
            _require(unit in unit_ids, f"group {order} names a missing unit")
        for sound in group.sound_ids:
            _require(sound in sound_ids, f"group {order} names a missing sound")
        for (lo, hi), (nlo, _) in zip(group.ranges, group.ranges[1:]):
            _require(lo < hi <= nlo, f"group {order} ranges overlap or misorder")
        for lo, hi in group.ranges:
            _require(lo < hi, f"group {order} has an empty range")


def _check_sounds(groups, bundle: AnalysisBundle) -> None:
    seen: list[int] = [s.value for group in groups for s in group.sound_ids]
    _require(
        sorted(seen) == list(range(len(bundle.sounds))),
        "the highlighted sounds are not exactly the result's sounds",
    )


def _lexical_positions(view: SourceView) -> set[int]:
    return {
        char.index
        for char in view.characters
        if char.kind is CharacterKind.LEXICAL
    }


def _check_coverage(groups, view: SourceView) -> None:
    units: list[int] = [u.value for group in groups for u in group.unit_ids]
    _require(
        sorted(units) == list(range(len(view.units))),
        "the highlighted units are not exactly the source units",
    )
    covered: set[int] = set()
    for group in groups:
        for lo, hi in group.ranges:
            covered.update(range(lo, hi))
    _require(
        covered == _lexical_positions(view),
        "the highlighted ranges are not the lexical span of the text",
    )


def _check_groups_are_sounded(groups, view: SourceView) -> None:
    for group in groups:
        _require(bool(group.sound_ids), f"group {group.id.value} holds no sound")
        owners = [
            unit for unit in group.unit_ids
            if view.units[unit.value].owned_sound_ids
        ]
        _require(
            bool(owners),
            f"group {group.id.value} is silent-only, no unit owns a sound",
        )


def _owner_of(view: SourceView) -> dict[int, int]:
    return {
        sound.value: unit.id.value
        for unit in view.units
        for sound in unit.owned_sound_ids
    }


def _check_multi_owner(groups, view: SourceView) -> None:
    """A group with more than one sound-owning unit is legitimate only when a
    presentation or a seen/saad ride ties the owners into one relation."""
    owner_of = _owner_of(view)
    for group in groups:
        owners = {
            u.value for u in group.unit_ids
            if view.units[u.value].owned_sound_ids
        }
        if len(owners) <= 1:
            continue
        link: dict[int, set[int]] = {owner: set() for owner in owners}
        for unit_id in group.unit_ids:
            unit = view.units[unit_id.value]
            for sound in unit.presented_sound_ids:
                held = owner_of.get(sound.value)
                if held in owners and unit_id.value in owners:
                    link[unit_id.value].add(held)
                    link[held].add(unit_id.value)
            ridden = unit.written_on_unit_id
            if ridden is not None and ridden.value in owners and unit_id.value in owners:
                link[unit_id.value].add(ridden.value)
                link[ridden.value].add(unit_id.value)
        _require(
            _connected(owners, link),
            f"group {group.id.value} joins owners nothing shares a sound with",
        )


def _connected(nodes: set[int], link: dict[int, set[int]]) -> bool:
    start = next(iter(nodes))
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbour in link[node]:
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    return seen == nodes


def _check_order(groups) -> None:
    firsts = [group.sound_ids[0].value for group in groups if group.sound_ids]
    _require(firsts == sorted(firsts), "groups are not in sound order")
    for group in groups:
        units = [u.value for u in group.unit_ids]
        sounds = [s.value for s in group.sound_ids]
        _require(units == sorted(units), f"group {group.id.value} units unordered")
        _require(sounds == sorted(sounds), f"group {group.id.value} sounds unordered")


def validate_highlight_groups(
    groups: tuple[HighlightGroup, ...],
    view: SourceView,
    bundle: AnalysisBundle,
) -> None:
    _check_references(groups, view, bundle)
    _check_sounds(groups, bundle)
    _check_coverage(groups, view)
    _check_groups_are_sounded(groups, view)
    _check_multi_owner(groups, view)
    _check_order(groups)


__all__ = ["HighlightValidationError", "validate_highlight_groups"]
