from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick


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
    # ٱلْحَمْدُ
    wasl_case("article-qamariyyah", "1:2", 1, "ʔ a l ħ a m d Q"),
    # ٱلنَّاسِ
    wasl_case("article-shamsiyyah", "114:1", 4, "ʔ a ñ a: s", indopak_alif="ا[1]"),
    # ٱللَّهُ
    wasl_case("divine-name", "2:15", 1, "ʔ a lˤlˤ aˤ: h"),
    # ٱدْخُلُوا
    wasl_case(
        "verb-original-damma", "2:58", 3, "ʔ u d Q x u l u:",
        indopak_alif="ا[1]",
    ),
    # ٱذْهَبْ
    wasl_case("verb-kasra", "20:24", 1, "ʔ i ð h a b Q"),
    # ٱلْتَقَى
    wasl_case("form-eight", "3:155", 6, "ʔ i l t a q aˤ:"),
    # ٱمْشُوا
    wasl_case("temporary-damma", "38:6", 5, "ʔ i m ʃ u:", indopak_alif="ا[1]"),
    # ٱبْنَ
    wasl_case("ibn", "2:87", 11, "ʔ i b Q n"),
    # ٱبْنَتَ
    wasl_case("ibnat", "66:12", 2, "ʔ i b Q n a t"),
    # ٱمْرُؤٌ
    wasl_case(
        "imru", "4:176", 8, "ʔ i m rˤ u ʔ", "ʔ[1]",
        indopak_alif="ا[1]",
    ),
    # ٱمْرَأَةٌ
    wasl_case(
        "imraah", "4:12", 56, "ʔ i m rˤ aˤ ʔ a h", "ʔ[1]",
        indopak_alif="ا[1]", warsh_alif="ا",
    ),
    # ٱثْنَانِ
    wasl_case("ithnan", "5:106", 12, "ʔ i θ n a: n"),
    # ٱثْنَتَا
    wasl_case("ithnata", "2:60", 11, "ʔ i θ n a t a:", indopak_alif="ا[1]"),
    # ٱسْمُهُ
    wasl_case("ism", "2:114", 10, "ʔ i s m u h"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_wasl_start(run):
    assert_case(run)
