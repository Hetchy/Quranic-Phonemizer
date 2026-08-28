"""Corpus-wide parity with the frozen legacy snapshots, as a floor.

A ratchet, not an equality: fix the engine, the rate rises, raise the
number. It may only ever go up.
"""
from __future__ import annotations

import gzip
import json
import pathlib

import pytest

from quranic_phonemizer.api import alphabet as load_alphabet
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.phonemize.legacy_views import phonemes_by_word
from tools.parity import (
    _moved_across_a_seam,
    _same_sequence,
    plan_for,
    units,
)

pytestmark = pytest.mark.audit

SNAPSHOTS = (
    pathlib.Path(__file__).resolve().parents[1] / "snapshots" / "phonemes"
)

#: Measured against the current engine, then pinned. The first number is
#: word-for-word equality; the second also credits a word whose only
#: difference is which side of a shared seam a merged sound landed on.
FLOORS = {
    "word": (0.9992, 0.9992),
    "verse": (0.9767, 0.9982),
    "continuous": (0.9742, 0.9955),
}


def _stretches(hafs, mode: str):
    """A surah at a time for `continuous`, else whatever the tool reads.

    `read` takes the words it is given, so a surah is one reading and a
    rule crosses the verse seams inside it.
    """
    if mode != "continuous":
        yield from units(hafs, mode)
        return
    for surah in range(1, 115):
        verses = [
            VerseRef(surah, ayah)
            for ayah in range(1, len(hafs.corpus.surah_info[str(surah)]) + 1)
        ]
        yield verses[0], tuple(
            word for verse in verses for word in hafs.words(verse)
        )


def _rates(mode: str) -> tuple[float, float]:
    hafs, alphabet = recitation(Riwayah.HAFS), load_alphabet()
    matched = bucketed = total = 0
    with gzip.open(
        SNAPSHOTS / f"{mode}.jsonl.gz", "rt", encoding="utf-8"
    ) as handle:
        expected = (json.loads(line) for line in handle)
        for verse, source in _stretches(hafs, mode):
            score = hafs.build(hafs.read(Script.UTHMANI, verse, source)).score
            performance = hafs.perform(
                score, plan_for(mode, len(score.words))
            )
            got = [
                list(word)
                for word in phonemes_by_word(performance, score, alphabet)
            ]
            want = [next(expected) for _ in got]
            wrong = [
                index
                for index, (left, right) in enumerate(zip(got, want))
                if left != right
            ]
            whole = _same_sequence(got, want)
            total += len(got)
            matched += len(got) - len(wrong)
            bucketed += sum(
                1 for index in wrong
                if whole or _moved_across_a_seam(got, want, index)
            )
    return matched / total, (matched + bucketed) / total


def _assert_floor(mode: str) -> None:
    exact, sequence = _rates(mode)
    floor, sequence_floor = FLOORS[mode]
    assert exact >= floor, f"{mode} word parity fell to {exact}"
    assert sequence >= sequence_floor, (
        f"{mode} phoneme parity fell to {sequence}"
    )


@pytest.mark.slow
def test_a_stop_after_every_word_holds_its_parity_floor():
    _assert_floor("word")


@pytest.mark.slow
def test_a_verse_joined_throughout_holds_its_parity_floor():
    _assert_floor("verse")


@pytest.mark.slow
def test_a_surah_read_as_one_reading_holds_its_parity_floor():
    _assert_floor("continuous")
