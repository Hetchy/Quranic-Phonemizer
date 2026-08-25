"""Closed selected-source registers for Warsh joined and pausal shapes."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "corpus_sources/warsh/scripts/king-fahd/quran.json"
STOP = frozenset("ۖۗۘۙۚۛۜ۩")
LETTERS = frozenset("ابتثجحخدذرزسشصضطظعغفقكلمنهويىےءأإؤئ")

YAA_ZAWAID_SOURCE_REFS = (
    "2:185:9", "2:185:11", "3:20:8", "11:46:12", "11:105:2",
    "14:17:10", "14:42:9", "17:62:8", "17:97:5", "18:17:27",
    "18:24:19", "18:39:4", "18:63:5", "18:65:8", "20:91:9",
    "22:23:16", "22:42:11", "27:37:5", "27:37:8", "28:34:14",
    "34:13:9", "34:45:14", "35:26:7", "36:22:15", "37:56:5",
    "40:14:16", "40:32:6", "42:30:3", "44:19:6", "44:20:5",
    "50:14:9", "50:41:4", "50:45:13", "54:6:5", "54:8:3",
    "54:16:4", "54:18:6", "54:21:4", "54:30:4", "54:37:9",
    "54:39:3", "67:18:12", "67:19:8", "89:4:3", "89:9:5",
    "89:16:3", "89:18:3",
)

RETAINED_ANA_SOURCE_REFS = (
    "2:257:21", "6:165:6", "7:143:39", "12:45:8", "12:69:10",
    "18:34:8", "18:38:15", "27:40:5", "27:41:7", "40:42:11",
    "43:81:6", "60:1:36",
)

ANA_QATA_I_SOURCE_REFS = ("7:188:23", "26:115:2", "46:8:21")
PLAIN_ANA_FORMS = frozenset({"أَنَا", "اَنَا", "وَأَنَا"})


def _source() -> dict[str, str]:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    return {ref: record["text"] for ref, record in raw.items()}


def _prior_base(text: str, offset: int) -> str | None:
    return next((char for char in reversed(text[:offset]) if char in LETTERS), None)


def _yaa_zawaid(text: str) -> bool:
    try:
        offset = text.index("ۦ")
    except ValueError:
        return False
    tail = text[offset + 1:]
    return (
        _prior_base(text, offset) not in {"ه", "ي"}
        and all(char in STOP | {"ٓ", "َ"} for char in tail)
    )


def test_the_plural_mim_qata_family_is_exactly_the_reviewed_888():
    rows = {
        ref: text for ref, text in _source().items() if "مُۥٓ" in text
    }

    assert len(rows) == 888
    assert all(text.rstrip("".join(STOP)).endswith("مُۥٓ") for text in rows.values())


def test_the_yaa_zawaid_sequence_family_is_the_closed_47_row_register():
    rows = {ref: text for ref, text in _source().items() if _yaa_zawaid(text)}

    assert tuple(rows) == YAA_ZAWAID_SOURCE_REFS
    assert Counter(
        "consonantal" if "ۦَ" in text
        else "munfasil" if "ۦٓ" in text
        else "badal" if ref == "14:42:9"
        else "tabii"
        for ref, text in rows.items()
    ) == Counter({"tabii": 35, "munfasil": 10, "badal": 1, "consonantal": 1})


def test_the_small_yaa_lookalikes_are_separate_closed_families():
    rows = _source()
    silah = 0
    ordinary_yaa = 0
    for text in rows.values():
        for offset, char in enumerate(text):
            if char != "ۦ":
                continue
            previous = _prior_base(text, offset)
            silah += previous == "ه"
            ordinary_yaa += previous == "ي"

    assert (silah, ordinary_yaa) == (939, 20)


def test_the_retained_and_deleted_ana_qata_registers_are_exact():
    rows = _source()

    assert all(
        rows[ref].rstrip("".join(STOP)).endswith("نَآ")
        for ref in RETAINED_ANA_SOURCE_REFS
    )
    assert all(
        rows[ref].rstrip("".join(STOP)).endswith("نَا")
        for ref in ANA_QATA_I_SOURCE_REFS
    )
    assert len(RETAINED_ANA_SOURCE_REFS) == 12
    assert len(ANA_QATA_I_SOURCE_REFS) == 3


def test_the_plain_ana_family_excludes_longer_lexemes_with_the_same_tail():
    rows = _source()
    plain = Counter(
        text.rstrip("".join(STOP))
        for text in rows.values()
        if text.rstrip("".join(STOP)) in PLAIN_ANA_FORMS
    )

    assert plain == Counter({
        "أَنَا": 38,
        "وَأَنَا": 14,
        "اَنَا": 4,
    })
    assert "نَبَّأَنَا" in rows.values()


def test_the_insan_rows_use_the_reviewed_alternate_fathatan_family():
    rows = _source()
    assert {
        ref for ref, text in rows.items()
        if ref in {"76:4:4", "76:15:8", "76:16:1"} and "اٗ" in text
    } == {"76:4:4", "76:15:8", "76:16:1"}


def test_every_projected_qata_mim_has_the_neutral_joined_only_shape():
    package = recitation(Riwayah.WARSH)
    candidates = {
        location for location, entry in package.corpus.entries.items()
        if "مُۥٓ" in entry.text
    }

    assert len(candidates) == 888
    for location in candidates:
        verse = VerseRef(location.surah, location.ayah)
        source = package.words(verse)
        reading = package.read(
            Script.UTHMANI, verse, (source[location.word - 1],)
        )
        mim = package.build(reading).score.words[0].slots[-1]

        assert mim.letter is CanonLetter.MEEM, location
        assert mim.nucleus.is_joined_only_long, location
        assert mim.nucleus.quality is Quality.U, location


def test_every_yaa_zawaid_source_projects_its_reviewed_shape():
    package = recitation(Riwayah.WARSH)
    candidates = {
        location: entry for location, entry in package.corpus.entries.items()
        if _yaa_zawaid(entry.text)
    }

    assert len(candidates) == 47
    for location, entry in candidates.items():
        verse = VerseRef(location.surah, location.ayah)
        source = package.words(verse)
        reading = package.read(
            Script.UTHMANI, verse, (source[location.word - 1],)
        )
        slots = package.build(reading).score.words[0].slots

        if "ۦَ" in entry.text:
            assert slots[-1].letter is CanonLetter.YA, location
            assert slots[-1].onset is Onset.GLIDE, location
            assert (
                slots[-1].nucleus == slots[-1].nucleus.short(Quality.A)
            ), location
        else:
            assert slots[-1].nucleus.is_joined_only_long, location
            assert slots[-1].nucleus.quality is Quality.I, location
