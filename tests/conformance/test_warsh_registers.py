"""Warsh wasl and iltiqa registers: the source supplies each start and
repair, and the canonical morphology derivation is their reconciliation."""
from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Location, Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import Onset, Quality
from quranic_phonemizer.phonemize.legacy_views import phonemes_by_word
from quranic_phonemizer.riwayat.warsh import naql_script
from quranic_phonemizer.riwayat.warsh.resources import corpus as warsh_corpus
from tests.support.boundary import plan_for

ROOT = Path(__file__).resolve().parents[2]
WARSH_SOURCE = ROOT / "corpus_sources" / "warsh" / "scripts" / "king-fahd" / "quran.json"

HARAKA = {"َ": "A", "ُ": "U", "ِ": "I"}
MARK_QUALITY = {"۬": "A", "۟": "U", "۪": "I"}
TANWIN = set("ًٌٍٖٗٞ")
STOP_SIGNS = "ۖۗۘۙۚۛۜ۩"

#: The one reviewed lexical start delta: Warsh reads the passive استحق.
USTUHIQQA = "5:107:12"

#: Marked words whose start quality the mark writes against the canonical
#: derivation: the temporary qaf damm of اتقوا never licenses a damm start,
#: and the passive اتُّبِعُوا really starts on one.
DERIVATION_DELTAS = {"اتقوا": ("I", "U"), "اتبعوا": ("U", "I")}

#: Wasl-marked words with no canonical wasl onset: Warsh-only lexical wasl
#: readings, and the eased istifham meetings the hamza vertical owns.
WARSH_ONLY_WASL = {"18:89:2": "I", "18:92:2": "I", "20:77:6": "I", "26:52:5": "I"}
EASED_ISTIFHAM = {"27:61:15", "37:16:1", "38:8:1", "43:19:8", "50:3:1", "54:25:1"}

#: The sixteen silent-qata starts and their ibtidaa readings, read on into
#: the following word except where the doc's row is the waqf-on-host form.
QATA_STARTS = (
    ("6:71:29", "ʔi:tina:", "joined"),
    ("7:77:9", "ʔi:tina:", "joined"),
    ("8:32:17", "ʔi:tina:", "joined"),
    ("29:29:17", "ʔi:tina:", "joined"),
    ("10:15:11", "ʔi:ti", "joined"),
    ("26:10:6", "ʔi:ti", "joined"),
    ("10:79:3", "ʔi:tu:ni:", "joined"),
    ("12:50:3", "ʔi:tu:ni:", "joined"),
    ("12:54:3", "ʔi:tu:ni:", "joined"),
    ("12:59:5", "ʔi:tu:ni:", "joined"),
    ("46:4:18", "ʔi:tu:ni:", "joined"),
    ("20:64:4", "ʔi:tu:", "joined"),
    ("45:25:12", "ʔi:tu:", "joined"),
    ("41:11:10", "ʔi:tija:", "joined"),
    ("9:49:4", "ʔi:ðan", "stopped"),
    ("2:283:16", "ʔu:tumina", "joined"),
)

#: The closed damm-over-kasr repair register: canonical boundary, selected
#: source boundary, and host family.
DAMM_REPAIRS = (
    ("4:66:5", "4:65:5", "an"),
    ("5:49:1", "5:51:1", "an"),
    ("5:117:8", "5:119:8", "an"),
    ("16:36:7", "16:36:7", "an"),
    ("23:32:5", "23:32:5", "an"),
    ("27:45:7", "27:47:7", "an"),
    ("31:12:5", "31:11:5", "an"),
    ("31:14:12", "31:13:12", "an"),
    ("36:61:1", "36:60:1", "an"),
    ("68:22:1", "68:22:1", "an"),
    ("71:3:1", "71:3:1", "an"),
    ("4:154:6", "4:153:6", "plural_mim"),
    ("7:161:3", "7:161:3", "plural_mim"),
    ("16:32:7", "16:32:7", "plural_mim"),
    ("25:60:3", "25:60:3", "plural_mim"),
    ("36:45:3", "36:44:3", "plural_mim"),
    ("40:60:2", "40:60:2", "plural_mim"),
    ("7:195:20", "7:195:20", "qul"),
    ("10:101:1", "10:101:1", "qul"),
    ("17:56:1", "17:56:1", "qul"),
    ("17:110:1", "17:109:1", "qul"),
    ("34:22:1", "34:22:1", "qul"),
    ("2:173:13", "2:172:13", "min"),
    ("5:3:51", "5:4:51", "min"),
    ("6:145:30", "6:146:30", "min"),
    ("16:115:13", "16:115:13", "min"),
    ("6:65:21", "6:66:21", "tanwin"),
    ("6:99:32", "6:100:32", "tanwin"),
    ("7:49:7", "7:48:7", "tanwin"),
    ("14:26:5", "14:28:5", "tanwin"),
    ("4:66:8", "4:65:8", "aw"),
    ("17:110:4", "17:109:4", "aw"),
    ("73:3:2", "73:2:2", "aw"),
    ("6:10:1", "6:11:1", "qad"),
    ("13:32:1", "13:33:1", "qad"),
    ("21:41:1", "21:41:1", "qad"),
    ("7:143:15", "7:143:15", "lakin"),
    ("12:31:14", "12:31:14", "feminine_taa"),
)

FAMILY_SIZES = {
    "an": 11, "plural_mim": 6, "qul": 5, "min": 4, "tanwin": 4,
    "aw": 3, "qad": 3, "lakin": 1, "feminine_taa": 1,
}


def _skeleton(text: str) -> str:
    return "".join(char for char in text if char not in set("ًٌٍَُِّْٰ۪ٓ۟۬") | TANWIN | set(STOP_SIGNS))


@lru_cache(maxsize=None)
def _canonical_wasl() -> dict[str, list[str]]:
    """Every canonical wasl onset with its derived start, by canonical ref."""
    package = recitation(Riwayah.HAFS)
    out: dict[str, list[str]] = {}
    for surah_key, counts in sorted(
        package.corpus.surah_info.items(), key=lambda item: int(item[0])
    ):
        for ayah in range(1, len(counts) + 1):
            verse = VerseRef(int(surah_key), ayah)
            words = package.words(verse)
            built = package.build(package.read(Script.UTHMANI, verse, words))
            for index, word in enumerate(built.score.words):
                location = words[index][0]
                ref = f"{location.surah}:{location.ayah}:{location.word}"
                for slot in word.slots:
                    if slot.onset is Onset.WASL:
                        out.setdefault(ref, []).append(slot.nucleus.quality.name)
    return out


@lru_cache(maxsize=None)
def _marked_words() -> dict[str, tuple[str, str]]:
    """Canonical ref -> (source text, mark start quality) for the wasl family."""
    out = {}
    for location, entry in warsh_corpus().entries.items():
        text = entry.text
        if len(text) >= 3 and text[0] == "ا" and text[1] in HARAKA and text[2] in MARK_QUALITY:
            ref = f"{location.surah}:{location.ayah}:{location.word}"
            out[ref] = (text, MARK_QUALITY[text[2]])
    return out


def _read(riwayah: str, ref: str, words: tuple[int, ...], **boundary):
    package = recitation(Riwayah(riwayah))
    surah, ayah, _ = (int(part) for part in ref.split(":"))
    verse = VerseRef(surah, ayah)
    verse_words = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, verse_words))
    plan = plan_for(len(verse_words), **boundary)
    performance = package.perform(built.score, plan)
    from quranic_phonemizer.api import alphabet

    by_word = phonemes_by_word(performance, built.score, alphabet())
    return tuple("".join(by_word[word - 1]) for word in words)


def test_the_canonical_start_register_counts():
    covered = {
        f"{location.surah}:{location.ayah}:{location.word}"
        for location in warsh_corpus().entries
    }
    register = Counter()
    total = 0
    for ref, qualities in _canonical_wasl().items():
        if ref not in covered:
            continue
        for quality in qualities:
            total += 1
            register[quality] += 1
    assert _canonical_wasl()[USTUHIQQA] == ["I"]
    register["I"] -= 1
    register["U"] += 1

    assert total == 13480
    assert register == Counter({"A": 11982, "I": 1097, "U": 401})


def test_every_supplied_mark_start_reconciles_with_the_derivation():
    derived = _canonical_wasl()
    disagreements = {}
    unmatched = {}
    for ref, (text, mark) in _marked_words().items():
        qualities = derived.get(ref)
        if qualities is None:
            unmatched[ref] = mark
            continue
        if qualities[0] == mark:
            continue
        disagreements[ref] = (_skeleton(text), mark, qualities[0])

    for ref, (skeleton, mark, derivation) in disagreements.items():
        if ref == USTUHIQQA:
            assert (mark, derivation) == ("U", "I")
            continue
        assert skeleton in DERIVATION_DELTAS, (ref, skeleton, mark, derivation)
        assert (mark, derivation) == DERIVATION_DELTAS[skeleton], (ref, mark)
    assert USTUHIQQA in disagreements

    for ref, mark in unmatched.items():
        if ref in WARSH_ONLY_WASL:
            assert mark == WARSH_ONLY_WASL[ref]
        else:
            assert ref in EASED_ISTIFHAM, (ref, mark)
    assert set(WARSH_ONLY_WASL) <= set(unmatched)


@pytest.mark.parametrize(
    ("ref", "expected", "state"), QATA_STARTS, ids=[row[0] for row in QATA_STARTS]
)
def test_a_started_silent_qata_form_reads_the_replacement_long(ref, expected, state):
    word = int(ref.split(":")[2])
    waqf = word if state == "stopped" else word + 1
    got = _read("warsh", ref, (word,), ibtidaa=word, waqf=waqf)
    assert got == (expected,)


@pytest.mark.parametrize(
    ("canonical", "source", "family"), DAMM_REPAIRS, ids=[row[0] for row in DAMM_REPAIRS]
)
def test_a_damm_repair_row_joins_on_damm(canonical, source, family):
    word = int(canonical.split(":")[2])
    first, second = _read(
        "warsh", canonical, (word, word + 1), ibtidaa=word, waqf=word + 1
    )
    assert first.endswith("u"), (canonical, first, second)


def test_the_damm_repair_register_is_the_documented_38():
    assert len(DAMM_REPAIRS) == 38
    assert Counter(family for *_, family in DAMM_REPAIRS) == Counter(FAMILY_SIZES)


def test_the_tanwin_repair_register_is_generated_from_the_source():
    source = json.loads(WARSH_SOURCE.read_text(encoding="utf-8"))
    by_ref = {
        tuple(int(part) for part in ref.split(":")): record["text"].rstrip(STOP_SIGNS)
        for ref, record in source.items()
    }
    # The eased istifham words اَ۟شْهِدُواْ and اَ۟لَٰهٞ are not wasl.
    excluded_next = {"43:18:8", "27:63:15"}
    special = {"53:49:3"}  # the received عَاداٗ اَ۬لُّاول۪ىٰ junction is naql-owned
    sites = {}
    for (surah, ayah, word), text in by_ref.items():
        following = by_ref.get((surah, ayah, word + 1))
        if following is None or len(following) < 3:
            continue
        if not (following[0] == "ا" and following[1] in HARAKA and following[2] in MARK_QUALITY):
            continue
        ref = f"{surah}:{ayah}:{word}"
        if f"{surah}:{ayah}:{word + 1}" in excluded_next or ref in special:
            continue
        if any(char in TANWIN for char in text[-2:]):
            sites[ref] = HARAKA[following[1]]

    assert len(sites) == 44
    assert Counter(sites.values()) == Counter({"I": 40, "U": 4})
    register_tanwin = {
        source_ref for _, source_ref, family in DAMM_REPAIRS if family == "tanwin"
    }
    assert {ref for ref, quality in sites.items() if quality == "U"} == register_tanwin


# ------------------------------------------------------------------ naql
#: Host kinds a supplied latent qata may stand after; anything else is an
#: unreviewed boundary.
def _naql_family(text: str) -> str | None:
    quality = naql_script.latent_qata_quality(text)
    if quality is None:
        return None
    if text[1] == "\u0670":
        return "badal"
    if text[1] == "\u06df":
        return "damm_stroke"
    return f"written_{quality.name}"


def _naql_host_kind(text: str, quality: Quality) -> str:
    text = "".join(char for char in text if char not in STOP_SIGNS)
    index = len(text) - 1
    while index > 0 and text[index] in "\u0627\u0652":
        index -= 1
    char = text[index]
    if char in HARAKA:
        moved = HARAKA[char] == ("A" if quality is Quality.A else quality.name)
        return "moved_haraka" if moved else "mismatch"
    if char in TANWIN:
        return "tanwin"
    if char == "\u0653":
        return "spelled"
    return "other"


@lru_cache(maxsize=None)
def _naql_boundaries():
    by_verse: dict[tuple[int, int], dict[int, str]] = {}
    for location, entry in warsh_corpus().entries.items():
        by_verse.setdefault((location.surah, location.ayah), {})[
            location.word
        ] = entry.text
    within: Counter = Counter()
    edge: Counter = Counter()
    for (surah, ayah), words in by_verse.items():
        for word, text in words.items():
            family = _naql_family(text)
            if family is None:
                continue
            quality = naql_script.latent_qata_quality(text)
            if word > 1:
                within[(family, _naql_host_kind(words[word - 1], quality))] += 1
            elif ayah > 1 and (surah, ayah - 1) in by_verse:
                previous = by_verse[(surah, ayah - 1)]
                host = previous[max(previous)]
                edge[(family, _naql_host_kind(host, quality))] += 1
            else:
                edge[(family, "surah_start")] += 1
    return within, edge


def test_the_naql_latent_register_reconciles_with_canonical_hosts():
    """Every supplied latent qata stands after an eligible host: the written
    moved haraka, a tanwin, or (at one edge) a spelled opening. The research
    doc's 1,550/180 subtotals are not reproducible from the supplied
    families; see docs/conformance.md."""
    within, edge = _naql_boundaries()
    assert sum(within.values()) == 1868
    assert within == Counter({
        ("written_A", "moved_haraka"): 752,
        ("written_A", "tanwin"): 365,
        ("written_I", "moved_haraka"): 174,
        ("written_I", "tanwin"): 299,
        ("written_U", "moved_haraka"): 1,
        ("written_U", "tanwin"): 1,
        ("damm_stroke", "moved_haraka"): 60,
        ("damm_stroke", "tanwin"): 43,
        ("badal", "moved_haraka"): 131,
        ("badal", "tanwin"): 42,
    })
    joinable = {key: count for key, count in edge.items() if key[1] != "surah_start"}
    assert sum(joinable.values()) == 325
    assert joinable == {
        ("written_A", "tanwin"): 112,
        ("written_A", "spelled"): 1,
        ("written_I", "tanwin"): 193,
        ("written_I", "moved_haraka"): 1,
        ("damm_stroke", "tanwin"): 14,
        ("badal", "tanwin"): 4,
    }


def test_a_full_hamza_after_a_sakin_verse_end_is_only_kitabiyah():
    """The one adjacent-ayah boundary written with tahqiq: كتابيه إني."""
    by_verse: dict[tuple[int, int], dict[int, str]] = {}
    for location, entry in warsh_corpus().entries.items():
        by_verse.setdefault((location.surah, location.ayah), {})[
            location.word
        ] = entry.text
    tahqiq = set()
    for (surah, ayah), words in by_verse.items():
        first = words[1]
        if ayah == 1 or first[0] not in "\u0621\u0623\u0625":
            continue
        previous = by_verse.get((surah, ayah - 1))
        if previous is None:
            continue
        host = "".join(
            char for char in previous[max(previous)] if char not in STOP_SIGNS
        )
        index = len(host) - 1
        while index > 0 and host[index] in "\u0627\u0652":
            index -= 1
        # A sakin consonant ends bare once the plural alif and sukun are
        # stripped; a madda or carrier there is a long vowel, not a host.
        if host[index] not in HARAKA and host[index] not in TANWIN and (
            host[index] not in "\u0653\u0670\u06e5\u06e6\u06d2"
        ) and host.endswith("\u0652"):
            tahqiq.add(Location(surah, ayah, 1))
    assert tahqiq == {Location(69, 20, 1)}
    assert warsh_corpus().entries[Location(69, 20, 1)].text.startswith("إ")


def test_the_article_naql_register_is_the_documented_1307():
    """1,283 written article alifs, 22 suppressed-alif prefix forms, and the
    two interrogative tokens; the reviewed long bases cover 214 tokens."""
    counts: Counter = Counter()
    longs = 0
    for location, entry in warsh_corpus().entries.items():
        text = "".join(char for char in entry.text if char not in STOP_SIGNS)
        found = naql_script._article_lam(text)
        if found is None:
            continue
        lam, wasl_alif = found
        if lam + 2 >= len(text) or text[lam + 1] not in HARAKA:
            continue
        if text[lam + 2] not in "\u0627\u0670":
            continue
        if text.startswith("\u0621"):
            kind = "interrogative"
        elif text[0] == "\u0644" or text.startswith("\u0648\u064e\u0644"):
            kind = "suppressed_alif"
        elif wasl_alif is None:
            kind = "written_alif"
        else:
            kind = "written_alif_prefixed"
        counts[kind] += 1
        if text[lam + 2] == "\u0670" or naql_script._skeleton(
            text[lam + 3:]
        ) in naql_script._LONG_BASES:
            longs += 1
    assert counts == Counter({
        "written_alif": 955,
        "written_alif_prefixed": 328,
        "suppressed_alif": 22,
        "interrogative": 2,
    })
    assert counts["written_alif"] + counts["written_alif_prefixed"] == 1283
    assert sum(counts.values()) == 1307
    assert longs == 214
