"""Cell projection for a boundary long vowel made by naql plus badal."""
from __future__ import annotations

from dataclasses import replace

from ...model.performance import Vowel
from ..dtos import AnalysisBundle, Merger
from ..facts import AnalysisFacts
from ..ids import OccurrenceId, SoundId
from .dtos import CellColumn, CellRole, CellWord


_RULES = frozenset({"naql", "madd_badal"})


def _sound_rules(bundle: AnalysisBundle, sound: SoundId) -> dict[str, OccurrenceId]:
    item = bundle.sounds[sound.value]
    return {
        bundle.rule_occurrences[occurrence.value].rule_id.value: occurrence
        for occurrence in item.rule_occurrence_ids
    }


def _move_naql_presenter(
    words: list[CellWord], merger: Merger, rules: dict[str, OccurrenceId],
) -> CellColumn:
    before_at = next(
        at for at, word in enumerate(words) if word.word_id == merger.before_word_id
    )
    before = words[before_at]
    before_columns = list(before.columns)
    presenter_at = next(
        at for at, column in enumerate(before_columns)
        if merger.sound_id in column.presented_sound_ids
    )
    presenter = before_columns[presenter_at]
    satellite_at = (
        presenter_at
        if presenter.role in {CellRole.HARAKA, CellRole.TANWEEN}
        else next((
            at for at, column in enumerate(before_columns)
            if column.attached_to_column_id == presenter.id
            and column.role in {CellRole.HARAKA, CellRole.TANWEEN}
        ), presenter_at)
    )
    satellite = before_columns[satellite_at]
    semantic = set(rules.values())
    if presenter_at != satellite_at:
        before_columns[presenter_at] = replace(
            presenter,
            presented_sound_ids=tuple(
                sound for sound in presenter.presented_sound_ids
                if sound != merger.sound_id
            ),
            rule_occurrence_ids=tuple(
                occurrence for occurrence in presenter.rule_occurrence_ids
                if occurrence not in semantic
            ),
        )
    before_columns[satellite_at] = replace(
        satellite,
        presented_sound_ids=tuple(dict.fromkeys(
            (*satellite.presented_sound_ids, merger.sound_id)
        )),
        rule_occurrence_ids=tuple(dict.fromkeys(
            (*satellite.rule_occurrence_ids, rules["naql"])
        )),
    )
    words[before_at] = replace(before, columns=tuple(before_columns))
    return satellite


def _without_column(items, column_id):
    return tuple(
        changed for item in items
        if (changed := replace(
            item,
            column_ids=tuple(
                column for column in item.column_ids if column != column_id
            ),
        )).column_ids
    )


def _project_one(words: list[CellWord], merger: Merger,
                 rules: dict[str, OccurrenceId]) -> None:
    satellite = _move_naql_presenter(words, merger, rules)
    after_at = next(
        at for at, word in enumerate(words) if word.word_id == merger.after_word_id
    )
    after = words[after_at]

    after_columns = list(after.columns)
    carrier = next(
        column for column in after_columns
        if merger.sound_id in column.owned_sound_ids
    )
    witness_at = next((
        at for at, column in enumerate(after_columns)
        if merger.sound_id in column.presented_sound_ids
    ), None)
    if witness_at is None:
        words[after_at] = replace(after, sounds=tuple(
            replace(sound, column_ids=(satellite.id, carrier.id))
            if sound.sound_id == merger.sound_id else sound
            for sound in after.sounds
        ))
        return
    witness = after_columns[witness_at]
    qata_at = next(
        at for at in range(witness_at - 1, -1, -1)
        if after_columns[at].silence == rules["naql"]
    )
    qata = after_columns[qata_at]
    after_columns[qata_at] = replace(
        qata,
        text=qata.text + witness.text,
        source_character_ids=tuple(dict.fromkeys(
            (*qata.source_character_ids, *witness.source_character_ids)
        )),
        source_unit_ids=tuple(dict.fromkeys(
            (*qata.source_unit_ids, *witness.source_unit_ids)
        )),
        slot_ids=tuple(dict.fromkeys((*qata.slot_ids, *witness.slot_ids))),
        rule_occurrence_ids=tuple(dict.fromkeys(
            (*qata.rule_occurrence_ids, rules["naql"])
        )),
        presented_sound_ids=(),
    )
    del after_columns[witness_at]
    groups = _without_column(after.groups, witness.id)
    runs = _without_column(after.runs, witness.id)
    sounds = tuple(
        replace(sound, column_ids=(satellite.id, carrier.id))
        if sound.sound_id == merger.sound_id else sound
        for sound in after.sounds
    )
    words[after_at] = replace(
        after, columns=tuple(after_columns), groups=groups, runs=runs, sounds=sounds
    )


def _move_long_presenter(words: list[CellWord], merger: Merger) -> None:
    before_at = next(
        at for at, word in enumerate(words) if word.word_id == merger.before_word_id
    )
    before = words[before_at]
    columns = list(before.columns)
    presenter_at = next(
        at for at, column in enumerate(columns)
        if merger.sound_id in column.presented_sound_ids
    )
    presenter = columns[presenter_at]
    if presenter.role in {CellRole.HARAKA, CellRole.TANWEEN}:
        return
    satellite_at = next((
        at for at, column in enumerate(columns)
        if column.attached_to_column_id == presenter.id
        and column.role in {CellRole.HARAKA, CellRole.TANWEEN}
    ), None)
    if satellite_at is None:
        return
    satellite = columns[satellite_at]
    columns[presenter_at] = replace(
        presenter,
        presented_sound_ids=tuple(
            sound for sound in presenter.presented_sound_ids
            if sound != merger.sound_id
        ),
    )
    columns[satellite_at] = replace(
        satellite,
        presented_sound_ids=tuple(dict.fromkeys(
            (*satellite.presented_sound_ids, merger.sound_id)
        )),
    )
    words[before_at] = replace(before, columns=tuple(columns))
    after_at = next(
        at for at, word in enumerate(words) if word.word_id == merger.after_word_id
    )
    after = words[after_at]
    words[after_at] = replace(after, sounds=tuple(
        replace(sound, column_ids=tuple(
            satellite.id if column == presenter.id else column
            for column in sound.column_ids
        )) if sound.sound_id == merger.sound_id else sound
        for sound in after.sounds
    ))


def project_naql_badal_bridges(
    words: tuple[CellWord, ...], bundle: AnalysisBundle, facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    """Expose the written vowel and carrier as long-merger endpoints."""
    out = list(words)
    for merger in bundle.mergers:
        if merger.boundary_id is None:
            continue
        rules = _sound_rules(bundle, merger.sound_id)
        if _RULES.issubset(rules):
            _project_one(out, merger, rules)
    for merger in bundle.mergers:
        value = facts.sounds[merger.sound_id.value].value
        if (
            merger.boundary_id is not None
            and isinstance(value, Vowel) and value.long
        ):
            _move_long_presenter(out, merger)
    return tuple(out)


__all__ = ["project_naql_badal_bridges"]
