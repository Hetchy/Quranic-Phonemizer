from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import Script
from tests.support import (
    Case,
    R,
    Site,
    assert_case,
    case_runs,
    isolated,
    pick,
    reading,
    through,
)


def qata_start_case(
    case_id: str,
    ref: str,
    word: int,
    phonemes: str,
    long_vowel: str,
    warsh_carrier: str,
) -> Case:
    """Ibtidaa on a wasl onset followed by a silent qata hamza: the qata
    hamza is replaced by a long vowel of the helping-vowel quality."""
    start = "hamza_wasl_kasra" if long_vowel.startswith("i") else "hamza_wasl_damma"
    return Case(
        id=case_id,
        site=Site.shared(ref, (word,)),
        read=isolated(),
        phonemes=phonemes,
        char_rules=pick(
            hafs_uthmani={
                "ٱ": R(start),
                "ئ" if warsh_carrier == "ي" else "ؤ": R("ibdal_hamza"),
            },
            hafs_indopak={"ا": R(start), "@hamza_mark": R("ibdal_hamza")},
            warsh_uthmani={
                "ا": R(start),
                warsh_carrier: R("ibdal_hamza", "madd_badal"),
            },
        ),
        sound_rules=pick(
            hafs={"ʔ": R(start), long_vowel: R("ibdal_hamza")},
            warsh={
                "ʔ": R(start),
                long_vowel: R("ibdal_hamza", "madd_badal"),
            },
        ),
    )


def wasl_case(
    case_id: str,
    ref: str,
    word: int,
    phonemes: str,
    hamza: str = "ʔ",
    indopak_alif: str = "ا",
    warsh_alif: str | None = None,
) -> Case:
    rule = {
        "a": "hamza_wasl_fatha",
        "i": "hamza_wasl_kasra",
        "u": "hamza_wasl_damma",
    }[phonemes.split()[1]]
    return Case(
        id=case_id,
        site=Site.shared(ref, (word,)),
        read=isolated(),
        phonemes=phonemes,
        char_rules=pick(
            hafs_uthmani={"ٱ": R(rule)},
            hafs_indopak={indopak_alif: R(rule)},
            warsh_uthmani={warsh_alif or indopak_alif: R(rule)},
        ),
        sound_rules={hamza: R(rule)},
    )


CASES = (
    # Hafs: ٱلْحَمْدُ
    # Warsh: اِ۬لْحَمْدُ
    wasl_case("article-qamariyyah", "1:2", 1, "ʔ a l ħ a m d Q"),
    # Hafs: ٱلنَّاسِ
    # Warsh: اِ۬لنَّاسِ
    wasl_case("article-shamsiyyah", "114:1", 4, "ʔ a ñ a: s", indopak_alif="ا[1]"),
    # Hafs: ٱللَّهُ
    # Warsh: اَ۬للَّهُ
    wasl_case("divine-name", "2:15", 1, "ʔ a lˤlˤ aˤ: h"),
    # Hafs: ٱدْخُلُوا۟
    # Warsh: اَ۟دْخُلُواْ
    wasl_case(
        "verb-original-damma", "2:58", 3, "ʔ u d Q x u l u:",
        indopak_alif="ا[1]",
    ),
    # Hafs: ٱذْهَبْ
    # Warsh: اَ۪ذْهَبِ
    wasl_case("verb-kasra", "20:24", 1, "ʔ i ð h a b Q"),
    # Hafs: ٱلْتَقَى
    # Warsh: اَ۪لْتَقَى
    wasl_case("form-eight", "3:155", 6, "ʔ i l t a q aˤ:"),
    # Hafs: ٱمْشُوا۟
    # Warsh: اِ۪مْشُواْ
    wasl_case("temporary-damma", "38:6", 5, "ʔ i m ʃ u:", indopak_alif="ا[1]"),
    # Hafs: ٱبْنَ
    # Warsh: اَ۪بْنَ
    wasl_case("ibn", "2:87", 11, "ʔ i b Q n"),
    # Hafs: ٱبْنَتَ
    # Warsh: اَ۪بْنَتَ
    wasl_case("ibnat", "66:12", 2, "ʔ i b Q n a t"),
    # Hafs: ٱمْرُؤٌا۟
    # Warsh: اِ۪مْرُؤٌاْ
    wasl_case(
        "imru", "4:176", 8, "ʔ i m rˤ u ʔ", "ʔ[1]",
        indopak_alif="ا[1]",
    ),
    # Hafs: ٱمْرَأَةٌ
    # Warsh: اِ۪مْرَأَةٞ
    wasl_case(
        "imraah", "4:12", 56, "ʔ i m rˤ aˤ ʔ a h", "ʔ[1]",
        indopak_alif="ا[1]", warsh_alif="ا",
    ),
    # Hafs: ٱثْنَانِ
    # Warsh: اِ۪ثْنَٰنِ
    wasl_case("ithnan", "5:106", 12, "ʔ i θ n a: n"),
    # Hafs: ٱثْنَتَا
    # Warsh: اُ۪ثْنَتَا
    wasl_case("ithnata", "2:60", 11, "ʔ i θ n a t a:", indopak_alif="ا[1]"),
    # Hafs: ٱسْمُهُۥ
    # Warsh: اَ۪سْمُهُۥ
    wasl_case("ism", "2:114", 10, "ʔ i s m u h"),
    # Hafs: ٱسْتَحَقَّ
    # Warsh: اَ۟سْتُحِقَّ
    Case(
        id="warsh-passive-delta",
        site=Site.shared("5:107", (12,)),
        read=isolated(),
        phonemes=pick(
            hafs="ʔ i s t a ħ a qq Q",
            warsh="ʔ u s t u ħ i qq Q",
        ),
        char_rules=pick(
            hafs_uthmani={"ٱ": R("hamza_wasl_kasra")},
            hafs_indopak={"ا": R("hamza_wasl_kasra")},
            warsh_uthmani={"ا": R("hamza_wasl_damma")},
        ),
        sound_rules=pick(
            hafs={"ʔ": R("hamza_wasl_kasra")},
            warsh={"ʔ": R("hamza_wasl_damma")},
        ),
    ),
    # Warsh: اُ۪تَّقُواْ
    Case(
        id="temporary-damm-taqwa",
        site=Site(warsh=("2:278", (4,))),
        read=isolated(),
        phonemes="ʔ i tt a q u:",
        char_rules={"ا[1]": R("hamza_wasl_kasra")},
        sound_rules={"ʔ": R("hamza_wasl_kasra")},
    ),
    # Hafs: ٱئْتُونِى
    # Warsh: اُ۪يتُونِے
    qata_start_case(
        "silent-qata-iituni", "10:79", 3, "ʔ i: t u: n i:", "i:[1]", "ي",
    ),
    # Hafs: ٱئْذَن
    # Warsh: اُ۪يذَن
    qata_start_case(
        "silent-qata-iidhan", "9:49", 4, "ʔ i: ð a n", "i:", "ي",
    ),
    # Hafs: ٱؤْتُمِنَ
    # Warsh: اِ۟وتُمِنَ
    qata_start_case(
        "silent-qata-uutumina", "2:283", 16, "ʔ u: t u m i n", "u:", "و",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_wasl_start(run):
    assert_case(run)


def test_warsh_joined_wasl_ibdal_is_one_cross_word_long_bridge():
    # Warsh: يَّقُولُ اُ۪يذَن
    site = Site(warsh=("9:49", (3, 4)))
    address = site.address("warsh")
    result = reading(
        site,
        "warsh",
        Script.UTHMANI,
        **through().kwargs(address.words),
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

    assert sound.token == "u:"
    assert rules == {"ibdal_hamza", "madd_tabii"}
    assert before_column.text == "ُ"
    assert before_column.role.value == "haraka"
    assert after_column.text == "و"
    assert after_column.role.value == "madd"
    assert after_column.status.value == "replaced"
    assert before_column.source_unit_ids
    assert after_column.source_unit_ids
    assert bridge.before_column_ids == (before_column.id,)
    assert bridge.after_column_ids == (after_column.id,)
    assert bridge.sound.column_ids == (before_column.id, after_column.id)
    assert all(
        not (column.status.value == "inserted" and column.text == "و")
        for column in result._cells.words[before].columns
    )
