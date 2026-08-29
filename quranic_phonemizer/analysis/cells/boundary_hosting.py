"""Move performed boundary vowels from word cells into boundary cells."""
from __future__ import annotations

from dataclasses import replace

from ...model.canon import Quality, Rule
from ...model.performance import Aspect, Vowel
from ...orthography.write import Pen
from ..ids import CellColumnId, OccurrenceId, SoundId
from .dtos import CellColumn, CellRole, CellSide, CellStatus, CellTier

_VOWEL_ROLE = {Quality.A: "fatha", Quality.U: "damma", Quality.I: "kasra"}


def _boundary_column(new_id, owner, sound, occurrence, value, pen: Pen):
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
        and facts.occurrences[edge.by].rule is Rule.ILTIQA_HARAKA
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


def move_boundary_sounds(words, boundaries, facts, bundle, pen: Pen):
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
        column = _boundary_column(
            next_id, owner, edge.sound, edge.by, facts.sounds[edge.sound].value, pen
        )
        next_id += 1
        words = tuple(
            _remove_boundary_sound(w, owner, edge)
            if owner in w.columns else w
            for w in words
        )
        boundary_id = boundary_of[edge.by]
        boundaries = tuple(replace(b,
            columns=(*b.columns, column),
            sounds=(*b.sounds, replace(cell, column_ids=(column.id,))),
        ) if b.boundary_id == boundary_id else b for b in boundaries)
    return words, boundaries


__all__ = ["move_boundary_sounds"]
