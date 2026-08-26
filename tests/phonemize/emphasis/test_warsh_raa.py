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


MOVING_STRUCTURAL_CASES = (
    # Warsh: قِرَدَةً
    Case(
        id="direct-original-kasra",
        site=Site(warsh=("2:65", (11,))),
        read=isolated(),
        phonemes="q i r a d a h",
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a[1]": R("tarqeeq")},
    ),
    # Warsh: اُ۬لْخَيْرَٰتِۖ
    Case(
        id="sakin-yaa-and-carrier-coloring",
        site=Site(warsh=("2:148", (6,))),
        read=isolated(),
        phonemes="ʔ a l x aˤ j r a: t",
        char_rules={
            "ر": R("tarqeeq"),
            "@dagger_alif": R("tarqeeq", "madd_arid_lissukun"),
        },
        sound_rules={
            "r": R("tarqeeq"),
            "a:": R("tarqeeq", "madd_arid_lissukun"),
        },
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: ذِكْرَ رَبِّهِۦ
    Case(
        id="one-sakin-extension",
        site=Site(warsh=("12:42", (12, 13))),
        read=through(),
        phonemes=("ð i k r a", "rˤ aˤ bb i h"),
        char_rules={"ر[1]": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a": R("tarqeeq")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: إِخْرَاجُهُمُۥٓۖ
    Case(
        id="khaa-intervening-exception",
        site=Site(warsh=("2:85", (22,))),
        read=isolated(),
        phonemes="ʔ i x r a: ʒ u h u m",
        char_rules={"ر": R("tarqeeq"), "ا": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a:": R("tarqeeq")},
    ),
    # Warsh: قِطْراٗۖ
    Case(
        id="intervening-isti-laa-blocker",
        site=Site(warsh=("18:96", (19,))),
        read=isolated(),
        phonemes="q i tˤ Q rˤ aˤ:",
        char_rules={
            "ر": R("tafkheem"),
            "ا": R("tafkheem", "madd_iwad", "madd_tabii"),
        },
        sound_rules={
            "rˤ": R("tafkheem"),
            "aˤ:": R("tafkheem", "madd_iwad", "madd_tabii"),
        },
    ),
    # Warsh: لِرُقِيِّكَ
    Case(
        id="following-isti-laa-blocker",
        site=Site(warsh=("17:93", (13,))),
        read=isolated(),
        phonemes="l i rˤ u q i jj i k",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
    # Warsh: رَبِّهِۦ
    Case(
        id="ordinary-open-heavy",
        site=Site(warsh=("12:42", (13,))),
        read=isolated(),
        phonemes="rˤ aˤ bb i h",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem"), "aˤ": R("tafkheem")},
    ),
)


SAKIN_AND_BOUNDARY_CASES = (
    # Warsh: خَيْرَ اَ۬لزَّادِ
    StateCase(
        id="final-open-raa-recomputed-at-waqf",
        site=Site(warsh=("2:197", (24, 25))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("x aˤ j r a", "zz a: d Q"),
                char_rules={"ر": R("tarqeeq")},
                sound_rules={"r": R("tarqeeq"), "a": R("tarqeeq")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=24, waqf=(24, 25)),
                phonemes=("x aˤ j r", "ʔ a zz a: d Q"),
                char_rules={"ر": R("tarqeeq")},
                sound_rules={"r": R("tarqeeq")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
    ),
    # Warsh: وَاذْكُرْ فِے
    Case(
        id="sakin-raa-governed-by-damma",
        site=Site(warsh=("19:16", (1, 2))),
        read=through(),
        phonemes=("w a ð k u rˤ", "f i:"),
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
    # Warsh: اِ۪رْتَبْتُمْ
    Case(
        id="wasl-start-kasra-is-not-original",
        site=Site(warsh=("5:106", (35,))),
        read=isolated(),
        phonemes="ʔ i rˤ t a b Q t u m",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
    # Warsh: اَمِ اِ۪رْتَابُوٓاْ
    Case(
        id="cross-word-kasra-is-not-original",
        site=Site(warsh=("24:50", (4, 5))),
        read=through(),
        phonemes=("ʔ a m i", "rˤ t a: b u:"),
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
)


FIXED_LEXICAL_EXCLUSION_CASES = (
    # Warsh: إِسْرَآءِيلَ
    Case(
        id="israil-fixed-heavy",
        site=Site(warsh=("2:40", (2,))),
        read=isolated(),
        phonemes="ʔ i s rˤ aˤ: ʔ i: l",
        char_rules={"ر": R("tafkheem"), "ا": R("tafkheem", "madd_muttasil")},
        sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem", "madd_muttasil")},
    ),
    # Warsh: إِبْرَٰهِيمَ
    Case(
        id="ibrahim-fixed-heavy",
        site=Site(warsh=("2:125", (10,))),
        read=isolated(),
        phonemes="ʔ i b Q rˤ aˤ: h i: m",
        char_rules={
            "ر": R("tafkheem"),
            "@dagger_alif": R("tafkheem", "madd_tabii"),
        },
        sound_rules={
            "rˤ": R("tafkheem"),
            "aˤ:": R("tafkheem", "madd_tabii"),
        },
    ),
    # Warsh: عِمْرَٰنَ
    Case(
        id="imran-fixed-heavy",
        site=Site(warsh=("3:33", (9,))),
        read=isolated(),
        phonemes="ʕ i m rˤ aˤ: n",
        char_rules={
            "ر": R("tafkheem"),
            "@dagger_alif": R("tafkheem", "madd_arid_lissukun"),
        },
        sound_rules={
            "rˤ": R("tafkheem"),
            "aˤ:": R("tafkheem", "madd_arid_lissukun"),
        },
    ),
    # Warsh: ضِرَاراٗ
    Case(
        id="repeated-raa-fixed-heavy",
        site=Site(warsh=("2:231", (13,))),
        read=isolated(),
        phonemes="dˤ i rˤ aˤ: rˤ aˤ:",
        char_rules={"ر[1]": R("tafkheem"), "ر[2]": R("tafkheem")},
        sound_rules={"rˤ[1]": R("tafkheem"), "rˤ[2]": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: حِذْرَهُمْ
    Case(
        id="hidhrahum-fixed-light",
        site=Site(warsh=("4:102", (26,))),
        read=isolated(),
        phonemes="ħ i ð r a h u m",
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq"), "a": R("tarqeeq")},
    ),
    # Warsh: اَ۬لْعَشِيرُۖ
    Case(
        id="other-ashir-fixed-light",
        site=Site(warsh=("22:13", (10,))),
        read=isolated(),
        phonemes="ʔ a l ʕ a ʃ i: r",
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq")},
    ),
    # Warsh: فَاحْذَرْهُمْۖ
    Case(
        id="hidhrahum-lookalike-keeps-structural-weight",
        site=Site(warsh=("63:4", (18,))),
        read=isolated(),
        phonemes="f a ħ ð a rˤ h u m",
        char_rules={"ر": R("tafkheem")},
        sound_rules={"rˤ": R("tafkheem")},
    ),
)


@pytest.mark.parametrize("run", case_runs(MOVING_STRUCTURAL_CASES))
def test_moving_structural_law(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(SAKIN_AND_BOUNDARY_CASES))
def test_sakin_and_boundary_law(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(FIXED_LEXICAL_EXCLUSION_CASES))
def test_fixed_lexical_exclusions(run):
    assert_case(run)
