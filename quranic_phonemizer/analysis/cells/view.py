"""Nest the source cell words and their between-word boundaries into one view.

Each internal boundary carries a stop-sign pause column and, for a cross-word
merger, a bridge that holds the shared sound; that sound leaves the host word.
"""
from __future__ import annotations

from dataclasses import replace

from ...render.alphabet import packaged_alphabet
from ...session import Session
from ..build import build_bundle
from ..dtos import Boundary, Merger
from ..facts import analyse
from ..ids import CellColumnId
from ..inscription import inscribe
from ..source import build_source_view
from ..source_dtos import Character, CharacterKind, MergerPlacement, SourceView
from ...orthography.write import Pen
from .columns import build_cell_words
from .laws import CellValidationError
from .dtos import (
    CellBoundary,
    CellBridge,
    CellColumn,
    CellRole,
    CellStatus,
    CellTier,
    CellSound,
    CellView,
    CellWord,
)
from .transform import transform_words
from .transform_laws import validate_transformed
from .view_laws import validate_cell_view


def _column_of_unit(words: tuple[CellWord, ...]) -> dict[int, CellColumnId]:
    return {
        unit.value: col.id
        for word in words for col in word.columns for unit in col.source_unit_ids
    }


def _next_id(words: tuple[CellWord, ...]) -> int:
    return 1 + max(
        (col.id.value for word in words for col in word.columns), default=-1
    )


def _extract_merger_sounds(
    words: tuple[CellWord, ...], mergers: tuple[Merger, ...]
) -> tuple[tuple[CellWord, ...], dict[int, CellSound]]:
    """Pull each merger's shared CellSound out of its host word; the sound now
    lives in the bridge and renders once between the words, not inside the host."""
    held = {word.word_id.value: list(word.sounds) for word in words}
    shared: dict[int, CellSound] = {}
    for merger in mergers:
        cells = held[merger.after_word_id.value]
        cell = next((c for c in cells if c.sound_id == merger.sound_id), None)
        if cell is None:
            raise CellValidationError(
                f"merger {merger.id.value} names sound {merger.sound_id.value} "
                f"with no cell left in its host word"
            )
        cells.remove(cell)
        shared[merger.id.value] = cell
    out = tuple(replace(w, sounds=tuple(held[w.word_id.value])) for w in words)
    return out, shared


def _bridge(
    merger: Merger,
    placement: MergerPlacement,
    column_of_unit: dict[int, CellColumnId],
    sound: CellSound,
) -> CellBridge:
    return CellBridge(
        merger_id=merger.id,
        before_column_ids=tuple(column_of_unit[u.value] for u in placement.before_unit_ids),
        after_column_ids=tuple(column_of_unit[u.value] for u in placement.after_unit_ids),
        sound=sound,
    )


def _boundary_signs(
    boundary: Boundary, source: SourceView
) -> tuple[Character, ...]:
    """Every written stop or sakt sign the source assigns to this boundary, in
    text order; a boundary may carry more than one."""
    return tuple(
        c for c in source.characters
        if c.boundary_id == boundary.id and c.kind is CharacterKind.STOP_SIGN
    )


def _stop_sign_column(
    signs: tuple[Character, ...], new_id: int
) -> CellColumn:
    return CellColumn(
        id=CellColumnId(new_id),
        role=CellRole.STOP_SIGN,
        text="".join(c.text for c in signs),
        source_character_ids=tuple(c.id for c in signs),
        source_unit_ids=(),
        tier=CellTier.MAIN,
        attached_to_column_id=None,
        status=CellStatus.PRESENT,
        rule_occurrence_ids=(),
        silence=None,
        variant_id=None,
        variant_choice=None,
        owned_sound_ids=(),
        presented_sound_ids=(),
        anchor_unit_id=None,
        side=None,
    )


def _boundaries(
    bundle,
    source: SourceView,
    placement_of: dict[int, MergerPlacement],
    column_of_unit: dict[int, CellColumnId],
    shared: dict[int, CellSound],
    next_id: int,
) -> tuple[CellBoundary, ...]:
    bridges: dict[int, list[CellBridge]] = {}
    for merger in bundle.mergers:
        bridges.setdefault(merger.boundary_id.value, []).append(
            _bridge(merger, placement_of[merger.id.value], column_of_unit,
                    shared[merger.id.value])
        )
    out: list[CellBoundary] = []
    for boundary in bundle.boundaries:
        if boundary.before is None or boundary.after is None:
            continue
        column = _stop_sign_column(_boundary_signs(boundary, source), next_id)
        next_id += 1
        out.append(CellBoundary(
            boundary_id=boundary.id,
            columns=(column,),
            bridges=tuple(bridges.get(boundary.id.value, ())),
        ))
    return tuple(out)


def build_cell_view(
    session: Session,
    *,
    ref: str,
    riwayah: str,
    script: str,
    variant: dict,
    extra_phonemes: frozenset[str] = frozenset(),
    spelling: str = "source",
    pen: Pen | None = None,
) -> CellView:
    if spelling not in ("source", "transformed"):
        raise ValueError(f"spelling must be 'source' or 'transformed', got {spelling!r}")
    facts = analyse(session, packaged_alphabet(), extra_phonemes=extra_phonemes)
    insc = inscribe(session)
    kw = dict(ref=ref, riwayah=riwayah, script=script, variant=variant,
              extra_phonemes=extra_phonemes, facts=facts, insc=insc)
    bundle = build_bundle(session, **kw)
    source = build_source_view(session, bundle=bundle, **kw)
    words = build_cell_words(session, view=source, bundle=bundle, **kw)
    if spelling == "transformed":
        if pen is None:
            raise ValueError("the transformed spelling needs a pen")
        words = transform_words(
            words, session, source, pen, extra_phonemes=extra_phonemes,
            facts=facts, insc=insc,
        )
    placement_of = {p.merger_id.value: p for p in source.merger_placements}
    column_of_unit = _column_of_unit(words)
    words, shared = _extract_merger_sounds(words, bundle.mergers)
    boundaries = _boundaries(
        bundle, source, placement_of, column_of_unit, shared, _next_id(words)
    )
    view = CellView(words=words, boundaries=boundaries)
    validate_cell_view(view, bundle, source)
    if spelling == "transformed":
        validate_transformed(view, source, session.performance.selection)
    return view


__all__ = ["build_cell_view"]
