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
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_inclination(run):
    assert_case(run)
