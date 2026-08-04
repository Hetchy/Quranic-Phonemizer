"""Drafts to a frozen `Score`, and the digest that names it."""
from __future__ import annotations

import hashlib

from ..model.address import SlotId
from ..model.canon import Score, ScoreWord, Slot
from ..orthography.adapter import Reading


def assemble(
    reading: Reading, drafts, selection,
) -> tuple[Score, dict[int, int]]:
    by_word: dict[int, list[Slot]] = {}
    ordinals: dict[int, int] = {}
    sakt: set[int] = set()
    for ordinal, draft in enumerate(drafts):
        ordinals[draft.uid] = ordinal
        word = reading.clusters[draft.cluster].word if draft.cluster >= 0 else 0
        by_word.setdefault(word, []).append(_slot(reading, draft, ordinal))
        if draft.sakt_after:
            sakt.add(word)

    words = tuple(
        ScoreWord(
            location=location,
            slots=tuple(by_word.get(index, ())),
            sakt_after=index in sakt,
        )
        for index, location in enumerate(reading.words)
    )
    return Score(
        riwayah=reading.riwayah,
        words=words,
        selection=selection,
        digest=digest(words),
    ), ordinals


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
    text = "|".join(_line(word) for word in words)
    return hashlib.blake2b(text.encode("utf-8"), digest_size=16).hexdigest()


def _line(word: ScoreWord) -> str:
    return f"{word.location}/{int(word.sakt_after)}/" + "|".join(
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
