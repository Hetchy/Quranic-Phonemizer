"""Validation the nested cell view must pass before a consumer reads it.

One stop-sign column per internal boundary, every core sound in exactly one
cell, a bridge that resolves to its merger, no bridge on an iltiqa, and closure.
"""
from __future__ import annotations

from ...model.canon import ILTIQA_RULES
from ..checks import requirer
from ..dtos import AnalysisBundle
from ..source_dtos import MergerPlacement, SourceView
from .dtos import CellRole, CellSound, CellStatus, CellView
from .laws import CellValidationError

_require = requirer(CellValidationError)


def _all_columns(view: CellView) -> dict[int, object]:
    out: dict[int, object] = {}
    for word in view.words:
        for col in word.columns:
            out[col.id.value] = col
    for boundary in view.boundaries:
        for col in boundary.columns:
            out[col.id.value] = col
    return out


def _all_cells(view: CellView) -> list[CellSound]:
    cells: list[CellSound] = [c for word in view.words for c in word.sounds]
    for boundary in view.boundaries:
        cells.extend(boundary.sounds)
        cells.extend(bridge.sound for bridge in boundary.bridges)
    return cells


def _check_stop_signs(view: CellView, bundle: AnalysisBundle) -> None:
    after_words = {
        b.id.value for b in bundle.boundaries
        if b.before is not None
    }
    got = {cb.boundary_id.value for cb in view.boundaries}
    _require(got == after_words, "the cell boundaries are not the after-word boundaries")
    for cb in view.boundaries:
        signs = [c for c in cb.columns if c.role is CellRole.STOP_SIGN]
        _require(len(signs) == 1, "an internal boundary has not one stop-sign column")
        _require(
            not signs[0].owned_sound_ids and not signs[0].presented_sound_ids,
            "a stop-sign column owns a sound",
        )


def _check_one_cell_per_sound(view: CellView, bundle: AnalysisBundle) -> None:
    held: dict[int, int] = {}
    for cell in _all_cells(view):
        sid = cell.sound_id.value
        held[sid] = held.get(sid, 0) + 1
    _require(
        set(held) == {s.id.value for s in bundle.sounds},
        "the cells are not exactly the core sounds",
    )
    _require(all(n == 1 for n in held.values()), "a core sound has two cells")


def _placement_columns(
    placement: MergerPlacement, column_of_unit: dict[int, int]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    before = tuple(column_of_unit[u.value] for u in placement.before_unit_ids)
    after = tuple(column_of_unit[u.value] for u in placement.after_unit_ids)
    return before, after


def _mergers_at(bundle: AnalysisBundle) -> dict[int, set[int]]:
    out: dict[int, set[int]] = {}
    for merger in bundle.mergers:
        out.setdefault(merger.boundary_id.value, set()).add(merger.id.value)
    return out


def _check_one_bridge(
    bridge, merger, placement: MergerPlacement,
    column_of_unit: dict[int, int], rules: dict[int, object],
) -> None:
    before, after = _placement_columns(placement, column_of_unit)
    _require(bridge.sound.sound_id == merger.sound_id, "a bridge owns another sound")
    _require(
        tuple(c.value for c in bridge.before_column_ids) == before
        and tuple(c.value for c in bridge.after_column_ids) == after,
        "a bridge endpoint is not the merger's contributor and host",
    )
    _require(
        {c.value for c in bridge.sound.column_ids} == set(before + after),
        "a bridged sound spans other than its endpoint columns",
    )
    _require(
        bridge.sound.rule_occurrence_ids == rules[merger.sound_id.value],
        "a bridge sound's rules are not its sound's",
    )


def _check_bridges(
    view: CellView, bundle: AnalysisBundle, source: SourceView
) -> None:
    mergers = {m.id.value: m for m in bundle.mergers}
    placements = {p.merger_id.value: p for p in source.merger_placements}
    rules = {s.id.value: s.rule_occurrence_ids for s in bundle.sounds}
    at = _mergers_at(bundle)
    column_of_unit = {
        u.value: c.id.value
        for w in view.words for c in w.columns for u in c.source_unit_ids
    }
    for cb in view.boundaries:
        seen: set[int] = set()
        for bridge in cb.bridges:
            merger = mergers.get(bridge.merger_id.value)
            _require(merger is not None, "a bridge resolves to no merger")
            _require(merger.boundary_id == cb.boundary_id, "a bridge sits off its boundary")
            _require(bridge.merger_id.value not in seen, "a merger has two bridges")
            seen.add(bridge.merger_id.value)
            _check_one_bridge(
                bridge, merger, placements[bridge.merger_id.value],
                column_of_unit, rules,
            )
        _require(seen == at.get(cb.boundary_id.value, set()),
                 "a boundary's bridges are not its mergers")


def _iltiqa_binds(bundle: AnalysisBundle) -> tuple[set[int], set[int]]:
    """The boundaries and sounds an iltiqa occurrence binds. Its connecting vowel
    is a host word's own sound, not a merger, so neither may back a bridge."""
    boundaries: set[int] = set()
    sounds: set[int] = set()
    iltiqa = frozenset(rule.value for rule in ILTIQA_RULES)
    for occ in bundle.rule_occurrences:
        if occ.rule_id.value in iltiqa:
            boundaries.update(b.value for b in occ.boundary_ids)
            sounds.update(s.value for s in occ.sound_ids)
    return boundaries, sounds


def _check_no_iltiqa_bridge(view: CellView, bundle: AnalysisBundle) -> None:
    """An iltiqa is never a merger: its boundary carries no bridge, its host-owned
    sound backs none, and no boundary insertion column is a bridge endpoint."""
    iltiqa_boundaries, iltiqa_sounds = _iltiqa_binds(bundle)
    for cb in view.boundaries:
        inserted = {
            c.id.value for c in cb.columns if c.status is CellStatus.INSERTED
        }
        for bridge in cb.bridges:
            _require(
                cb.boundary_id.value not in iltiqa_boundaries,
                "a bridge sits on an iltiqa boundary",
            )
            _require(
                bridge.sound.sound_id.value not in iltiqa_sounds,
                "a bridge holds an iltiqa sound",
            )
            endpoints = {
                c.value for c in (*bridge.before_column_ids, *bridge.after_column_ids)
            }
            _require(
                inserted.isdisjoint(endpoints),
                "a bridge endpoint is a boundary insertion column",
            )


def _check_closure(view: CellView, bundle: AnalysisBundle) -> None:
    columns = set(_all_columns(view))
    sounds = {s.id.value for s in bundle.sounds}
    mergers = {m.id.value for m in bundle.mergers}
    for cell in _all_cells(view):
        _require(cell.sound_id.value in sounds, "a cell names an unknown sound")
        for cid in cell.column_ids:
            _require(cid.value in columns, "a cell spans an unknown column")
    for cb in view.boundaries:
        for bridge in cb.bridges:
            _require(bridge.merger_id.value in mergers, "a bridge names an unknown merger")
            for cid in (*bridge.before_column_ids, *bridge.after_column_ids):
                _require(cid.value in columns, "a bridge endpoint is an unknown column")


def _check_groups(view: CellView) -> None:
    if not any(word.groups for word in view.words):
        return
    for word in view.words:
        columns = {column.id for column in word.columns}
        sounds = {sound.sound_id for sound in word.sounds}
        claimed_columns = [item for group in word.groups for item in group.column_ids]
        claimed_sounds = [item for group in word.groups for item in group.sound_ids]
        _require(
            set(claimed_columns) == columns and len(claimed_columns) == len(columns),
            "the groups do not partition a word's columns",
        )
        _require(
            set(claimed_sounds) == sounds and len(claimed_sounds) == len(sounds),
            "the groups do not partition a word's sounds",
        )
        _require(
            all(group.key in group.column_ids for group in word.groups),
            "a group key is not one of its columns",
        )


def validate_cell_view(
    view: CellView, bundle: AnalysisBundle, source: SourceView
) -> None:
    _check_stop_signs(view, bundle)
    _check_one_cell_per_sound(view, bundle)
    _check_no_iltiqa_bridge(view, bundle)
    _check_bridges(view, bundle, source)
    _check_closure(view, bundle)
    _check_groups(view)


__all__ = ["validate_cell_view"]
