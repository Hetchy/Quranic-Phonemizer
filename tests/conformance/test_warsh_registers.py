"""Warsh wasl and connected-vowel registers reconciled to morphology."""
from __future__ import annotations

import json
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.model.address import Location, Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality, Rule
from quranic_phonemizer.phonemize.legacy_views import phonemes_by_word
from quranic_phonemizer.riwayat.warsh import naql_script
from quranic_phonemizer.riwayat.warsh.relative_pronoun import relative_pronoun_form
from quranic_phonemizer.riwayat.warsh.resources import corpus as warsh_corpus
from quranic_phonemizer.riwayat.warsh.single_hamza import (
    authored_locations,
    canonical_absence,
    fixed_ibdal_counts,
    fixed_ibdal_family,
    supplied_ibdal,
)
from tests.support.boundary import plan_for

ROOT = Path(__file__).resolve().parents[2]
WARSH_SOURCE = ROOT / "corpus_sources" / "warsh" / "scripts" / "king-fahd" / "quran.json"

HARAKA = {"َ": "A", "ُ": "U", "ِ": "I"}
MARK_QUALITY = {"۬": "A", "۟": "U", "۪": "I"}
TANWIN = set("ًٌٍٖٗٞ")
STOP_SIGNS = "ۖۗۘۙۚۛۜ۩"

LEEN_MAHMUZ_EXCLUSIONS = {"18:58:19", "81:8:2"}
SAWAT = {
    "7:20:10", "7:22:8", "7:26:8", "7:27:15", "20:121:5",
}

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
    ("6:71:29", "ʔi:tina:", "a:tina:", "joined"),
    ("7:77:9", "ʔi:tina:", "u:tina:", "joined"),
    ("8:32:17", "ʔi:tina:", "i:tina:", "joined"),
    ("29:29:17", "ʔi:tina:", "u:tina:", "joined"),
    ("10:15:11", "ʔi:ti", "a:ti", "joined"),
    ("26:10:6", "ʔi:ti", "i:ti", "joined"),
    ("10:79:3", "ʔi:tu:ni:", "u:tu:ni:", "joined"),
    ("12:50:3", "ʔi:tu:ni:", "u:tu:ni:", "joined"),
    ("12:54:3", "ʔi:tu:ni:", "u:tu:ni:", "joined"),
    ("12:59:5", "ʔi:tu:ni:", "a:tu:ni:", "joined"),
    ("46:4:18", "ʔi:tu:ni:", "i:tu:ni:", "joined"),
    ("20:64:4", "ʔi:tu:", "a:tu:", "joined"),
    ("45:25:12", "ʔi:tu:", "u:tu:", "joined"),
    ("41:11:10", "ʔi:tija:", "i:tija:", "joined"),
    ("9:49:4", "ʔi:ðan", "u:ða", "stopped"),
    ("2:283:16", "ʔu:tumina", "i:tumina", "joined"),
)

#: The closed damm-over-kasr connected-form register: canonical boundary,
#: selected source boundary, and host family.
DAMM_CONNECTED_FORMS = (
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

CANONICAL_ABSENCE = canonical_absence()
TAHQIQ_EXCLUSIONS = tuple(sorted(authored_locations("tahqiq_exclusions")))


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


def _boundary_rules(ref: str) -> set[Rule]:
    package = recitation(Riwayah.WARSH)
    surah, ayah, word = (int(part) for part in ref.split(":"))
    verse = VerseRef(surah, ayah)
    verse_words = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, verse_words))
    plan = plan_for(len(verse_words), ibtidaa=word, waqf=word + 1)
    performance = package.perform(built.score, plan)
    return {
        occurrence.rule
        for occurrence in performance.occurrences
        if occurrence.boundary == word - 1
    }


@lru_cache(maxsize=1)
def _derived_regular_single_hamza() -> dict[Location, int]:
    """Reconcile selected supplies with the canonical single-hamza shape."""
    hafs = recitation(Riwayah.HAFS)
    warsh = recitation(Riwayah.WARSH)
    register = {}
    for surah_key, counts in sorted(
        warsh.corpus.surah_info.items(), key=lambda item: int(item[0])
    ):
        surah = int(surah_key)
        for ayah in range(1, len(counts) + 1):
            verse = VerseRef(surah, ayah)
            words = warsh.words(verse)
            hafs_built = hafs.build(
                hafs.read(Script.UTHMANI, verse, hafs.words(verse))
            )
            warsh_built = warsh.build(
                warsh.read(Script.UTHMANI, verse, words)
            )
            for index, (hafs_word, warsh_word) in enumerate(
                zip(hafs_built.score.words, warsh_built.score.words)
            ):
                location = words[index][0]
                if fixed_ibdal_family(warsh_corpus().entries[location].text):
                    continue
                lost_hamza = sum(
                    slot.letter is CanonLetter.HAMZA for slot in hafs_word.slots
                ) > sum(
                    slot.letter is CanonLetter.HAMZA for slot in warsh_word.slots
                )
                if not lost_hamza:
                    continue
                for slot_index, slot in enumerate(hafs_word.slots[1:], start=1):
                    before = hafs_word.slots[slot_index - 1]
                    if before.letter is CanonLetter.HAMZA:
                        continue
                    sakin = (
                        slot.letter is CanonLetter.HAMZA
                        and slot.nucleus.is_silent
                        and not before.nucleus.is_silent
                    )
                    open_after_u = (
                        slot.letter is CanonLetter.HAMZA
                        and slot.nucleus.quality is Quality.A
                        and before.nucleus.quality is Quality.U
                    )
                    if sakin or open_after_u:
                        register[location] = (
                            slot_index if open_after_u else slot_index - 1
                        )
    return register


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
    ("ref", "expected", "joined", "state"),
    QATA_STARTS,
    ids=[row[0] for row in QATA_STARTS],
)
def test_a_started_silent_qata_form_reads_the_replacement_long(
    ref, expected, joined, state
):
    del joined
    word = int(ref.split(":")[2])
    waqf = word if state == "stopped" else word + 1
    got = _read("warsh", ref, (word,), ibtidaa=word, waqf=waqf)
    assert got == (expected,)


@pytest.mark.parametrize(
    ("ref", "started", "joined", "state"),
    QATA_STARTS,
    ids=[row[0] for row in QATA_STARTS],
)
def test_a_joined_silent_qata_form_uses_the_preceding_vowel(
    ref, started, joined, state
):
    del started, state
    word = int(ref.split(":")[2])
    before, got = _read(
        "warsh", ref, (word - 1, word), ibtidaa=word - 1, waqf=word + 1
    )
    assert before
    assert got == joined


@pytest.mark.parametrize(
    ("canonical", "source", "family"),
    DAMM_CONNECTED_FORMS,
    ids=[row[0] for row in DAMM_CONNECTED_FORMS],
)
def test_a_damm_over_kasr_form_joins_on_damm(canonical, source, family):
    word = int(canonical.split(":")[2])
    first, second = _read(
        "warsh", canonical, (word, word + 1), ibtidaa=word, waqf=word + 1
    )
    assert first.endswith("u"), (canonical, first, second)
    assert (Rule.ILTIQA_HARAKA in _boundary_rules(canonical)) is (
        family == "tanwin"
    )


def test_the_damm_connected_form_register_is_the_documented_38():
    assert len(DAMM_CONNECTED_FORMS) == 38
    assert Counter(
        family for *_, family in DAMM_CONNECTED_FORMS
    ) == Counter(FAMILY_SIZES)


def test_relative_pronoun_projection_covers_only_its_selected_script_family():
    relative = [
        entry
        for entry in warsh_corpus().entries.values()
        if relative_pronoun_form(entry.text)
    ]

    forms = Counter(
        "".join(
            char for char in entry.text
            if not unicodedata.combining(char) and char not in "ـۥۦۧۨ"
        )
        for entry in relative
    )

    assert forms == Counter({
        "الذين": 812,
        "الذے": 268,
        "والذين": 163,
        "للذين": 80,
        "التے": 65,
        "والذے": 15,
        "بالذے": 11,
        "فالذين": 10,
        "كالذين": 9,
        "بالتے": 7,
        "بالذين": 6,
        "كالذے": 5,
        "والتے": 4,
        "للذے": 4,
        "كالتے": 1,
        "للتے": 1,
        "وبالذے": 1,
        "وللذين": 1,
        "والذن": 1,
    })
    assert len(relative) == 1464
    assert not relative_pronoun_form(
        warsh_corpus().entries[Location(12, 13, 10)].text
    )
    assert not relative_pronoun_form(
        warsh_corpus().entries[Location(7, 144, 7)].text
    )


def test_every_selected_relative_pronoun_restores_the_lam_gemination():
    warsh = recitation(Riwayah.WARSH)
    seen = 0
    for location, entry in warsh_corpus().entries.items():
        if not relative_pronoun_form(entry.text):
            continue
        built = warsh.build(warsh.read(
            Script.UTHMANI,
            location.verse,
            ((location, entry.text),),
        ))
        lam, relative = next(
            (current, following)
            for current, following in zip(
                built.score.words[0].slots,
                built.score.words[0].slots[1:],
            )
            if current.letter is CanonLetter.LAM
            and following.letter in {CanonLetter.THAL, CanonLetter.TA}
        )
        assert lam.onset is Onset.GEMINATE, (location, entry.text)
        assert lam.nucleus.is_short and lam.nucleus.quality is Quality.A
        assert relative.onset is Onset.PLAIN, (location, entry.text)
        seen += 1

    assert seen == 1464


def test_unwritten_gemination_source_conventions_are_closed():
    families = Counter()
    for entry in warsh_corpus().entries.values():
        text = entry.text
        if "ّ" in text:
            continue
        skeleton = "".join(
            char for char in text
            if not unicodedata.combining(char) and char not in "ـۥۦۧۨ"
        )
        if relative_pronoun_form(text):
            families["relative_pronoun"] += 1
        elif skeleton in {"لله", "ولله", "فلله"}:
            families["contracted_divine_name"] += 1
        elif skeleton == "اليل":
            families["al_layl"] += 1

    assert families == Counter({
        "relative_pronoun": 1434,
        "contracted_divine_name": 135,
        "al_layl": 59,
    })


def test_every_unmarked_solar_shape_is_relative_or_a_closed_nonarticle():
    sun = set("تثدذرزسشصضطظلن")
    prefixes = ("وبال", "وكال", "وال", "فال", "بال", "كال", "ولل", "لل", "ال")
    residual = Counter()
    for entry in warsh_corpus().entries.values():
        bases = [
            (char, offset)
            for offset, char in enumerate(entry.text)
            if not unicodedata.combining(char) and char not in "ـۥۦۧۨ"
        ]
        skeleton = "".join(char for char, _ in bases)
        prefix = next((one for one in prefixes if skeleton.startswith(one)), None)
        if prefix is None or len(bases) <= len(prefix):
            continue
        following = len(prefix)
        if bases[following][0] not in sun:
            continue
        start = bases[following][1]
        end = bases[following + 1][1] if following + 1 < len(bases) else len(entry.text)
        if "ّ" in entry.text[start:end] or relative_pronoun_form(entry.text):
            continue
        residual[skeleton] += 1

    assert residual == Counter({
        "الن": 4,
        "التقى": 3,
        "فالن": 1,
        "التقتا": 1,
        "التقيتم": 1,
        "الزمنه": 1,
        "فالتقطه": 1,
        "والد": 1,
        "والده": 1,
        "فالتقمه": 1,
        "فالتقى": 1,
        "فالتمسوا": 1,
        "والتفت": 1,
    })


def test_the_fixed_single_hamza_register_is_the_documented_56():
    register = Counter(
        family
        for entry in warsh_corpus().entries.values()
        if (family := fixed_ibdal_family(entry.text)) is not None
    )
    assert register == Counter(fixed_ibdal_counts())
    assert register.total() == 56


def test_the_regular_selected_single_hamza_register_is_closed():
    register = supplied_ibdal()
    assert len(register) == 918
    assert Counter(register.values()) == Counter({0: 596, 2: 162, 1: 119, 3: 37, 4: 4})
    assert not any(
        fixed_ibdal_family(warsh_corpus().entries[location].text)
        for location in register
    )
    assert register == _derived_regular_single_hamza()


@pytest.mark.parametrize(("ref", "text"), CANONICAL_ABSENCE.items())
def test_the_four_isqat_spellings_create_no_ghost_hamza(ref, text):
    surah, ayah, word = ref.surah, ref.ayah, ref.word
    entry = warsh_corpus().entries[ref]
    assert entry.text == text

    package = recitation(Riwayah.WARSH)
    verse = VerseRef(surah, ayah)
    words = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, words))
    slots = built.score.words[word - 1].slots
    assert all(
        slot.letter is not CanonLetter.HAMZA or slot.onset is Onset.WASL
        for slot in slots
    )
    performance = package.perform(
        built.score, plan_for(len(words), isolated=word)
    )
    ids = {slot.id for slot in slots}
    assert not {
        occurrence.rule
        for occurrence in performance.occurrences
        if ids & set(occurrence.subjects)
    } & {Rule.IBDAL_HAMZA, Rule.TASHIL}


def test_the_iwaa_tahqiq_exclusion_register_is_the_documented_25():
    assert len(TAHQIQ_EXCLUSIONS) == 25
    assert all(
        any(char in "ءأإؤئٕٔ" for char in warsh_corpus().entries[ref].text)
        for ref in TAHQIQ_EXCLUSIONS
    )


@pytest.mark.parametrize("ref", TAHQIQ_EXCLUSIONS)
@pytest.mark.parametrize("state", ("isolated", "continued"))
def test_every_iwaa_exclusion_keeps_tahqiq_in_each_boundary_state(ref, state):
    package = recitation(Riwayah.WARSH)
    verse = VerseRef(ref.surah, ref.ayah)
    words = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, words))
    slots = built.score.words[ref.word - 1].slots
    hamzas = {
        slot.id for slot in slots
        if slot.letter is CanonLetter.HAMZA and slot.onset is not Onset.WASL
    }
    assert hamzas

    boundary = (
        {"isolated": ref.word}
        if state == "isolated"
        else {"ibtidaa": ref.word, "waqf": ref.word + 1}
    )
    performance = package.perform(
        built.score, plan_for(len(words), **boundary)
    )
    assert not {
        occurrence.rule
        for occurrence in performance.occurrences
        if hamzas & set(occurrence.subjects)
    } & {Rule.IBDAL_HAMZA, Rule.TASHIL}


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
        source_ref
        for _, source_ref, family in DAMM_CONNECTED_FORMS
        if family == "tanwin"
    }
    assert {ref for ref, quality in sites.items() if quality == "U"} == register_tanwin


# ------------------------------------------------------------------ naql
#: Host kinds a supplied latent qata may stand after; anything else is an
#: unreviewed boundary.
def _naql_family(text: str) -> str | None:
    quality = naql_script.latent_qata_quality(text)
    if quality is None:
        return None
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
    """Every supplied latent qata stands after an eligible host: a written
    moved haraka, a tanwin, or one spelled opening at a verse edge."""
    within, edge = _naql_boundaries()
    assert sum(within.values()) == 1680
    assert within == Counter({
        ("written_A", "moved_haraka"): 752,
        ("written_A", "tanwin"): 365,
        ("written_I", "moved_haraka"): 173,
        ("written_I", "tanwin"): 298,
        ("written_U", "tanwin"): 1,
        ("damm_stroke", "moved_haraka"): 48,
        ("damm_stroke", "tanwin"): 43,
    })
    joinable = {key: count for key, count in edge.items() if key[1] != "surah_start"}
    assert sum(joinable.values()) == 320
    assert joinable == {
        ("written_A", "tanwin"): 112,
        ("written_A", "spelled"): 1,
        ("written_I", "tanwin"): 192,
        ("written_I", "moved_haraka"): 1,
        ("damm_stroke", "tanwin"): 14,
    }


def test_the_193_initial_badals_have_the_reviewed_quality_register():
    register = Counter(
        quality.name
        for entry in warsh_corpus().entries.values()
        if (quality := naql_script.latent_qata_badal_quality(entry.text))
        is not None
    )
    assert register == Counter({"A": 177, "U": 13, "I": 3})


def test_the_selected_source_has_the_reviewed_304_leen_mahmuz_candidates():
    raw = json.loads(WARSH_SOURCE.read_text(encoding="utf-8"))
    families = {
        "yaa_combining": ("ئْ", "يْـٔ"),
        "yaa_barree": ("ےْء",),
        "waw_bare": ("وْء",),
        "waw_seated": ("وْئ",),
    }
    counts = Counter({
        name: sum(
            any(pattern in row["text"] for pattern in patterns)
            for row in raw.values()
        )
        for name, patterns in families.items()
    })
    assert counts == Counter({
        "yaa_combining": 84,
        "yaa_barree": 202,
        "waw_bare": 17,
        "waw_seated": 1,
    })
    assert sum(counts.values()) == 304


@pytest.mark.slow
def test_the_canonical_leen_mahmuz_register_reconciles_to_302_emissions():
    package = recitation(Riwayah.WARSH)
    candidates: set[tuple[str, int]] = set()
    emitted: set[tuple[str, int]] = set()
    families = Counter()

    for surah, counts in package.corpus.surah_info.items():
        for ayah in range(1, len(counts) + 1):
            verse = VerseRef(int(surah), ayah)
            words = package.words(verse)
            built = package.build(package.read(Script.UTHMANI, verse, words))
            performance = package.perform(
                built.score, all_join(len(built.score.words))
            )
            by_slot = {
                slot.id: word.location
                for word in built.score.words
                for slot in word.slots
            }
            for word in built.score.words:
                slots = word.slots
                for index, slot in enumerate(slots[1:-1], 1):
                    before, after = slots[index - 1], slots[index + 1]
                    if not (
                        slot.letter in {CanonLetter.WAW, CanonLetter.YA}
                        and slot.nucleus.is_silent
                        and before.nucleus.is_short
                        and before.nucleus.quality is Quality.A
                        and after.letter is CanonLetter.HAMZA
                    ):
                        continue
                    key = (str(word.location), slot.id.ordinal)
                    candidates.add(key)
                    ref = str(word.location)
                    if ref in LEEN_MAHMUZ_EXCLUSIONS:
                        families["excluded"] += 1
                    elif ref in SAWAT:
                        families["sawat"] += 1
                    else:
                        families["ordinary"] += 1
            emitted.update(
                (str(by_slot[occurrence.subjects[0]]),
                 occurrence.subjects[0].ordinal)
                for occurrence in performance.occurrences
                if occurrence.rule is Rule.MADD_LEEN_MAHMUZ
            )

    assert families == Counter({
        "ordinary": 297,
        "sawat": 5,
        "excluded": 2,
    })
    assert len(candidates) == 304
    assert len(emitted) == 302
    assert emitted <= candidates


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
    """Written article alifs, suppressed-alif prefix forms, and the two
    interrogative tokens close the register with the reviewed long bases."""
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
