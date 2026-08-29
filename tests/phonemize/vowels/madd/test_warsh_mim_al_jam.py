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
    through,
)

CASES = (
    # Warsh: وَعَدُوَّكُمُۥٓ أَوْلِيَآءَۖ
    Case(
        id="qata-a",
        site=Site(warsh=("60:1", (7, 8))),
        read=through(),
        phonemes=("w a ʕ a d u ww a k u m u:", "ʔ a w l i j a: ʔ"),
        char_rules={"@small_waw": R("madd_mim_al_jam", "madd_munfasil")},
        sound_rules={"u:": R("madd_mim_al_jam", "madd_munfasil")},
        absent_sound_rules={"u:": R("madd_silah")},
    ),
    # Warsh: وَإِيَّاكُمُۥٓ أَن
    Case(
        id="qata-a-after-i-pronoun",
        site=Site(warsh=("60:1", (20, 21))),
        read=through(),
        phonemes=("w a ʔ i jj a: k u m u:", "ʔ a n"),
        char_rules={"@small_waw": R("madd_mim_al_jam", "madd_munfasil")},
        sound_rules={"u:": R("madd_mim_al_jam", "madd_munfasil")},
    ),
    # Warsh: رَبِّكُمُۥٓۖ إِن
    StateCase(
        id="qata-i-boundaries",
        site=Site(warsh=("60:1", (24, 25))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("rˤ aˤ bb i k u m u:", "ʔ i n"),
                char_rules={"@small_waw": R("madd_mim_al_jam", "madd_munfasil")},
                sound_rules={"u:": R("madd_mim_al_jam", "madd_munfasil")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=24, waqf=(24, 25)),
                phonemes=("rˤ aˤ bb i k u m", "ʔ i n"),
                absent_char_rules={
                    "@small_waw": R(
                        "madd_mim_al_jam", "madd_munfasil", "madd_silah"
                    )
                },
            ),
        },
    ),
    # Warsh: فَزَادَهُمُ اُ۬للَّهُ
    StateCase(
        id="before-wasl",
        site=Site(warsh=("2:10", (4, 5))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("f a z a: d a h u m u", "lˤlˤ aˤ: h"),
                char_rules={"ا[2]": R("hamza_wasl_silent")},
                absent_sound_rules={
                    "u[2]": R(
                        "iltiqa_haraka", "madd_mim_al_jam",
                        "madd_tabii", "madd_munfasil",
                    )
                },
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=4, waqf=(4, 5)),
                phonemes=("f a z a: d a h u m", "ʔ a lˤlˤ aˤ: h"),
                absent_sound_rules={"u": R("iltiqa_haraka", "madd_mim_al_jam")},
            ),
        },
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_mim_al_jam(run):
    assert_case(run)
