from __future__ import annotations

import pytest

from tests.support import (
    Case,
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    explicit,
    isolated,
    through,
)

CASES = (
    # Warsh: بِالْهُد۪ىٰ
    Case(
        id="ordinary-dhat-yaa-default",
        site=Site(warsh=("2:16", (5,))),
        read=isolated(),
        phonemes="b i l h u d ɛ:",
        char_rules={"ى": R("taqlil", "madd_tabii")},
        sound_rules={"ɛ:": R("taqlil", "madd_tabii")},
    ),
    # Warsh: هُدىٗ مِّن
    StateCase(
        id="dhat-yaa-fathatan-mask",
        site=Site(warsh=("2:5", (3, 4))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("h u d a", "m̃ i n"),
                absent_char_rules={"ى": R("taqlil", "madd_iwad")},
                absent_sound_rules={"a": R("taqlil", "madd_iwad")},
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=3, waqf=(3, 4)),
                phonemes=("h u d ɛ:", "m i n"),
                char_rules={"ى": R("taqlil", "madd_iwad", "madd_tabii")},
                sound_rules={"ɛ:": R("taqlil", "madd_iwad", "madd_tabii")},
            ),
        },
    ),
    # Warsh: اَ۬لَاعْلَي
    Case(
        id="unmarked-fixed-verse-head",
        site=Site(warsh=("87:1", (4,))),
        read=isolated(),
        phonemes="ʔ a l a ʕ l ɛ:",
        char_rules={"ي": R("taqlil", "madd_tabii")},
        sound_rules={"ɛ:": R("taqlil", "madd_tabii")},
    ),
    # Warsh: حَتَّىٰ
    Case(
        id="hatta-fixed-fath",
        site=Site(warsh=("2:55", (7,))),
        read=isolated(),
        phonemes="ħ a tt a:",
        absent_char_rules={"ى": R("taqlil", "imala")},
        absent_sound_rules={"a:": R("taqlil", "imala")},
    ),
    # Warsh: ءَات۪يٰنِۦَ
    Case(
        id="yaa-zawaid-host",
        site=Site(warsh=("27:36", (8,))),
        read=isolated(),
        phonemes="ʔ a: t ɛ: n",
        char_rules={"ي": R("taqlil", "madd_arid_lissukun")},
        sound_rules={"ɛ:": R("taqlil", "madd_arid_lissukun")},
    ),
    # Warsh: ر۪ء۪اهُ
    Case(
        id="raa-seen-short-taqlil-default-off",
        site=Site(warsh=("81:23", (2,))),
        read=isolated(),
        phonemes="r a ʔ ɛ: h",
        extra_phonemes=(),
        sound_rules={
            "r": R("tarqeeq"),
            "a": R("taqlil"),
            "ɛ:": R("taqlil", "madd_badal"),
        },
    ),
    # Warsh: ر۪ء۪اهُ
    Case(
        id="raa-seen-short-taqlil-enabled",
        site=Site(warsh=("81:23", (2,))),
        read=isolated(),
        phonemes="r ɛ ʔ ɛ: h",
        extra_phonemes=("taqlil_short",),
        sound_rules={
            "r": R("tarqeeq"),
            "ɛ": R("taqlil"),
            "ɛ:": R("taqlil", "madd_badal"),
        },
    ),
    # Warsh: رَءَا اَ۬لشَّمْسَ
    StateCase(
        id="raa-seen-before-sakin",
        site=Site(warsh=("6:78", (2, 3))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("rˤ a ʔ a", "ʃʃ a m s"),
                extra_phonemes=("taqlil_short",),
                absent_sound_rules={
                    "a[1]": R("taqlil"),
                    "a[2]": R("taqlil"),
                },
            ),
            "stopped-off": Expect(
                read=explicit(ibtidaa=2, waqf=(2, 3)),
                phonemes=("r a ʔ ɛ:", "ʔ a ʃʃ a m s"),
                extra_phonemes=(),
                sound_rules={
                    "r": R("tarqeeq"),
                    "a[1]": R("taqlil"),
                    "ɛ:": R("taqlil", "madd_badal"),
                },
            ),
            "stopped-on": Expect(
                read=explicit(ibtidaa=2, waqf=(2, 3)),
                phonemes=("r ɛ ʔ ɛ:", "ʔ a ʃʃ a m s"),
                extra_phonemes=("taqlil_short",),
                sound_rules={
                    "r": R("tarqeeq"),
                    "ɛ": R("taqlil"),
                    "ɛ:": R("taqlil", "madd_badal"),
                },
            ),
        },
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_inclination(run):
    assert_case(run)
