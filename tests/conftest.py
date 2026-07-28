"""Shared fixtures: building a Score and a Performance for a real verse."""
from __future__ import annotations

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.model.address import Location, Riwayah, Script, VerseRef


@pytest.fixture(scope="session")
def hafs():
    """The whole riwayah, assembled once. Anything a test needs to build or
    perform comes from here rather than from a hand-gathered bundle."""
    return recitation(Riwayah.HAFS)


@pytest.fixture(scope="session")
def packed(hafs):
    return hafs.corpus


@pytest.fixture(scope="session")
def alphabet():
    from quranic_phonemizer.api import alphabet as load

    return load()


def words_of(packed, surah: int, ayah: int) -> tuple:
    """The verse's words, sized from `surah_info`."""
    # Probing with try/except would walk into the next verse instead of stopping.
    count = packed.surah_info[str(surah)][ayah - 1]
    return tuple(
        (Location(surah, ayah, word), packed.word(Location(surah, ayah, word)))
        for word in range(1, count + 1)
    )


@pytest.fixture(scope="session")
def sources():
    """Both scripts' editable text. The packed corpus holds only Uthmani, so
    anything comparing the two has to read from here."""
    import json
    from collections import defaultdict
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    base = root / "corpus_sources" / "riwayat" / "hafs" / "scripts"
    out: dict = {}
    for script in Script:
        raw = json.loads(
            (base / script.value / "quran.json").read_text(encoding="utf-8")
        )
        verses: dict = defaultdict(list)
        for key, record in raw.items():
            surah, ayah, word = (int(part) for part in key.split(":"))
            verses[(surah, ayah)].append(
                (Location(surah, ayah, word), record["text"])
            )
        out[script] = {
            key: tuple(sorted(words, key=lambda pair: pair[0].word))
            for key, words in verses.items()
        }
    return out


def built_for(packed, hafs, surah: int, ayah: int, script=Script.UTHMANI):
    reading = hafs.read(
        script, VerseRef(surah, ayah), words_of(packed, surah, ayah)
    )
    return hafs.build(reading)


def score_for(packed, hafs, surah: int, ayah: int, script=Script.UTHMANI):
    return built_for(packed, hafs, surah, ayah, script).score


def performance_for(packed, hafs, surah: int, ayah: int, rules=None,
                    script=Script.UTHMANI):
    """`rules` overrides the riwayah's own set, for tests that swap one in."""
    score = score_for(packed, hafs, surah, ayah, script)
    plan = all_join(len(score.words))
    if rules is None:
        return score, hafs.perform(score, plan)
    from quranic_phonemizer.engine.run import perform

    return score, perform(score, rules, plan)
