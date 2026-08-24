from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick, through


CASES = (
    # Hafs: ٱللَّهِ
    # Warsh: اَ۬للَّهُ
    Case(
        id="standalone-heavy",
        site=Site(hafs=("1:1", (2,)), warsh=("2:15", (1,))),
        read=isolated(),
        phonemes="ʔ a lˤlˤ aˤ: h",
        char_rules=pick(
            hafs={"ل[2]": R("tafkheem"), "@fatha": R("tafkheem")},
            hafs_indopak={"ل[2]": R("tafkheem"), "@dagger_alif": R("tafkheem")},
            warsh_uthmani={"ل[2]": R("tafkheem"), "@fatha": R("tafkheem")},
        ),
        sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
    ),
    # Hafs: ءَآللَّهُ
    # Warsh: آٰللَّهُ
    Case(
        id="interrogative-heavy",
        site=Site.shared("10:59", (14,)),
        read=isolated(),
        phonemes="ʔ a: lˤlˤ aˤ: h",
        char_rules=pick(
            hafs={"ل[2]": R("tafkheem"), "@fatha[2]": R("tafkheem")},
            hafs_indopak={"ل[2]": R("tafkheem"), "@dagger_alif[2]": R("tafkheem")},
            warsh_uthmani={"ل[2]": R("tafkheem"), "@fatha": R("tafkheem")},
        ),
        sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
    ),
    # Hafs: ٱللَّهُمَّ
    # Warsh: اِ۬للَّهُمَّ
    Case(
        id="allahumma-heavy",
        site=Site.shared("3:26", (2,)),
        read=isolated(),
        phonemes="ʔ a lˤlˤ aˤ: h u m̃",
        char_rules=pick(
            hafs={"ل[2]": R("tafkheem"), "@fatha[1]": R("tafkheem")},
            hafs_indopak={"ل[2]": R("tafkheem"), "@dagger_alif": R("tafkheem")},
            warsh_uthmani={"ل[2]": R("tafkheem"), "@fatha[1]": R("tafkheem")},
        ),
        sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
    ),
    # Hafs: لِلَّهِ
    # Warsh: لِلهِ
    Case(
        id="li-prefix-light",
        site=Site.shared("1:2", (2,)),
        read=isolated(),
        phonemes="l i ll a: h",
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"ll": R("tafkheem"), "a:": R("tafkheem")},
    ),
    # Hafs: بِٱللَّهِ
    # Warsh: بِاللَّهِ
    Case(
        id="bi-prefix-light",
        site=Site.shared("2:8", (6,)),
        read=isolated(),
        phonemes="b i ll a: h",
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"ll": R("tafkheem"), "a:": R("tafkheem")},
    ),
    # Hafs: قَالَ ٱللَّهُ
    # Warsh: قَالَ اَ۬للَّهُ
    Case(
        id="joined-after-fatha",
        site=Site.shared("5:119", (1, 2)),
        read=through(),
        phonemes=("q aˤ: l a", "lˤlˤ aˤ: h"),
        char_rules=pick(
            hafs={"ل[3]": R("tafkheem"), "@fatha[3]": R("tafkheem")},
            hafs_indopak={"ل[3]": R("tafkheem"), "@dagger_alif": R("tafkheem")},
            warsh_uthmani={"ل[3]": R("tafkheem"), "@fatha[3]": R("tafkheem")},
        ),
        sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:[2]": R("tafkheem")},
    ),
    # Hafs: نَصْرُ ٱللَّهِ
    # Warsh: نَصْرُ اُ۬للَّهِ
    Case(
        id="joined-after-damma",
        site=Site.shared("110:1", (3, 4)),
        read=through(),
        phonemes=("n a sˤ rˤ u", "lˤlˤ aˤ: h"),
        char_rules=pick(
            hafs={"ل[2]": R("tafkheem"), "@fatha[2]": R("tafkheem")},
            hafs_indopak={"ل[2]": R("tafkheem"), "@dagger_alif": R("tafkheem")},
            warsh_uthmani={"ل[2]": R("tafkheem"), "@fatha[2]": R("tafkheem")},
        ),
        sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
    ),
    # Hafs: بِسْمِ ٱللَّهِ
    # Warsh: بِسْمِ اِ۬للَّهِ
    Case(
        id="joined-after-kasra",
        site=Site(hafs=("1:1", (1, 2)), warsh=("27:30", (5, 6))),
        read=through(),
        phonemes=("b i s m i", "ll a: h"),
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"ll": R("tafkheem"), "a:": R("tafkheem")},
    ),
    # Hafs: يُضْلِلْهُ
    # Warsh: يُضْلِلْهُۖ
    Case(
        id="non-divine-lam-sequence",
        site=Site.shared("6:39", (11,)),
        read=isolated(),
        phonemes="j u dˤ l i l h",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_allah_lam(run):
    assert_case(run)
