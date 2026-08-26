"""Build the reviewed order-8 register from canonical/source evidence.

This is a maintainer tool.  Runtime loads its checked-in JSON output and never
derives the closed register from its own current pronunciation.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Onset
from quranic_phonemizer.riwayat.warsh.resources import corpus


OUTPUT = ROOT / "quranic_phonemizer/data/riwayat/warsh/hamza_meetings.json"

TARGETS = {
    "A+A": 30, "I+I": 37, "U+U": 1, "A+I": 19,
    "A+U": 1, "I+A": 29, "U+A": 13, "U+I": 26,
}

AIMMA = {"9:12:11", "21:73:2", "28:5:10", "28:41:2", "32:24:3"}
AAJAMI = {"41:44:9"}
TRIPLE = {"7:123:3", "20:71:2", "26:49:2", "43:58:2"}
JAA_AAL = {"15:61:3", "54:41:3"}
KASR_YAA = {"2:31:13", "24:33:33"}
ONE_WORD_EXCLUDED = {
    "13:5:8", "17:49:6", "17:98:11", "23:82:7", "27:67:4",
    "32:10:6", "37:16:6", "37:53:6", "56:47:8", "60:4:27",
    "79:11:8",
    "2:264:12", "4:38:4", "8:47:8", "79:11:1", "60:4:14",
}


def _ref(location) -> str:
    return str(location)


def _source(location) -> str:
    item = corpus().entries[location].sources[0].location
    return f"{item.surah}:{item.ayah}:{item.word}"


def _one_word_rows(package):
    rows = []
    for surah, ayahs in sorted(package.corpus.surah_info.items(), key=lambda item: int(item[0])):
        for ayah in range(1, len(ayahs) + 1):
            verse = VerseRef(int(surah), ayah)
            built = package.build(package.read(Script.UTHMANI, verse, package.words(verse)))
            for word in built.score.words:
                adjacent = [
                    (left, right)
                    for left, right in zip(word.slots, word.slots[1:])
                    if left.letter is CanonLetter.HAMZA and right.letter is CanonLetter.HAMZA
                ]
                if not adjacent:
                    continue
                hamzas = adjacent[0]
                if hamzas[0].nucleus.quality is None or hamzas[1].nucleus.quality is None:
                    continue
                pair = f"{hamzas[0].nucleus.quality.name}+{hamzas[1].nucleus.quality.name}"
                if pair not in {"A+A", "A+I", "A+U"}:
                    continue
                canonical = _ref(word.location)
                if canonical in ONE_WORD_EXCLUDED:
                    continue
                exception = (
                    "aimma" if canonical in AIMMA else
                    "aajami" if canonical in AAJAMI else
                    "triple" if canonical in TRIPLE else None
                )
                owner = "hamza_dhat_fath" if pair == "A+A" and exception is None else "fixed_tashil"
                rows.append({
                    "source": _source(word.location), "canonical": canonical,
                    "first": pair[0], "second": pair[2], "scope": "one_word",
                    "owner": owner, "exception": exception,
                })
    by_ref = {str(location): location for location in corpus().entries}
    for canonical in sorted(TRIPLE - {row["canonical"] for row in rows}):
        location = by_ref[canonical]
        rows.append({
            "source": _source(location), "canonical": canonical,
            "first": "A", "second": "A", "scope": "one_word",
            "owner": "fixed_tashil", "exception": "triple",
        })
    return rows


def _across_candidates(package):
    grouped = defaultdict(list)
    for surah, ayahs in sorted(package.corpus.surah_info.items(), key=lambda item: int(item[0])):
        for ayah in range(1, len(ayahs) + 1):
            verse = VerseRef(int(surah), ayah)
            built = package.build(package.read(Script.UTHMANI, verse, package.words(verse)))
            for left, right in zip(built.score.words, built.score.words[1:]):
                first = left.slots[-2] if left.slots[-1].origin.value == "nunation" else left.slots[-1]
                second = right.slots[0]
                if (
                    first.letter is CanonLetter.HAMZA and first.onset is Onset.PLAIN
                    and first.nucleus.quality is not None
                    and second.letter is CanonLetter.HAMZA and second.onset is Onset.PLAIN
                    and second.nucleus.quality is not None
                ):
                    pair = f"{first.nucleus.quality.name}+{second.nucleus.quality.name}"
                    grouped[pair].append((left.location, right.location))
    return grouped


def _supplement(package, grouped):
    """Supply compact-script misses after the strict qata scan.

    Checked-in rows remain authoritative; this only rebuilds them.
    """
    wanted = {
        "I+I": ("3:93:6", "7:11:11", "7:125:2"),
        "I+A": ("2:9:7", "2:20:10"),
        "U+I": ("82:1:2", "84:1:2"),
    }
    by_location = {
        word.location: word
        for surah, ayahs in sorted(package.corpus.surah_info.items(), key=lambda item: int(item[0]))
        for ayah in range(1, len(ayahs) + 1)
        for word in package.build(package.read(
            Script.UTHMANI,
            VerseRef(int(surah), ayah),
            package.words(VerseRef(int(surah), ayah)),
        )).score.words
    }
    for pair, refs in wanted.items():
        for ref in refs:
            surah, ayah, word = (int(part) for part in ref.split(":"))
            left = by_location[next(location for location in by_location if str(location) == ref)]
            right_ref = next(location for location in by_location if (location.surah, location.ayah, location.word) == (surah, ayah, word + 1))
            candidate = (left.location, right_ref)
            if candidate not in grouped[pair]:
                grouped[pair].append(candidate)


def _across_rows(package):
    grouped = _across_candidates(package)
    _supplement(package, grouped)
    rows = []
    required = {
        "A+A": {"15:61:3", "54:41:3", "4:43:28"},
        "I+I": {"2:31:13", "24:33:33", "4:22:8"},
        "U+U": {"46:32:15"},
        "A+I": {"49:9:18", "19:3:1"},
        "A+U": {"23:44:8"},
        "I+A": {"2:235:10"},
        "U+A": {"11:44:6", "14:28:1"},
        "U+I": {"19:7:2"},
    }
    cross = {
        "A+I": ("19:2:5", "19:3:1"),
        "U+A": ("14:27:18", "14:28:1"),
    }
    forced = {"U+I": (("19:7:1", "19:7:2"),)}
    by_ref = {str(location): location for location in corpus().entries}
    for pair, target in TARGETS.items():
        candidates = list(grouped[pair])
        for left_ref, right_ref in forced.get(pair, ()):
            candidate = (by_ref[left_ref], by_ref[right_ref])
            if candidate not in candidates:
                candidates.append(candidate)
            required[pair].add(right_ref)
        if pair in cross:
            left_ref, right_ref = cross[pair]
            left = next(location for location in corpus().entries if str(location) == left_ref)
            right = next(location for location in corpus().entries if str(location) == right_ref)
            candidates.append((left, right))
        candidates.sort(key=lambda item: (str(item[1]) not in required[pair], item[1]))
        for left, right in candidates[:target]:
            canonical = _ref(right)
            exception = "jaa_aal" if canonical in JAA_AAL else "kasr_yaa" if canonical in KASR_YAA else None
            if exception == "jaa_aal":
                owner = "jaa_aal"
            elif exception == "kasr_yaa":
                owner = "hamza_kasr_yaa"
            elif pair in {"A+A", "I+I", "U+U"}:
                owner = "hamza_muttafiq"
            elif pair in {"A+I", "A+U"}:
                owner = "fixed_tashil"
            elif pair in {"I+A", "U+A"}:
                owner = "fixed_ibdal"
            else:
                owner = "hamza_damm_kasr"
            rows.append({
                "source": _source(right), "canonical": canonical,
                "previous": _ref(left), "first": pair[0], "second": pair[2],
                "scope": "joined_ayahs" if pair in cross and (str(left), str(right)) == cross[pair] else "joined_words",
                "owner": owner, "exception": exception,
            })
    return rows


def main() -> None:
    package = recitation(Riwayah.HAFS)
    rows = _one_word_rows(package)
    rows.extend(_across_rows(package))
    payload = {"schema_version": 1, "rows": rows}
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
