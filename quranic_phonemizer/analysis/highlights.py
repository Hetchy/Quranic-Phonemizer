"""Continuous-text highlight groups over the source view.

A unit that owns a sound seeds a group; presenters, seen/saad pairs, and every
silent or soundless unit fold into the group that carries their sound.
"""
from __future__ import annotations

from collections import defaultdict

from ..model.canon import Rule
from . import ids
from .dtos import AnalysisBundle
from .highlight_dtos import HighlightGroup
from .highlight_laws import validate_highlight_groups
from .source_dtos import SourceView


class _Merge:
    """Disjoint-set over unit indices."""

    __slots__ = ("_parent",)

    def __init__(self, size: int) -> None:
        self._parent = list(range(size))

    def find(self, node: int) -> int:
        parent = self._parent
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(self, left: int, right: int) -> None:
        self._parent[self.find(left)] = self.find(right)


def _owner_of(view: SourceView) -> dict[int, int]:
    return {
        sound.value: unit.id.value
        for unit in view.units
        for sound in unit.owned_sound_ids
    }


def _sounding(view: SourceView) -> list[bool]:
    return [
        bool(unit.owned_sound_ids or unit.presented_sound_ids)
        for unit in view.units
    ]


def _bind(view: SourceView, owner: dict[int, int], merge: _Merge) -> None:
    """A presenter co-highlights with the owner it shares a sound with, and a
    seen/saad pair with the base it rides."""
    for unit in view.units:
        for sound in unit.presented_sound_ids:
            if sound.value in owner:
                merge.union(unit.id.value, owner[sound.value])
        if unit.written_on_unit_id is not None:
            merge.union(unit.id.value, unit.written_on_unit_id.value)


def _has_owner(view: SourceView, merge: _Merge) -> list[bool]:
    roots = [False] * len(view.units)
    for unit in view.units:
        if unit.owned_sound_ids:
            roots[merge.find(unit.id.value)] = True
    return roots


def _predecessor_sounds(view: SourceView, sounding: list[bool], index: int) -> bool:
    word = view.units[index].word_id
    cursor = index - 1
    while cursor >= 0 and view.units[cursor].word_id == word:
        if sounding[cursor]:
            return True
        cursor -= 1
    return False


def _nearest(sounding: list[bool], index: int, step: int) -> int | None:
    cursor = index + step
    while 0 <= cursor < len(sounding):
        if sounding[cursor]:
            return cursor
        cursor += step
    return None


def _direction(unit, has_predecessor: bool, iltiqa: bool) -> int:
    """+1 folds forward, -1 folds back. A soundless mark and a trailing silent
    letter fold back; a word-start elision and an iltiqa carrier fold forward."""
    if unit.silence is None:
        return -1
    if not has_predecessor or iltiqa:
        return 1
    return -1


def _fold(
    view: SourceView, bundle: AnalysisBundle, sounding: list[bool], merge: _Merge
) -> None:
    rule_of = {occ.id.value: occ.rule_id.value for occ in bundle.rule_occurrences}
    has_owner = _has_owner(view, merge)
    for index, unit in enumerate(view.units):
        if has_owner[merge.find(index)]:
            continue
        iltiqa = (
            isinstance(unit.silence, ids.OccurrenceId)
            and rule_of.get(unit.silence.value) == Rule.ILTIQA_SHORTENING.value
        )
        step = _direction(
            unit, _predecessor_sounds(view, sounding, index), iltiqa
        )
        target = _nearest(sounding, index, step)
        if target is None:
            target = _nearest(sounding, index, -step)
        if target is not None:
            merge.union(index, target)
            has_owner[merge.find(index)] = True


def _coalesce(indices: list[int]) -> tuple[tuple[int, int], ...]:
    spans: list[list[int]] = []
    for value in sorted(indices):
        if spans and spans[-1][1] == value:
            spans[-1][1] = value + 1
        else:
            spans.append([value, value + 1])
    return tuple((lo, hi) for lo, hi in spans)


def _assemble(view: SourceView, merge: _Merge) -> tuple[HighlightGroup, ...]:
    members: dict[int, list[int]] = defaultdict(list)
    for index in range(len(view.units)):
        members[merge.find(index)].append(index)

    drafts: list[tuple[list[int], list[int], list[int]]] = []
    for group in members.values():
        units = sorted(group)
        sounds = sorted(
            s.value for u in units for s in view.units[u].owned_sound_ids
        )
        chars = [c.value for u in units for c in view.units[u].character_ids]
        drafts.append((sounds, units, chars))

    drafts.sort(key=lambda draft: draft[0][0])
    return tuple(
        HighlightGroup(
            id=ids.HighlightId(order),
            unit_ids=tuple(ids.LetterUnitId(u) for u in units),
            ranges=_coalesce(chars),
            sound_ids=tuple(ids.SoundId(s) for s in sounds),
        )
        for order, (sounds, units, chars) in enumerate(drafts)
    )


def highlight_groups(
    view: SourceView, bundle: AnalysisBundle
) -> tuple[HighlightGroup, ...]:
    """The ordered, validated highlight groups for one source view."""
    merge = _Merge(len(view.units))
    owner = _owner_of(view)
    sounding = _sounding(view)
    _bind(view, owner, merge)
    _fold(view, bundle, sounding, merge)
    groups = _assemble(view, merge)
    validate_highlight_groups(groups, view, bundle)
    return groups


__all__ = ["highlight_groups"]
