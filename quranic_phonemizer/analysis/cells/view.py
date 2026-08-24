"""Nest the source cell words and their between-word boundaries into one view.

Each internal boundary carries a stop-sign pause column and, for a cross-word
merger, a bridge that holds the shared sound; that sound leaves the host word.
"""
from __future__ import annotations

from dataclasses import replace

from ...render.alphabet import packaged_alphabet
from ...model.inscription import StopAdvice
from ...model.performance import Aspect, Vowel
from ...model.canon import Quality
from ...session import Session
from ..build import build_bundle
from ..dtos import Boundary, Merger
from ..facts import analyse
from ..ids import CellColumnId, OccurrenceId, SoundId
from ..inscription import inscribe
from ..source import build_source_view
from ..source_dtos import Character, CharacterKind, MergerPlacement, SourceView
from ...orthography.write import Pen
from .align import next_column_id
from .columns import build_cell_words
from .laws import CellValidationError
from .dtos import (
    CellBoundary,
    CellBridge,
    CellColumn,
    CellRole,
    CellSide,
    CellStatus,
    CellTier,
    CellSound,
    CellView,
    CellWord,
)
from .transform import transform_words
from .projection import project_words
from .projection_semantics import separate_tanween_vowel_colours
from .transform_laws import validate_transformed
from .view_laws import validate_cell_view


def _column_of_unit(words: tuple[CellWord, ...]) -> dict[int, CellColumnId]:
    return {
        unit.value: col.id
        for word in words for col in word.columns for unit in col.source_unit_ids
    }


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
    remaining = {
        w.word_id.value: {s.sound_id for s in held[w.word_id.value]}
        for w in words
    }
    out = tuple(replace(
        w, sounds=tuple(held[w.word_id.value]),
        groups=tuple(replace(g, sound_ids=tuple(
            s for s in g.sound_ids if s in remaining[w.word_id.value]
        )) for g in w.groups),
    ) for w in words)
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
    verse_ends: frozenset[str] | None,
) -> tuple[CellBoundary, ...]:
    bridges: dict[int, list[CellBridge]] = {}
    for merger in bundle.mergers:
        if merger.boundary_id is None:
            continue
        bridges.setdefault(merger.boundary_id.value, []).append(
            _bridge(merger, placement_of[merger.id.value], column_of_unit,
                    shared[merger.id.value])
        )
    exclusive = _exclusive_groups(bundle.boundaries)
    words = {word.id.value: word for word in bundle.words}
    out: list[CellBoundary] = []
    for boundary in bundle.boundaries:
        if boundary.before is None:
            continue
        column = _stop_sign_column(_boundary_signs(boundary, source), next_id)
        next_id += 1
        out.append(CellBoundary(
            boundary_id=boundary.id,
            columns=(column,),
            bridges=tuple(bridges.get(boundary.id.value, ())),
            state=boundary.state,
            verse_end=_verse_end(boundary, words, verse_ends),
            exclusive_group=exclusive.get(boundary.id.value),
        ))
    return tuple(out)


def _word_bridges(
    words: tuple[CellWord, ...], mergers: tuple[Merger, ...],
    shared: dict[int, CellSound],
) -> tuple[CellWord, ...]:
    words_by_id = {word.word_id.value: word for word in words}
    by_word: dict[int, list[CellBridge]] = {}
    for merger in mergers:
        if merger.boundary_id is not None:
            continue
        word = words_by_id[merger.before_word_id.value]
        before = tuple(
            column.id for column in word.columns
            if merger.sound_id in column.presented_sound_ids
        )
        after = tuple(
            column.id for column in word.columns
            if merger.sound_id in column.owned_sound_ids
        )
        by_word.setdefault(merger.before_word_id.value, []).append(
            CellBridge(
                merger_id=merger.id, before_column_ids=before,
                after_column_ids=after,
                sound=replace(
                    shared[merger.id.value], column_ids=(*before, *after)
                ),
            )
        )
    return tuple(replace(
        word, bridges=tuple(by_word.get(word.word_id.value, ()))
    ) for word in words)


def _ayah(ref: str) -> int:
    return int(ref.split(":", 2)[1])


def _verse_end(
    boundary: Boundary, words, verse_ends: frozenset[str] | None
) -> int | None:
    if boundary.before is None:
        return None
    before = words[boundary.before.value]
    if boundary.after is None:
        return (
            _ayah(before.ref)
            if verse_ends is None or before.ref in verse_ends
            else None
        )
    after = words[boundary.after.value]
    return _ayah(before.ref) if _ayah(before.ref) != _ayah(after.ref) else None


def _exclusive_groups(boundaries: tuple[Boundary, ...]) -> dict[int, int]:
    pending = None
    group = 0
    out: dict[int, int] = {}
    for boundary in boundaries:
        if boundary.stop_advice is not StopAdvice.EITHER_STOP:
            continue
        if pending is None:
            pending = boundary.id.value
            continue
        out[pending] = group
        out[boundary.id.value] = group
        pending = None
        group += 1
    return out


_VOWEL_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}


def _boundary_column(new_id, owner, sound, occurrence, value, pen):
    anchor = owner.source_unit_ids[0] if owner.source_unit_ids else owner.anchor_unit_id
    return CellColumn(
        id=CellColumnId(new_id), role=CellRole.HARAKA,
        text=pen.role(_VOWEL_ROLE[value.quality]),
        source_character_ids=(), source_unit_ids=(),
        tier=CellTier.BELOW if value.quality is Quality.I else CellTier.ABOVE,
        attached_to_column_id=None, status=CellStatus.INSERTED,
        rule_occurrence_ids=(OccurrenceId(occurrence),), silence=None,
        variant_id=None, variant_choice=None, owned_sound_ids=(SoundId(sound),),
        presented_sound_ids=(), anchor_unit_id=anchor, side=CellSide.AFTER,
    )


def _boundary_hosted(facts, bundle):
    boundary_of = {
        occ.id.value: occ.boundary_ids[0]
        for occ in bundle.rule_occurrences if occ.boundary_ids
    }
    boundaries = {b.id: b for b in bundle.boundaries}
    return [
        edge for edge in facts.hosts
        if edge.by in boundary_of and edge.aspect is Aspect.VOWEL
        and isinstance(facts.sounds[edge.sound].value, Vowel)
        and not facts.sounds[edge.sound].value.long
        and boundaries[boundary_of[edge.by]].before is not None
        and facts.word_of_slot[edge.slots[0].ordinal]
            == boundaries[boundary_of[edge.by]].before.value
    ], boundary_of


def _remove_boundary_sound(word, owner, edge):
    drop_owner = (
        owner.status is CellStatus.INSERTED
        and not owner.source_character_ids
        and not owner.source_unit_ids
        and owner.owned_sound_ids == (SoundId(edge.sound),)
    )
    columns = tuple(
        replace(c,
            owned_sound_ids=tuple(
                s for s in c.owned_sound_ids if s.value != edge.sound
            ),
            presented_sound_ids=tuple(
                s for s in c.presented_sound_ids if s.value != edge.sound
            ),
            rule_occurrence_ids=tuple(
                o for o in c.rule_occurrence_ids if o.value != edge.by
            ),
        )
        for c in word.columns if not (drop_owner and c.id == owner.id)
    )
    groups = tuple(
        replace(group,
            column_ids=(
                tuple(c for c in group.column_ids if c != owner.id)
                if drop_owner else group.column_ids
            ),
            sound_ids=tuple(
                s for s in group.sound_ids if s.value != edge.sound
            ),
        )
        for group in word.groups
        if not drop_owner or group.column_ids != (owner.id,)
    )
    runs = tuple(
        replace(run, column_ids=tuple(c for c in run.column_ids if c != owner.id))
        if drop_owner else run
        for run in word.runs
    )
    return replace(
        word, columns=columns,
        sounds=tuple(s for s in word.sounds if s.sound_id.value != edge.sound),
        groups=groups, runs=runs,
    )


def _move_boundary_sounds(words, boundaries, facts, bundle, pen):
    hosted, boundary_of = _boundary_hosted(facts, bundle)
    next_id = 1 + max(
        c.id.value
        for c in (
            *(c for w in words for c in w.columns),
            *(c for b in boundaries for c in b.columns),
        )
    )
    for edge in hosted:
        owner = next(c for w in words for c in w.columns
                     if SoundId(edge.sound) in c.owned_sound_ids)
        cell = next(c for w in words for c in w.sounds
                    if c.sound_id.value == edge.sound)
        boundary_id = boundary_of[edge.by]
        column = _boundary_column(
            next_id, owner, edge.sound, edge.by, facts.sounds[edge.sound].value, pen
        )
        next_id += 1
        words = tuple(
            _remove_boundary_sound(w, owner, edge)
            if owner in w.columns else w
            for w in words
        )
        boundaries = tuple(replace(b,
            columns=(*b.columns, column),
            sounds=(*b.sounds, replace(cell, column_ids=(column.id,))),
        ) if b.boundary_id == boundary_id else b for b in boundaries)
    return words, boundaries


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
    bundle = build_bundle(
        session, ref=ref, riwayah=riwayah, script=script, variant=variant,
        extra_phonemes=extra_phonemes, facts=facts, insc=insc,
    )
    source = build_source_view(session, bundle=bundle, facts=facts, insc=insc)
    words = build_cell_words(
        session, bundle=bundle, view=source, facts=facts, insc=insc,
        pen=pen if spelling == "transformed" else None,
    )
    if spelling == "transformed":
        if pen is None:
            raise ValueError("the transformed spelling needs a pen")
        words = transform_words(
            words, session, source, pen, extra_phonemes=extra_phonemes,
            facts=facts, insc=insc,
        )
        words = project_words(words, facts, source, insc, pen)
    words = separate_tanween_vowel_colours(words, facts)
    placement_of = {p.merger_id.value: p for p in source.merger_placements}
    column_of_unit = _column_of_unit(words)
    words, shared = _extract_merger_sounds(words, bundle.mergers)
    words = _word_bridges(words, bundle.mergers, shared)
    boundaries = _boundaries(
        bundle,
        source,
        placement_of,
        column_of_unit,
        shared,
        next_column_id(words),
        (
            None
            if session.verse_ends is None
            else frozenset(str(location) for location in session.verse_ends)
        ),
    )
    if spelling == "transformed":
        words, boundaries = _move_boundary_sounds(
            words, boundaries, facts, bundle, pen
        )
    view = CellView(words=words, boundaries=boundaries)
    validate_cell_view(view, bundle, source)
    if spelling == "transformed":
        validate_transformed(view, source, session.performance.selection)
    return view


__all__ = ["build_cell_view"]
