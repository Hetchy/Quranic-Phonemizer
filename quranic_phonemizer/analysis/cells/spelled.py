"""Project muqattaat names as flat runs of ordinary cells."""
from __future__ import annotations

from dataclasses import replace

from ...model.canon import CARRIER_OF, CanonLetter, Quality
from ...model.performance import Aspect, Consonant
from ...orthography.write import Pen
from ..attributions import Hosted, Insertion, Merged
from ..dtos import AnalysisBundle
from ..facts import AnalysisFacts
from ..ids import (
    CanonicalSlotId,
    CellColumnId,
    CellRunId,
    OccurrenceId,
    SoundId,
)
from .dtos import (
    CellColumn,
    CellRole,
    CellRun,
    CellSide,
    CellSound,
    CellStatus,
    CellTier,
    CellWord,
)


def _edges(facts: AnalysisFacts, kind: type) -> dict[tuple[object, Aspect], list[int]]:
    out: dict[tuple[object, Aspect], list[int]] = {}
    for edge in facts.attributions:
        if not isinstance(edge, kind):
            continue
        slots = edge.slots if isinstance(edge, (Hosted, Merged)) else (edge.anchor[0],)
        for slot in slots:
            out.setdefault((slot, edge.aspect), []).append(edge.sound)
    return out


def _rule_ids(bundle: AnalysisBundle, sounds: tuple[int, ...]) -> tuple[OccurrenceId, ...]:
    return tuple(dict.fromkeys(
        occurrence
        for sound in sounds
        for occurrence in bundle.sounds[sound].rule_occurrence_ids
    ))


def _rule_names(bundle: AnalysisBundle, occurrences) -> frozenset[str]:
    return frozenset(
        bundle.rule_occurrences[occurrence.value].rule_id.value
        for occurrence in occurrences
    )


def _column(
    new_id: int, role: CellRole, text: str, tier: CellTier,
    slot, source_unit, *, owned=(), presented=(), attached=None,
    status=CellStatus.PRESENT, rules=(),
) -> CellColumn:
    return CellColumn(
        id=CellColumnId(new_id), role=role, text=text,
        source_character_ids=(), source_unit_ids=(), tier=tier,
        attached_to_column_id=attached, status=status,
        rule_occurrence_ids=rules, silence=None, variant_id=None,
        variant_choice=None,
        owned_sound_ids=tuple(SoundId(sound) for sound in owned),
        presented_sound_ids=tuple(SoundId(sound) for sound in presented),
        anchor_unit_id=source_unit,
        side=CellSide.AFTER if status is CellStatus.INSERTED else None,
        slot_ids=(CanonicalSlotId(str(slot.id)),),
    )


def _consonant_text(slot, sounds, facts, pen, *, merged_into: bool) -> str:
    text = (
        pen.seated_hamza(slot.nucleus.quality)
        if slot.letter is CanonLetter.HAMZA and slot.nucleus.is_short
        else pen.letter(slot.letter)
    )
    geminate = merged_into or any(
        isinstance(facts.sounds[sound].value, Consonant)
        and facts.sounds[sound].value.geminate
        for sound in sounds
    )
    return text + (pen.role("shadda") if geminate else "")


def _needs_sukun(slot, rules: frozenset[str], has_vowel: bool) -> bool:
    if not slot.nucleus.is_silent or has_vowel:
        return False
    return not any(
        rule.startswith(("idgham_", "ikhfaa")) for rule in rules
    )


def _vowel_columns(
    slot, source_unit, facts, bundle, pen, vowel, base, next_id,
) -> tuple[list[CellColumn], int]:
    if not vowel:
        return [], next_id
    quality = facts.sounds[vowel[0]].value.quality
    tier = CellTier.BELOW if quality.value == "i" else CellTier.ABOVE
    rules = _rule_ids(bundle, vowel)
    if slot.nucleus.is_short:
        return [_column(
            next_id, CellRole.HARAKA, pen.short_vowel(quality), tier,
            slot, source_unit, owned=vowel, attached=base.id, rules=rules,
        )], next_id + 1
    if not slot.nucleus.is_long:
        return [_column(
            next_id, CellRole.HARAKA, pen.short_vowel(quality), tier,
            slot, source_unit, owned=vowel, attached=base.id,
            status=CellStatus.INSERTED, rules=rules,
        )], next_id + 1
    performed = {
        Quality.KUBRA: Quality.I,
        Quality.TAQLIL: Quality.A,
    }.get(quality, quality)
    carrier_text = pen.letter(CARRIER_OF[performed])
    if "madd_lazim" in _rule_names(bundle, rules):
        carrier_text += pen.role("madd")
    carrier_id = CellColumnId(next_id + 1)
    return [
        _column(
            next_id, CellRole.HARAKA, pen.short_vowel(quality), tier,
            slot, source_unit, presented=vowel, attached=carrier_id,
        ),
        _column(
            next_id + 1, CellRole.MADD, carrier_text, CellTier.MAIN,
            slot, source_unit, owned=vowel, rules=rules,
        ),
    ], next_id + 2


def _slot_columns(
    slot, source_unit, facts, bundle, pen, hosted, merged, inserted,
    next_id: int,
) -> tuple[list[CellColumn], int]:
    consonants = tuple(hosted.get((slot.id, Aspect.CONSONANT), ()))
    presenters = tuple(merged.get((slot.id, Aspect.CONSONANT), ()))
    vowel = tuple(hosted.get((slot.id, Aspect.VOWEL), ()))
    added = tuple(inserted.get((slot.id, Aspect.VOWEL), ()))
    base_sounds = (*consonants, *presenters)
    base_rules = _rule_ids(bundle, base_sounds)
    names = _rule_names(bundle, base_rules)
    text = _consonant_text(
        slot, consonants, facts, pen,
        merged_into=bool(consonants and any(
            edge.sound in consonants for edge in facts.merges
        )),
    )
    if _needs_sukun(slot, names, bool(vowel or added)):
        text += pen.role("sukun")
    if slot.letter.value == "ya" and "madd_lazim" in names:
        text += pen.role("madd")
    base = _column(
        next_id, CellRole.LETTER, text, CellTier.MAIN, slot, source_unit,
        owned=consonants, presented=presenters, rules=base_rules,
    )
    next_id += 1
    out = [base]
    made, next_id = _vowel_columns(
        slot, source_unit, facts, bundle, pen, vowel, base, next_id
    )
    out.extend(made)
    for sound in added:
        value = facts.sounds[sound].value
        out.append(_column(
            next_id, CellRole.HARAKA, pen.short_vowel(value.quality),
            CellTier.BELOW if value.quality.value == "i" else CellTier.ABOVE,
            slot, source_unit, owned=(sound,), attached=base.id,
            status=CellStatus.INSERTED, rules=_rule_ids(bundle, (sound,)),
        ))
        next_id += 1
    return out, next_id


def _realign(
    words: tuple[CellWord, ...], bundle: AnalysisBundle,
) -> tuple[CellWord, ...]:
    """Align sound spans across the full row, including cross-word mergers."""
    spans: dict[int, list[CellColumnId]] = {}
    for word in words:
        for column in word.columns:
            for sound in (*column.owned_sound_ids, *column.presented_sound_ids):
                spans.setdefault(sound.value, []).append(column.id)
    existing = {
        cell.sound_id.value: cell
        for word in words
        for cell in word.sounds
    }
    by_word: dict[int, list[CellSound]] = {}
    for sound in bundle.sounds:
        columns = spans.get(sound.id.value)
        if columns:
            cell = CellSound(
                sound.id, tuple(columns), sound.rule_occurrence_ids
            )
        else:
            cell = existing.get(sound.id.value)
            if cell is None:
                raise ValueError(
                    f"spelled word {sound.word_id.value} leaves sound "
                    f"{sound.id.value} unaligned"
                )
        by_word.setdefault(sound.word_id.value, []).append(cell)
    return tuple(replace(
        word, sounds=tuple(by_word.get(word.word_id.value, ()))
    ) for word in words)


def expand_spelled_words(
    words: tuple[CellWord, ...], facts: AnalysisFacts,
    bundle: AnalysisBundle, score, pen: Pen,
) -> tuple[CellWord, ...]:
    """Replace compact muqattaat columns with one flat expanded cell row."""
    hosted = _edges(facts, Hosted)
    merged = _edges(facts, Merged)
    inserted = _edges(facts, Insertion)
    next_id = 1 + max(c.id.value for word in words for c in word.columns)
    next_run_id = 0
    out = []
    for word in words:
        score_word = score.words[word.word_id.value]
        if not score_word.spelling_runs:
            out.append(word)
            continue
        anchors = [
            column for column in word.columns
            if column.tier is CellTier.MAIN and column.source_unit_ids
        ]
        if len(anchors) != len(score_word.spelling_runs):
            raise ValueError(
                f"{score_word.location}: {len(anchors)} source letters for "
                f"{len(score_word.spelling_runs)} spelling runs"
            )
        columns = []
        runs = []
        slots = {slot.id: slot for slot in score_word.slots}
        for run, anchor in zip(score_word.spelling_runs, anchors, strict=True):
            run_columns = []
            for slot_id in run.slot_ids:
                made, next_id = _slot_columns(
                    slots[slot_id], anchor.source_unit_ids[0], facts, bundle,
                    pen, hosted, merged, inserted, next_id,
                )
                columns.extend(made)
                run_columns.extend(column.id for column in made)
            runs.append(CellRun(
                CellRunId(next_run_id), anchor.source_unit_ids[0],
                tuple(run_columns),
            ))
            next_run_id += 1
        out.append(replace(
            word, columns=tuple(columns), sounds=(), runs=tuple(runs)
        ))
    return _realign(tuple(out), bundle)


__all__ = ["expand_spelled_words"]
