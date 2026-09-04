"""Drafts to a frozen `Score`, and the digest that names it."""
from __future__ import annotations

import hashlib

from ..model.address import SlotId, SpellingRunId
from ..model.canon import Score, ScoreWord, Slot, SpellingRun
from ..orthography.adapter import Reading


def assemble(
    reading: Reading, drafts, selection,
) -> tuple[Score, dict[int, int]]:
    by_word: dict[int, list[Slot]] = {}
    ordinals: dict[int, int] = {}
    sakt: set[int] = set()
    run_drafts: dict[int, dict[int, list]] = {}
    for ordinal, draft in enumerate(drafts):
        ordinals[draft.uid] = ordinal
        word = reading.clusters[draft.cluster].word if draft.cluster >= 0 else 0
        by_word.setdefault(word, []).append(_slot(reading, draft, ordinal))
        if draft.spelling_run is not None:
            run_drafts.setdefault(word, {}).setdefault(
                draft.spelling_run, []
            ).append((draft, ordinal))
        if draft.sakt_after:
            sakt.add(word)

    words = tuple(
        ScoreWord(
            location=location,
            slots=tuple(by_word.get(index, ())),
            sakt_after=index in sakt,
            spelling_runs=_spelling_runs(
                reading.verse, location, run_drafts.get(index, {})
            ),
        )
        for index, location in enumerate(reading.words)
    )
    return Score(
        riwayah=reading.riwayah,
        words=words,
        selection=selection,
        digest=digest(words),
    ), ordinals


def _spelling_runs(verse, location, drafts_by_run) -> tuple[SpellingRun, ...]:
    out = []
    for run, drafts in sorted(drafts_by_run.items()):
        letters = {draft.spelled_letter for draft, _ in drafts}
        if len(letters) != 1 or None in letters:
            raise ValueError(f"{location}: spelling run {run} has no single letter")
        out.append(SpellingRun(
            id=SpellingRunId(location, run),
            source_letter=next(iter(letters)),
            slot_ids=tuple(SlotId(verse, ordinal) for _, ordinal in drafts),
        ))
    return tuple(out)


def _slot(reading: Reading, draft, ordinal: int) -> Slot:
    return Slot(
        id=SlotId(reading.verse, ordinal),
        letter=draft.letter,
        onset=draft.onset,
        nucleus=draft.nucleus,
        origin=draft.origin,
        annotations=frozenset(draft.annotations),
    )


def digest(words: tuple[ScoreWord, ...]) -> str:
    """Every field two Scores may differ in, so equal digests are equal
    Scores. A digest over part of a Slot would report a lost fact as a match."""
    digest = hashlib.blake2b(digest_size=16)
    for index, word in enumerate(words):
        if index:
            digest.update(b"|")
        digest.update(_line(word).encode("utf-8"))
    return digest.hexdigest()


def _line(word: ScoreWord) -> str:
    runs = ";".join(
        f"{run.source_letter.value}:{','.join(str(slot.ordinal) for slot in run.slot_ids)}"
        for run in word.spelling_runs
    )
    return f"{word.location}/{int(word.sakt_after)}/{runs}/" + "|".join(
        f"{slot.letter.value}:{slot.onset.value}:{_nucleus(slot.nucleus)}:"
        f"{slot.origin.value}:"
        f"{','.join(sorted(a.value for a in slot.annotations))}"
        for slot in word.slots
    )


def _nucleus(nucleus) -> str:
    joined, stopped = nucleus.joined, nucleus.stopped
    return (
        f"{joined.form.value}{joined.quality.value if joined.quality else ''}"
        f">{stopped.form.value}{stopped.quality.value if stopped.quality else ''}"
    )
