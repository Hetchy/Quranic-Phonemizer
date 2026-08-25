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
    # Warsh: وَعَدُوَّكُمُۥٓ أَوْلِيَآءَۖ
    Case(
        id="qata-a",
        site=Site(warsh=("60:1", (7, 8))),
        read=through(),
        phonemes=("w a ʕ a d u ww a k u m u:", "ʔ a w l i j a: ʔ"),
        char_rules={"@small_waw": R("madd_munfasil")},
        sound_rules={"u:": R("madd_munfasil")},
        absent_sound_rules={"u:": R("madd_silah")},
    ),
    # Warsh: وَإِيَّاكُمُۥٓ أَن
    Case(
        id="qata-a-after-i-pronoun",
        site=Site(warsh=("60:1", (20, 21))),
        read=through(),
        phonemes=("w a ʔ i jj a: k u m u:", "ʔ a n"),
        char_rules={"@small_waw": R("madd_munfasil")},
        sound_rules={"u:": R("madd_munfasil")},
    ),
    # Warsh: رَبِّكُمُۥٓۖ إِن
    StateCase(
        id="qata-i-boundaries",
        site=Site(warsh=("60:1", (24, 25))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("rˤ aˤ bb i k u m u:", "ʔ i n"),
                char_rules={"@small_waw": R("madd_munfasil")},
                sound_rules={"u:": R("madd_munfasil")},
            ),
            "host-ibtidaa": Expect(
                read=explicit(ibtidaa=24, waqf=25),
                phonemes=("rˤ aˤ bb i k u m u:", "ʔ i n"),
                char_rules={"@small_waw": R("madd_munfasil")},
                sound_rules={"u:": R("madd_munfasil")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=24, waqf=(24, 25)),
                phonemes=("rˤ aˤ bb i k u m", "ʔ i n"),
                absent_char_rules={"@small_waw": R("madd_munfasil", "madd_silah")},
            ),
        },
    ),
    # Warsh: إِن
    Case(
        id="next-word-ibtidaa",
        site=Site(warsh=("60:1", (25,))),
        read=isolated(),
        phonemes="ʔ i n",
        absent_sound_rules={"i": R("madd_munfasil")},
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
                sound_rules={"u[2]": R("iltiqa_haraka")},
                absent_sound_rules={"u[2]": R("madd_tabii", "madd_munfasil")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=4, waqf=(4, 5)),
                phonemes=("f a z a: d a h u m", "ʔ a lˤlˤ aˤ: h"),
                absent_sound_rules={"u": R("iltiqa_haraka")},
            ),
        },
    ),
    # Warsh: اَ۪تَّخَذتُّمُ اُ۬لْعِجْلَ
    StateCase(
        id="verbal-plural-before-wasl",
        site=Site(warsh=("2:51", (7, 8))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=(
                    "ʔ i tt a x aˤ ð t u m u",
                    "l ʕ i ʒ Q l",
                ),
                char_rules={"ا[2]": R("hamza_wasl_silent")},
                sound_rules={"u[2]": R("iltiqa_haraka")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=7, waqf=(7, 8)),
                phonemes=(
                    "ʔ i tt a x aˤ ð t u m",
                    "ʔ a l ʕ i ʒ Q l",
                ),
            ),
        },
    ),
    # Warsh: هُمْ يُوقِنُونَ
    StateCase(
        id="moving-onset",
        site=Site(warsh=("2:4", (11, 12))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("h u m", "j u: q i n u: n"),
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=11, waqf=(11, 12)),
                phonemes=("h u m", "j u: q i n u: n"),
            ),
        },
    ),
    # Warsh: هَآؤُمُ اُ۪قْرَءُواْ
    Case(
        id="lexical-haaum-negative",
        site=Site(warsh=("69:19", (7, 8))),
        read=through(),
        phonemes=("h a: ʔ u m u", "q Q rˤ aˤ ʔ u:"),
        absent_sound_rules={"u[2]": R("iltiqa_haraka", "madd_munfasil")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_mim_al_jam(run):
    assert_case(run)
