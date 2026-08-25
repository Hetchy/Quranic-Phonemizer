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
    isolated,
    joining,
)


CASES = (
    # Warsh: طَه۪ۖ
    Case(
        id="taha-kubra-collapsed",
        site=Site(warsh=("20:1", (1,))),
        read=isolated(),
        phonemes="tˤ aˤ: h ɛ:",
        char_rules={"هي/@madd": R("imala", "madd_tabii")},
        sound_rules={"ɛ:": R("imala", "madd_tabii")},
        extra_phonemes=(),
    ),
    # Warsh: طَه۪ۖ
    Case(
        id="taha-kubra-rendered",
        site=Site(warsh=("20:1", (1,))),
        read=isolated(),
        phonemes="tˤ aˤ: h e:",
        char_rules={"هي/@madd": R("imala", "madd_tabii")},
        sound_rules={"e:": R("imala", "madd_tabii")},
        extra_phonemes=("imala",),
    ),
    # Warsh: ح۪مِٓۖ
    Case(
        id="hawamim-haa",
        site=Site(warsh=("40:1", (1,))),
        read=isolated(),
        phonemes="ħ ɛ: m i: m",
        char_rules={"حا/@madd": R("taqlil", "madd_tabii")},
        sound_rules={"ɛ:": R("taqlil", "madd_tabii")},
    ),
    # Warsh: كَٓه۪ي۪عَٓصَٓۖ
    Case(
        id="maryam-haa-yaa-default",
        site=Site(warsh=("19:1", (1,))),
        read=isolated(),
        phonemes="k a: f h ɛ: j ɛ: ʕ a j ŋ sˤ aˤ: d Q",
        char_rules={
            "ها/@madd": R("taqlil", "madd_tabii"),
            "يا/@madd": R("taqlil", "madd_tabii"),
        },
        sound_rules={
            "ɛ:[1]": R("taqlil", "madd_tabii"),
            "ɛ:[2]": R("taqlil", "madd_tabii"),
        },
    ),
    # Warsh: بِالْهُد۪ىٰ
    Case(
        id="ordinary-dhat-yaa-default",
        site=Site(warsh=("2:16", (5,))),
        read=isolated(),
        phonemes="b i l h u d ɛ:",
        char_rules={"ى": R("taqlil", "madd_tabii")},
        sound_rules={"ɛ:": R("taqlil", "madd_tabii")},
    ),
    # Warsh: هُدىٗ
    StateCase(
        id="dhat-yaa-fathatan-mask",
        site=Site(warsh=("2:5", (3,))),
        states={
            "joined": Expect(
                read=joining(),
                phonemes="h u d a",
                absent_char_rules={"ى": R("taqlil", "madd_iwad")},
                absent_sound_rules={"a": R("taqlil", "madd_iwad")},
            ),
            "stopped": Expect(
                read=isolated(),
                phonemes="h u d ɛ:",
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
    # Warsh: يَسِٓۖ
    Case(
        id="yaseen-yaa-default-fath",
        site=Site(warsh=("36:1", (1,))),
        read=isolated(),
        phonemes="j a: s i: n",
        absent_char_rules={"يا/@madd": R("taqlil", "imala")},
        absent_sound_rules={"a:": R("taqlil", "imala")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_inclination(run):
    assert_case(run)
