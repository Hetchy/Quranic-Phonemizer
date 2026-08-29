"""Keep tafkheem and tarqeeq on their semantic sound owners."""

from __future__ import annotations

from dataclasses import replace

from ...model.canon import Quality
from ...model.performance import Vowel
from ..facts import AnalysisFacts
from ..ids import OccurrenceId
from .dtos import CellRole, CellWord

_WEIGHT_RULES = frozenset({"tafkheem", "tarqeeq"})


def keep_weight_labels_off_short_vowels(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    """Keep weight visible on a letter/carrier, never a short vowel."""
    weight = {
        OccurrenceId(index)
        for index, occurrence in enumerate(facts.occurrences)
        if occurrence.rule.value in _WEIGHT_RULES
    }
    out = []
    for word in words:
        columns = tuple(
            replace(column, rule_occurrence_ids=tuple(
                occurrence for occurrence in column.rule_occurrence_ids
                if occurrence not in weight
            )) if column.role in {CellRole.HARAKA, CellRole.TANWEEN}
            else column
            for column in word.columns
        )
        sounds = tuple(
            replace(sound, rule_occurrence_ids=tuple(
                occurrence for occurrence in sound.rule_occurrence_ids
                if occurrence not in weight
            )) if (
                isinstance(facts.sounds[sound.sound_id.value].value, Vowel)
                and not facts.sounds[sound.sound_id.value].value.long
                and facts.sounds[sound.sound_id.value].value.quality is Quality.A
            ) else sound
            for sound in word.sounds
        )
        out.append(replace(word, columns=columns, sounds=sounds))
    return tuple(out)


def keep_weight_labels_on_sound_owners(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
) -> tuple[CellWord, ...]:
    """Remove weight identity from columns that merely present its sound."""
    weight = {
        OccurrenceId(index)
        for index, occurrence in enumerate(facts.occurrences)
        if occurrence.rule.value in _WEIGHT_RULES
    }
    out = []
    for word in words:
        sounds_by_occurrence: dict[OccurrenceId, set] = {}
        for sound in word.sounds:
            for occurrence in sound.rule_occurrence_ids:
                if occurrence in weight:
                    sounds_by_occurrence.setdefault(occurrence, set()).add(
                        sound.sound_id
                    )
        columns = tuple(replace(column, rule_occurrence_ids=tuple(
            occurrence for occurrence in column.rule_occurrence_ids
            if occurrence not in weight
            or bool(
                set(column.owned_sound_ids)
                & sounds_by_occurrence.get(occurrence, set())
            )
        )) for column in word.columns)
        out.append(replace(word, columns=columns))
    return tuple(out)


__all__ = [
    "keep_weight_labels_off_short_vowels",
    "keep_weight_labels_on_sound_owners",
]
