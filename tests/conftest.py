"""Shared fixtures: building a Score and a Performance for a real verse."""
from __future__ import annotations

import pytest

from quranic_phonemizer.canon.build import build
from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.classifier import RuleSet
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import Location, Script, VerseRef
from quranic_phonemizer.riwayat.hafs import (
    corpus,
    ledger,
    lexeme_passes,
    lexicon,
    script_adapter,
)


@pytest.fixture(scope="session")
def packed():
    return corpus()


@pytest.fixture(scope="session")
def shared():
    return {"lexicon": lexicon(), "ledger": ledger(), "passes": lexeme_passes()}


@pytest.fixture(scope="session")
def alphabet():
    from pathlib import Path

    from quranic_phonemizer.render.alphabet import load_alphabet

    root = Path(__file__).resolve().parent.parent
    return load_alphabet(root / "quranic_phonemizer" / "data" / "render" / "ipa.yaml")


def words_of(packed, surah: int, ayah: int) -> tuple:
    """The verse's words, sized from `surah_info`."""
    # Probing with try/except would walk into the next verse instead of stopping.
    count = packed.surah_info[str(surah)][ayah - 1]
    return tuple(
        (Location(surah, ayah, word), packed.word(Location(surah, ayah, word)))
        for word in range(1, count + 1)
    )


def built_for(packed, shared, surah: int, ayah: int, script=Script.UTHMANI):
    reading = script_adapter(script).read(
        VerseRef(surah, ayah), words_of(packed, surah, ayah)
    )
    return build(reading, **shared)


def score_for(packed, shared, surah: int, ayah: int, script=Script.UTHMANI):
    return built_for(packed, shared, surah, ayah, script).score


def performance_for(packed, shared, surah: int, ayah: int, rules: RuleSet,
                    script=Script.UTHMANI):
    score = score_for(packed, shared, surah, ayah, script)
    return score, perform(score, rules, all_join(len(score.words)))
