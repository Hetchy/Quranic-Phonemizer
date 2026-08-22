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
    joining,
    through,
)


CASES = (
    # تِجَارَةٍ تُنجِيكُم
    Case(
        id="taa-jeem",
        site=Site(hafs=("61:10", (7, 8))),
        read=through(),
        phonemes=("t i ʒ a: rˤ aˤ t i ŋ", "t u ŋ ʒ i: k u m"),
        char_rules={"@kasratan": R("ikhfaa_haqiqi"), "ن": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ[1]": R("ikhfaa_haqiqi"), "ŋ[2]": R("ikhfaa_haqiqi")},
    ),
    # إِنسٌ قَبْلَهُم
    Case(
        id="seen-qaf",
        site=Site(hafs=("55:74", (3, 4))),
        read=through(),
        phonemes=("ʔ i ŋ s u ŋ", "q aˤ b Q l a h u m"),
        char_rules={"ن": R("ikhfaa_haqiqi"), "@dammatan": R("ikhfaa_haqiqi")},
        sound_rules={
            "ŋ[1]": R("ikhfaa_haqiqi"),
            "ŋ[2]": R("ikhfaa_haqiqi", "tafkheem"),
        },
    ),
    # بِقَدَرٍ فَأَنشَرْنَا
    Case(
        id="fa-sheen",
        site=Site(hafs=("43:11", (6, 7))),
        read=through(),
        phonemes=("b i q aˤ d a r i ŋ", "f a ʔ a ŋ ʃ a rˤ n a:"),
        char_rules={"@kasratan": R("ikhfaa_haqiqi"), "ن[1]": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ[1]": R("ikhfaa_haqiqi"), "ŋ[2]": R("ikhfaa_haqiqi")},
    ),
    # أَندَادًا ذَلِكَ
    Case(
        id="dal-thal",
        site=Site(hafs=("41:9", (11, 12))),
        read=through(),
        phonemes=("ʔ a ŋ d a: d a ŋ", "ð a: l i k"),
        char_rules={"ن": R("ikhfaa_haqiqi"), "@fathatan": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ[1]": R("ikhfaa_haqiqi"), "ŋ[2]": R("ikhfaa_haqiqi")},
    ),
    # مَعِيشَةً ضَنكًا
    Case(
        id="dad-kaf",
        site=Site(hafs=("20:124", (7, 8))),
        read=through(),
        phonemes=("m a ʕ i: ʃ a t a ŋ", "dˤ aˤ ŋ k a:"),
        char_rules={"@fathatan[1]": R("ikhfaa_haqiqi"), "ن": R("ikhfaa_haqiqi")},
        sound_rules={
            "ŋ[1]": R("ikhfaa_haqiqi", "tafkheem"),
            "ŋ[2]": R("ikhfaa_haqiqi"),
        },
    ),
    # حِينَئِذٍ تَنظُرُونَ
    Case(
        id="taa-zhaa",
        site=Site(hafs=("56:84", (2, 3))),
        read=through(),
        phonemes=("ħ i: n a ʔ i ð i ŋ", "t a ŋ ðˤ u rˤ u: n"),
        char_rules={"@kasratan": R("ikhfaa_haqiqi"), "ن[2]": R("ikhfaa_haqiqi")},
        sound_rules={
            "ŋ[1]": R("ikhfaa_haqiqi"),
            "ŋ[2]": R("ikhfaa_haqiqi", "tafkheem"),
        },
    ),
    # مَيِّتٍ فَأَنزَلْنَا
    Case(
        id="fa-zay",
        site=Site(hafs=("7:57", (16, 17))),
        read=through(),
        phonemes=("m a jj i t i ŋ", "f a ʔ a ŋ z a l n a:"),
        char_rules={"@kasratan": R("ikhfaa_haqiqi"), "ن[1]": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ[1]": R("ikhfaa_haqiqi"), "ŋ[2]": R("ikhfaa_haqiqi")},
    ),
    # قِنطَارًا فَلَا
    Case(
        id="tah-fa",
        site=Site(hafs=("4:20", (9, 10))),
        read=through(),
        phonemes=("q i ŋ tˤ aˤ: rˤ aˤ ŋ", "f a l a:"),
        char_rules={"ن": R("ikhfaa_haqiqi"), "@fathatan": R("ikhfaa_haqiqi")},
        sound_rules={
            "ŋ[1]": R("ikhfaa_haqiqi", "tafkheem"),
            "ŋ[2]": R("ikhfaa_haqiqi"),
        },
    ),
    # إِن تَنصُرُوا
    StateCase(
        id="taa-sad-boundary",
        site=Site(hafs=("47:7", (4, 5))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("ʔ i ŋ", "t a ŋ sˤ u rˤ u:"),
                char_rules={"ن[1]": R("ikhfaa_haqiqi"), "ن[2]": R("ikhfaa_haqiqi")},
                sound_rules={
                    "ŋ[1]": R("ikhfaa_haqiqi"),
                    "ŋ[2]": R("ikhfaa_haqiqi", "tafkheem"),
                },
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=4, waqf=(4, 5)),
                phonemes=("ʔ i n", "t a ŋ sˤ u rˤ u:"),
                char_rules={"ن[1]": R("izhar"), "ن[2]": R("ikhfaa_haqiqi")},
                sound_rules={"n": R("izhar"), "ŋ": R("ikhfaa_haqiqi", "tafkheem")},
                absent_char_rules={"ن[1]": R("ikhfaa_haqiqi")},
            ),
        },
    ),
    # وَٱلْأُنثَىٰ
    Case(
        id="tha",
        site=Site(hafs=("2:178", (13,))),
        read=isolated(),
        phonemes="w a l ʔ u ŋ θ a:",
        char_rules={"ن": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ": R("ikhfaa_haqiqi")},
    ),
    # نُـۨجِى
    Case(
        id="small-noon-jeem",
        site=Site(hafs=("21:88", (7,))),
        read=isolated(),
        phonemes="n u ŋ ʒ i:",
        char_rules={"@small_noon": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ": R("ikhfaa_haqiqi")},
    ),
    # حِينٍ فَتَلَقَّىٰ
    Case(
        id="verse-seam",
        site=Site(hafs=("2:36", (19,))),
        read=joining(),
        phonemes="ħ i: n i ŋ",
        char_rules={"@kasratan": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ": R("ikhfaa_haqiqi")},
    ),
    # مَنضُودٍ
    StateCase(
        id="emphatic-token",
        site=Site(hafs=("56:29", (2,))),
        states={
            "plain-render": Expect(
                read=isolated(),
                phonemes="m a ŋ dˤ u: d Q",
                char_rules={"ن": R("ikhfaa_haqiqi")},
                sound_rules={"ŋ": R("ikhfaa_haqiqi", "tafkheem")},
                extra_phonemes=(),
            ),
            "emphatic-render": Expect(
                read=isolated(),
                phonemes="m a ŋˤ dˤ u: d Q",
                char_rules={"ن": R("ikhfaa_haqiqi")},
                sound_rules={"ŋˤ": R("ikhfaa_haqiqi", "tafkheem")},
                extra_phonemes=("emphatic_ikhfaa",),
            ),
        },
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_ikhfaa_haqiqi(run):
    assert_case(run)
