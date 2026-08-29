from __future__ import annotations

from collections import Counter

import pytest

from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.model.address import Location, Script, VerseRef
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.riwayat.warsh.hamza_meetings import rows_by_target
from quranic_phonemizer.riwayat.warsh.naql_script import latent_qata_badal_quality
from tests.support import (
    Case,
    R,
    Site,
    assert_case,
    case_runs,
    isolated,
    joining,
    loaded,
    reading,
)


CASES = (
    # Warsh: ءَادَمَ
    Case(
        id="ordinary",
        site=Site(warsh=("2:31", (2,))),
        read=isolated(),
        phonemes="ʔ a: d a m",
        char_rules={"ا": R("madd_badal")},
        sound_rules={"a:": R("madd_badal")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # Warsh: مَـَٔابٖۖ
    Case(
        id="pausal-arid-overlap",
        site=Site(warsh=("13:29", (8,))),
        read=isolated(),
        phonemes="m a ʔ a: b Q",
        char_rules={"ا": R("madd_badal", "madd_arid_lissukun")},
        sound_rules={"a:": R("madd_badal", "madd_arid_lissukun")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # Warsh: يُومِنُونَ
    Case(
        id="general-ibdal-is-not-badal",
        site=Site(warsh=("2:3", (2,))),
        read=isolated(),
        phonemes="j u: m i n u: n",
        char_rules={"و[1]": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"u:[1]": R("ibdal_hamza", "madd_tabii")},
        absent_sound_rules={"u:[1]": R("madd_badal")},
    ),
    # Warsh: يُوَ۬اخِذُ
    Case(
        id="ibdal-changed-badal",
        site=Site(warsh=("16:61", (2,))),
        read=isolated(),
        phonemes="j u w a: x i ð",
        char_rules={
            "و": R("ibdal_hamza"),
            "ا": R("madd_badal"),
        },
        sound_rules={
            "w": R("ibdal_hamza"),
            "a:": R("madd_badal"),
        },
        absent_sound_rules={
            "w": R("madd_badal"),
            "a:": R("ibdal_hamza", "madd_tabii"),
        },
    ),
    # Warsh: إِسْرَآءِيلَ
    Case(
        id="fixed-qasr-israel-keeps-badal",
        site=Site(warsh=("2:40", (2,))),
        read=isolated(),
        phonemes="ʔ i s rˤ aˤ: ʔ i: l",
        char_rules={"ي": R("madd_badal", "madd_arid_lissukun")},
        sound_rules={"i:": R("madd_badal", "madd_arid_lissukun")},
        absent_sound_rules={"i:": R("madd_tabii")},
    ),
    # Warsh: مَسْـُٔولاٗۖ
    Case(
        id="sakin-before-hamza-keeps-badal",
        site=Site(warsh=("17:34", (17,))),
        read=isolated(),
        phonemes="m a s ʔ u: l a:",
        char_rules={"و": R("madd_badal")},
        sound_rules={"u:": R("madd_badal")},
        absent_sound_rules={"u:": R("madd_tabii")},
    ),
)


MUGHAYYAR_BIN_NAQL_CASES = (
    # A-badal after an ordinary sakin: مَنَ اٰمَنَ
    Case(
        id="a-moved-haraka",
        site=Site(warsh=("9:18", (5, 6))),
        read=joining(),
        phonemes=("m a n", "a: m a n a"),
        char_rules={"ا": R("naql"), "@dagger_alif": R("madd_badal")},
        sound_rules={"a:": R("naql", "madd_badal")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # A-badal after tanwin: بَلَداً اٰمِناٗ
    Case(
        id="a-tanwin",
        site=Site(warsh=("2:126", (7, 8))),
        read=joining(),
        phonemes=("b a l a d a n", "a: m i n a"),
        char_rules={"ا[2]": R("naql"), "@dagger_alif": R("madd_badal")},
        sound_rules={"a:": R("naql", "madd_badal")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # A-badal across an ayah edge: رَدْماًۖ اٰتُونِے
    Case(
        id="a-ayah-edge",
        site=Site(warsh=("18:95", (12, 13))),
        read=joining(),
        phonemes=("rˤ aˤ d Q m a n", "a: t u: n i:"),
        char_rules={"ا[2]": R("naql"), "@dagger_alif": R("madd_badal")},
        sound_rules={"a:": R("naql", "madd_badal")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # U-badal after an ordinary sakin: فَقَدُ ا۟وتِيَ
    Case(
        id="u-moved-haraka",
        site=Site(warsh=("2:269", (8, 9))),
        read=joining(),
        phonemes=("f a q aˤ d", "u: t i j a"),
        char_rules={"ا": R("naql"), "و": R("madd_badal")},
        sound_rules={"u:": R("naql", "madd_badal")},
        absent_sound_rules={"u:": R("madd_tabii")},
    ),
    # I-badal after an ordinary sakin: قُلِ اِے
    Case(
        id="i-moved-haraka",
        site=Site(warsh=("10:53", (4, 5))),
        read=joining(),
        phonemes=("q u l", "i:"),
        char_rules={"ا": R("naql"), "ے": R("madd_badal")},
        sound_rules={"i:": R("naql", "madd_badal")},
        absent_sound_rules={"i:": R("madd_tabii")},
    ),
    # I-badal after tanwin: نَفْساً اِيمَٰنُهَا
    Case(
        id="i-tanwin",
        site=Site(warsh=("6:158", (22, 23))),
        read=joining(),
        phonemes=("n a f s a n", "i: m a: n u h a:"),
        char_rules={"ا[2]": R("naql"), "ي": R("madd_badal")},
        sound_rules={"i:": R("naql", "madd_badal")},
        absent_sound_rules={"i:": R("madd_tabii")},
    ),
    # I-badal across an ayah edge: قُرَيْشٍ اِيلَٰفِهِمْ
    Case(
        id="i-ayah-edge",
        site=Site(warsh=("106:1", (2, 3))),
        read=joining(),
        phonemes=("q u rˤ aˤ j ʃ i n", "i: l a: f i h i m"),
        char_rules={"ا": R("naql"), "ي[2]": R("madd_badal")},
        sound_rules={"i:": R("naql", "madd_badal")},
        absent_sound_rules={"i:": R("madd_tabii")},
    ),
)


MEETING_OWNED_INITIAL_SHAPES = frozenset({
    Location(2, 140, 14),
    Location(20, 22, 10),
    Location(58, 13, 1),
})


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_madd_badal(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(MUGHAYYAR_BIN_NAQL_CASES))
def test_warsh_madd_badal_mughayyar_bin_naql(run):
    assert_case(run)


def test_warsh_mughayyar_bin_naql_is_one_cross_word_bridge():
    case = next(
        item for item in MUGHAYYAR_BIN_NAQL_CASES if item.id == "a-tanwin"
    )
    address = case.site.address("warsh")
    result = reading(
        case.site,
        "warsh",
        Script.UTHMANI,
        **case.read.kwargs(address.words),
    )
    before, after = (word - 1 for word in address.words)
    merger = next(
        item for item in result._bundle.mergers
        if item.before_word_id.value == before
        and item.after_word_id.value == after
    )
    sound = result._bundle.sounds[merger.sound_id.value]
    rules = {
        result._bundle.rule_occurrences[item.value].rule_id.value
        for item in sound.rule_occurrence_ids
    }
    bridge = next(
        item for boundary in result._cells.boundaries for item in boundary.bridges
        if item.merger_id == merger.id
    )
    before_column = next(
        item for item in result._cells.words[before].columns
        if sound.id in item.presented_sound_ids
    )
    after_column = next(
        item for item in result._cells.words[after].columns
        if sound.id in item.owned_sound_ids
    )

    assert sound.word_id == merger.after_word_id
    assert rules == {"naql", "madd_badal", "tarqeeq"}
    assert bridge.before_column_ids == (before_column.id,)
    assert bridge.after_column_ids == (after_column.id,)
    assert bridge.sound.column_ids == (before_column.id, after_column.id)
    assert before_column.role.value in {"haraka", "tanween"}
    assert after_column.role.value == "madd"


def _mughayyar_overlaps(built, performance, candidates):
    by_slot = {
        slot.id: (word.location, slot)
        for word in built.score.words
        for slot in word.slots
    }
    badal = {
        occurrence.subjects[0]
        for occurrence in performance.occurrences
        if occurrence.rule is Rule.MADD_BADAL
    }
    for occurrence in performance.occurrences:
        if occurrence.rule is not Rule.NAQL or occurrence.subjects[0] not in badal:
            continue
        location, _ = by_slot[occurrence.subjects[0]]
        quality = candidates.get(location)
        if quality is not None:
            yield quality.name, by_slot[occurrence.subjects[1]][1].origin.value


@pytest.mark.slow
def test_warsh_mughayyar_bin_naql_register_reconciles():
    package = loaded("warsh")
    meeting_targets = rows_by_target()
    boundaries: Counter = Counter()
    qualities: Counter = Counter()
    hosts: Counter = Counter()

    for surah, ayah_counts in package.corpus.surah_info.items():
        for ayah in range(1, len(ayah_counts) + 1):
            verse = VerseRef(int(surah), ayah)
            words = package.words(verse)
            candidates = {
                location: quality
                for location, text in words
                if location.word > 1
                and (quality := latent_qata_badal_quality(text)) is not None
                and location not in meeting_targets
            }
            if not candidates:
                continue
            built = package.build(package.read(Script.UTHMANI, verse, words))
            performance = package.perform(
                built.score, all_join(len(built.score.words))
            )
            for quality, host in _mughayyar_overlaps(
                built, performance, candidates
            ):
                boundaries["within"] += 1
                qualities[quality] += 1
                hosts[host] += 1

    for surah, ayah_counts in package.corpus.surah_info.items():
        for ayah in range(2, len(ayah_counts) + 1):
            current = VerseRef(int(surah), ayah)
            current_words = package.words(current)
            if current_words[0][0] in meeting_targets:
                continue
            quality = latent_qata_badal_quality(current_words[0][1])
            if quality is None:
                continue
            previous = VerseRef(int(surah), ayah - 1)
            words = package.words(previous) + current_words
            built = package.build(package.read(Script.UTHMANI, previous, words))
            performance = package.perform(
                built.score, all_join(len(built.score.words))
            )
            candidates = {current_words[0][0]: quality}
            for found_quality, host in _mughayyar_overlaps(
                built, performance, candidates
            ):
                boundaries["ayah_edge"] += 1
                qualities[found_quality] += 1
                hosts[host] += 1

    initial_shapes = {
        location
        for location, entry in package.corpus.entries.items()
        if latent_qata_badal_quality(entry.text) is not None
    }
    assert initial_shapes & set(meeting_targets) == MEETING_OWNED_INITIAL_SHAPES
    assert boundaries == Counter({"within": 186, "ayah_edge": 4})
    assert qualities == Counter({"A": 174, "U": 13, "I": 3})
    assert hosts == Counter({"written": 144, "nunation": 46})
