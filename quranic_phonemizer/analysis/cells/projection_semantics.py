"""Semantic relations retained when a reading drops their performed sound."""
from __future__ import annotations

from dataclasses import replace

from ...model.performance import Vowel
from ...orthography.write import Pen
from ..attributions import Recoloured
from ..facts import AnalysisFacts
from ..ids import OccurrenceId
from .dtos import CellRole, CellStatus, CellTier, CellWord

_IQLAB_MEEM = frozenset({"ۢ", "ۭ"})
_CARRIER_IDENTITIES = frozenset({
    "ibdal_hamza",
    "imala",
    "pausal_alif",
    "taqlil",
})


def is_carrier_identity_rule(rule: str) -> bool:
    return rule in _CARRIER_IDENTITIES or rule.startswith("madd_")


def _has_rule(column, rule: str, facts: AnalysisFacts) -> bool:
    return any(
        facts.occurrences[occurrence.value].rule.value == rule
        for occurrence in column.rule_occurrence_ids
    )


def _occurrence_for(column, rule: str, facts: AnalysisFacts) -> OccurrenceId | None:
    candidates = list(column.rule_occurrence_ids)
    if isinstance(column.silence, OccurrenceId):
        candidates.append(column.silence)
    return next((
        occurrence for occurrence in candidates
        if facts.occurrences[occurrence.value].rule.value == rule
    ), None)


def _with_occurrence(column, occurrence: OccurrenceId):
    return replace(column, rule_occurrence_ids=tuple(dict.fromkeys(
        (*column.rule_occurrence_ids, occurrence)
    )))


def preserve_semantic_cells(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Keep semantic silence and dropped vowel units explicit in the wire."""
    out = []
    for word in words:
        columns = list(word.columns)
        for at, column in enumerate(columns):
            if (
                _has_rule(column, "lam_shamsiyyah", facts)
                and not column.owned_sound_ids and column.presented_sound_ids
            ):
                occurrence = next(
                    one for one in column.rule_occurrence_ids
                    if facts.occurrences[one.value].rule.value == "lam_shamsiyyah"
                )
                columns[at] = replace(
                    column,
                    rule_occurrence_ids=(occurrence,),
                    silence=occurrence,
                )
                continue
            occurrence = _occurrence_for(column, "waqf_silah_drop", facts)
            if occurrence is None:
                continue
            if (
                column.silence == occurrence
                and column.role is not CellRole.HARAKA
            ):
                columns[at] = replace(
                    _with_occurrence(column, occurrence), role=CellRole.MADD
                )
                continue
            carrier_at = next((
                index for index in range(at + 1, len(columns))
                if columns[index].tier is CellTier.MAIN
                and columns[index].status is CellStatus.DROPPED
                and columns[index].silence == occurrence
            ), None)
            if carrier_at is None:
                continue
            carrier = replace(
                _with_occurrence(columns[carrier_at], occurrence),
                role=CellRole.MADD,
            )
            columns[at] = replace(column, attached_to_column_id=carrier.id)
            columns[carrier_at] = carrier
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def separate_tanween_vowel_colours(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Keep vowel colouring on the sound, not the composite tanween glyph."""
    vowel_colours = {
        OccurrenceId(modifier.by)
        for modifier in facts.modifiers
        if isinstance(modifier, Recoloured)
        and isinstance(facts.sounds[modifier.sound].value, Vowel)
    }
    if not vowel_colours:
        return words
    out = []
    for word in words:
        native_iqlab_hosts = {
            column.attached_to_column_id
            for column in word.columns
            if column.source_character_ids
            and column.text in _IQLAB_MEEM
            and _has_rule(column, "iqlab", facts)
        }
        out.append(replace(word, columns=tuple(
            replace(column, rule_occurrence_ids=tuple(
                occurrence for occurrence in column.rule_occurrence_ids
                if occurrence not in vowel_colours
            )) if (
                column.role is CellRole.TANWEEN
                and column.attached_to_column_id not in native_iqlab_hosts
            ) else column
            for column in word.columns
        )))
    return tuple(out)


def _native_meem_host(meem, columns, by_id, facts):
    if (
        not meem.source_character_ids
        or meem.text not in _IQLAB_MEEM
        or meem.attached_to_column_id is None
        or meem.owned_sound_ids
    ):
        return None
    attached = meem.attached_to_column_id
    candidates = (
        [by_id[attached]] if attached in by_id else []
    ) + [
        at for at, column in enumerate(columns)
        if column.id != meem.id and column.attached_to_column_id == attached
    ]
    return next(
        (
            at for at in candidates
            if _has_rule(columns[at], "iqlab", facts)
        ),
        None,
    )


def assign_native_iqlab_meem(words: tuple[CellWord, ...], facts: AnalysisFacts,
                             riwayah: str,
                             source=None) -> tuple[CellWord, ...]:
    """Give a written iqlab meem the sound instead of duplicating it."""
    if riwayah != "warsh":
        return words
    out = []
    for word in words:
        columns = list(word.columns)
        sounds = list(word.sounds)
        by_id = {column.id: at for at, column in enumerate(columns)}
        for at, meem in enumerate(columns):
            host_at = _native_meem_host(meem, columns, by_id, facts)
            if host_at is None:
                continue
            host = columns[host_at]
            occurrence_ids = tuple(
                occurrence for occurrence in host.rule_occurrence_ids
                if facts.occurrences[occurrence.value].rule.value == "iqlab"
            )
            if not occurrence_ids:
                continue
            moved_ids = {
                cell.sound_id for cell in sounds
                if any(
                    occurrence in occurrence_ids
                    for occurrence in cell.rule_occurrence_ids
                )
            }
            moved = tuple(
                sound for sound in host.owned_sound_ids if sound in moved_ids
            )
            if not moved:
                continue
            occurrence = occurrence_ids[0]
            remaining = tuple(
                sound for sound in host.owned_sound_ids if sound not in moved
            )
            written = (
                "".join(
                    source.units[uid.value].text
                    for uid in host.source_unit_ids
                )
                if source is not None and not remaining
                else host.text
            )
            columns[host_at] = replace(
                host,
                text=written,
                status=(host.status if remaining else CellStatus.DROPPED),
                rule_occurrence_ids=tuple(
                    item for item in host.rule_occurrence_ids
                    if item not in occurrence_ids
                ),
                silence=None if remaining else occurrence,
                owned_sound_ids=remaining,
            )
            columns[at] = replace(
                meem,
                status=CellStatus.PRESENT,
                silence=None,
                rule_occurrence_ids=occurrence_ids,
                owned_sound_ids=moved,
            )
            sounds = [
                replace(cell, column_ids=tuple(
                    meem.id if column == host.id else column
                    for column in cell.column_ids
                )) if cell.sound_id in moved else cell
                for cell in sounds
            ]
        out.append(replace(word, columns=tuple(columns), sounds=tuple(sounds)))
    return tuple(out)


def keep_madd_rules_on_carriers(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Name a performed madd on its carrier rather than its vowel mark."""
    out = []
    for word in words:
        carrier_rules = {
            occurrence
            for column in word.columns if column.role is CellRole.MADD
            for occurrence in column.rule_occurrence_ids
            if facts.occurrences[occurrence.value].rule.value.startswith("madd_")
        }
        out.append(replace(word, columns=tuple(
            replace(column, rule_occurrence_ids=tuple(
                occurrence for occurrence in column.rule_occurrence_ids
                if occurrence not in carrier_rules
            )) if column.role is not CellRole.MADD else column
            for column in word.columns
        )))
    return tuple(out)


def keep_waqf_drop_on_silenced_cells(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """A waqf vowel drop labels only the written cell it silences."""
    drops = {
        OccurrenceId(index)
        for index, occurrence in enumerate(facts.occurrences)
        if occurrence.rule.value == "waqf_diacritic_drop"
    }
    return tuple(replace(word, columns=tuple(
        replace(column, rule_occurrence_ids=tuple(
            occurrence for occurrence in column.rule_occurrence_ids
            if occurrence not in drops or column.silence == occurrence
        ))
        for column in word.columns
    )) for word in words)


def keep_ibdal_off_harakas(
    words: tuple[CellWord, ...], facts: AnalysisFacts, pen: Pen | None
) -> tuple[CellWord, ...]:
    """Place ibdal identity on its replacement letter or carrier cell."""
    ibdal = {
        OccurrenceId(index)
        for index, occurrence in enumerate(facts.occurrences)
        if occurrence.rule.value == "ibdal_hamza"
    }
    if not ibdal:
        return words
    sounds_by_occurrence: dict[OccurrenceId, set] = {}
    for edge in facts.attributions:
        if edge.by is not None:
            occurrence = OccurrenceId(edge.by)
            if occurrence in ibdal and hasattr(edge, "sound"):
                sounds_by_occurrence.setdefault(occurrence, set()).add(
                    edge.sound
                )
    for modifier in facts.modifiers:
        occurrence = OccurrenceId(modifier.by)
        if occurrence in ibdal:
            sounds_by_occurrence.setdefault(occurrence, set()).add(
                modifier.sound
            )
    out = []
    for word in words:
        columns = []
        for column in word.columns:
            column = replace(column, rule_occurrence_ids=tuple(
                occurrence for occurrence in column.rule_occurrence_ids
                if occurrence not in ibdal
                or bool(
                    {sound.value for sound in column.owned_sound_ids}
                    & sounds_by_occurrence.get(occurrence, set())
                )
                or column.silence == occurrence
            ))
            if (
                column.role is CellRole.MADD
                and pen is not None
                and ibdal.intersection(column.rule_occurrence_ids)
                and column.owned_sound_ids
            ):
                value = facts.sounds[column.owned_sound_ids[0].value].value
                if isinstance(value, Vowel) and value.long:
                    text = pen.performed_carrier(value.quality)[1]
                    if column.text != text:
                        column = replace(
                            column, text=text, status=CellStatus.REPLACED
                        )
            columns.append(column)
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def keep_taqlil_on_carriers(
    words: tuple[CellWord, ...], facts: AnalysisFacts
) -> tuple[CellWord, ...]:
    """Taqlil names its written carrier, never the preceding fatha cell."""
    out = []
    for word in words:
        carrier_rules = {
            occurrence
            for column in word.columns if column.role is CellRole.MADD
            for occurrence in column.rule_occurrence_ids
            if facts.occurrences[occurrence.value].rule.value == "taqlil"
        }
        out.append(replace(word, columns=tuple(
            replace(column, rule_occurrence_ids=tuple(
                occurrence for occurrence in column.rule_occurrence_ids
                if occurrence not in carrier_rules
            )) if column.role is not CellRole.MADD else column
            for column in word.columns
        )))
    return tuple(out)


def keep_pausal_alif_on_carriers(
    words: tuple[CellWord, ...], facts: AnalysisFacts, slot_of_unit,
) -> tuple[CellWord, ...]:
    """Keep pausal-alif identity on its written alif in every boundary state."""
    pausal = {
        OccurrenceId(index)
        for index, occurrence in enumerate(facts.occurrences)
        if occurrence.rule.value == "pausal_alif"
    }
    out = []
    for word in words:
        columns = list(word.columns)
        for occurrence in pausal:
            subjects = set(facts.occurrences[occurrence.value].subjects)
            target = next((
                at for at, column in enumerate(columns)
                if column.silence == occurrence
            ), None)
            if target is None:
                target = next((
                    at for at, column in enumerate(columns)
                    if column.text.startswith("ا")
                    and any(
                        slot_of_unit.get(unit.value) in subjects
                        for unit in column.source_unit_ids
                    )
                ), None)
            if target is None:
                continue
            columns = [
                replace(column, rule_occurrence_ids=tuple(
                    item for item in column.rule_occurrence_ids
                    if item != occurrence
                ))
                for column in columns
            ]
            carrier = columns[target]
            columns[target] = replace(
                carrier,
                role=CellRole.MADD,
                rule_occurrence_ids=tuple(dict.fromkeys(
                    (*carrier.rule_occurrence_ids, occurrence)
                )),
            )
        out.append(replace(word, columns=tuple(columns)))
    return tuple(out)


def keep_carrier_identity_off_harakas(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    """A carrier identity never decorates its accompanying short-vowel cell."""
    return tuple(replace(word, columns=tuple(
        replace(column, rule_occurrence_ids=tuple(
            occurrence for occurrence in column.rule_occurrence_ids
            if not is_carrier_identity_rule(
                facts.occurrences[occurrence.value].rule.value
            )
        )) if column.role is CellRole.HARAKA else column
        for column in word.columns
    )) for word in words)


__all__ = [
    "assign_native_iqlab_meem", "is_carrier_identity_rule", "keep_carrier_identity_off_harakas",
    "keep_ibdal_off_harakas", "keep_madd_rules_on_carriers", "keep_pausal_alif_on_carriers",
    "keep_taqlil_on_carriers", "keep_waqf_drop_on_silenced_cells", "preserve_semantic_cells", "separate_tanween_vowel_colours",
]
