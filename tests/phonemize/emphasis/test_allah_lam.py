from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick, through


CASES = (
    # ٱللَّهِ
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
    # ءَاللَّهُ
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
    # ٱللَّهُمَّ
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
    # لِلَّهِ
    Case(
        id="li-prefix-light",
        site=Site.shared("1:2", (2,)),
        read=isolated(),
        phonemes="l i ll a: h",
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"ll": R("tafkheem"), "a:": R("tafkheem")},
    ),
    # بِٱللَّهِ
    Case(
        id="bi-prefix-light",
        site=Site.shared("2:8", (6,)),
        read=isolated(),
        phonemes="b i ll a: h",
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"ll": R("tafkheem"), "a:": R("tafkheem")},
    ),
    # قَالَ ٱللَّهُ
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
    # نَصْرُ ٱللَّهِ
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
    # بِسْمِ ٱللَّهِ
    Case(
        id="joined-after-kasra",
        site=Site(hafs=("1:1", (1, 2)), warsh=("27:30", (5, 6))),
        read=through(),
        phonemes=("b i s m i", "ll a: h"),
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"ll": R("tafkheem"), "a:": R("tafkheem")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_allah_lam(run):
    assert_case(run)
