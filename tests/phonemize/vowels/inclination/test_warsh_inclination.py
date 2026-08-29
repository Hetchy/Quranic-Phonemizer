from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Case,
    Expect,
    R,
    Site,
    StateCase,
    VariantCase,
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


QUALITY_VARIANT_CASES = (
    # Warsh: بِالْهُد۪ىٰ
    VariantCase(
        id="dhat-yaa-ordinary",
        site=Site(warsh=("2:16", (5,))),
        selector=KhilafId.DHAT_YAA,
        faces={
            "taqlil": Expect(
                read=isolated(),
                phonemes="b i l h u d ɛ:",
                char_rules={"ى": R("taqlil", "madd_tabii")},
                sound_rules={"ɛ:": R("taqlil", "madd_tabii")},
            ),
            "fath": Expect(
                read=isolated(),
                phonemes="b i l h u d a:",
                absent_char_rules={"ى": R("taqlil")},
                absent_sound_rules={"a:": R("taqlil")},
            ),
        },
        default="taqlil",
    ),
    # Warsh: هُدىٗ مِّن
    VariantCase(
        id="dhat-yaa-fathatan",
        site=Site(warsh=("2:5", (3, 4))),
        selector=KhilafId.DHAT_YAA,
        faces={
            "taqlil": Expect(
                read=explicit(ibtidaa=3, waqf=(3, 4)),
                phonemes=("h u d ɛ:", "m i n"),
                char_rules={"ى": R("taqlil", "madd_iwad", "madd_tabii")},
                sound_rules={"ɛ:": R("taqlil", "madd_iwad", "madd_tabii")},
            ),
            "fath": Expect(
                read=explicit(ibtidaa=3, waqf=(3, 4)),
                phonemes=("h u d a:", "m i n"),
                absent_char_rules={"ى": R("taqlil")},
                absent_sound_rules={"a:": R("taqlil")},
            ),
        },
        default="taqlil",
        masked=Expect(
            read=through(),
            phonemes=("h u d a", "m̃ i n"),
            absent_char_rules={"ى": R("taqlil")},
            absent_sound_rules={"a": R("taqlil")},
        ),
    ),
    # Warsh: اَر۪يٰكَهُمْ
    VariantCase(
        id="arakahum-couples-the-raa-weight",
        site=Site(warsh=("8:43", (8,))),
        selector=KhilafId.ARAKAHUM,
        faces={
            "taqlil": Expect(
                read=isolated(),
                phonemes="ʔ a r ɛ: k a h u m",
                char_rules={"ر": R("tarqeeq"), "ي": R("taqlil")},
                sound_rules={"r": R("tarqeeq"), "ɛ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "fath": Expect(
                read=isolated(),
                phonemes="ʔ a rˤ aˤ: k a h u m",
                char_rules={"ر": R("tafkheem")},
                sound_rules={"rˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
                absent_sound_rules={"aˤ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="taqlil",
    ),
    # Warsh: وَالْج۪ارِ
    VariantCase(
        id="al-jar-alif-before-final-raa",
        site=Site(warsh=("4:36", (13,))),
        selector=KhilafId.AL_JAR,
        faces={
            "taqlil": Expect(
                read=isolated(),
                phonemes="w a l ʒ ɛ: r",
                char_rules={"ا[2]": R("taqlil")},
                sound_rules={"ɛ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "fath": Expect(
                read=isolated(),
                phonemes="w a l ʒ a: rˤ",
                absent_char_rules={"ا[2]": R("taqlil")},
                absent_sound_rules={"a:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="taqlil",
    ),
    # Warsh: جَبّ۪ارِينَ
    VariantCase(
        id="jabbarin",
        site=Site(warsh=("5:22", (6,))),
        selector=KhilafId.JABBARIN,
        faces={
            "taqlil": Expect(
                read=isolated(),
                phonemes="ʒ a bb ɛ: r i: n",
                sound_rules={"ɛ:": R("taqlil")},
            ),
            "fath": Expect(
                read=isolated(),
                phonemes="ʒ a bb a: r i: n",
                absent_sound_rules={"a:": R("taqlil")},
            ),
        },
        default="taqlil",
    ),
    # Warsh: وَضُحَيٰهَا
    VariantCase(
        id="haa-verse-head-ending-only",
        site=Site(warsh=("91:1", (2,))),
        selector=KhilafId.HAA_VERSE_HEADS,
        faces={
            "fath": Expect(
                read=isolated(),
                phonemes="w a dˤ u ħ a j a: h a:",
                absent_sound_rules={"a:[2]": R("taqlil")},
            ),
            "taqlil": Expect(
                read=isolated(),
                phonemes="w a dˤ u ħ a j a: h ɛ:",
                sound_rules={"ɛ:": R("taqlil")},
                absent_sound_rules={"a:": R("taqlil")},
            ),
        },
        default="fath",
    ),
    # Warsh: كَٓه۪ي۪عَٓصَٓ
    VariantCase(
        id="maryam-haa-yaa-one-pair",
        site=Site(warsh=("19:1", (1,))),
        selector=KhilafId.MARYAM_HAA_YAA,
        faces={
            "taqlil": Expect(
                read=isolated(),
                phonemes="k a: f h ɛ: j ɛ: ʕ a j ŋ sˤ aˤ: d Q",
                extra_phonemes=("emphatic_fatha",),
            ),
            "fath": Expect(
                read=isolated(),
                phonemes="k a: f h a: j a: ʕ a j ŋ sˤ aˤ: d Q",
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="taqlil",
    ),
    # Warsh: يَسِٓ
    VariantCase(
        id="yaseen-yaa",
        site=Site(warsh=("36:1", (1,))),
        selector=KhilafId.YASEEN_YAA,
        faces={
            "fath": Expect(read=isolated(), phonemes="j a: s i: n"),
            "taqlil": Expect(
                read=isolated(),
                phonemes="j ɛ: s i: n",
                sound_rules={"ɛ:": R("taqlil")},
            ),
        },
        default="fath",
    ),
)


COUPLED_VARIANT_CASES = (
    # Warsh: صَلّ۪ىٰۖ
    VariantCase(
        id="coupled-verse-head",
        site=Site(warsh=("75:31", (4,))),
        selector=KhilafId.LAM_VERSE_HEADS,
        faces={
            "taqlil_tarqiq": Expect(
                read=isolated(),
                phonemes="sˤ aˤ ll ɛ:",
                char_rules={"ل": R("tarqeeq"), "ى": R("taqlil")},
                sound_rules={"ll": R("tarqeeq"), "ɛ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "fath_tafkheem": Expect(
                read=isolated(),
                phonemes="sˤ aˤ lˤlˤ aˤ:",
                char_rules={"ل": R("tafkheem")},
                sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
                absent_sound_rules={"aˤ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="taqlil_tarqiq",
    ),
    # Warsh: يَصْلَيٰهَا
    VariantCase(
        id="coupled-dhat-yaa-medial-alif",
        site=Site(warsh=("17:18", (16,))),
        selector=KhilafId.LAM_DHAT_YAA,
        faces={
            "fath_tafkheem": Expect(
                read=isolated(),
                phonemes="j a sˤ lˤ aˤ j a: h a:",
                char_rules={"ل": R("tafkheem")},
                sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "taqlil_tarqiq": Expect(
                read=isolated(),
                phonemes="j a sˤ l a j ɛ: h a:",
                char_rules={"ل": R("tarqeeq")},
                sound_rules={"l": R("tarqeeq"), "ɛ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="fath_tafkheem",
    ),
    # Warsh: يَصْلَى اَ۬لنَّارَ
    VariantCase(
        id="coupled-iltiqa-mask",
        site=Site(warsh=("87:12", (2, 3))),
        selector=KhilafId.LAM_DHAT_YAA,
        faces={
            "fath_tafkheem": Expect(
                read=explicit(ibtidaa=2, waqf=(2, 3)),
                phonemes=("j a sˤ lˤ aˤ:", "ʔ a ñ a: rˤ"),
                char_rules={"ل[1]": R("tafkheem")},
                sound_rules={"lˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "taqlil_tarqiq": Expect(
                read=explicit(ibtidaa=2, waqf=(2, 3)),
                phonemes=("j a sˤ l ɛ:", "ʔ a ñ a: rˤ"),
                char_rules={"ل[1]": R("tarqeeq")},
                sound_rules={"l": R("tarqeeq"), "ɛ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="fath_tafkheem",
        masked=Expect(
            read=through(),
            phonemes=("j a sˤ lˤ aˤ", "ñ a: rˤ"),
            char_rules={"ل[1]": R("tafkheem")},
            sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
            absent_sound_rules={"aˤ": R("taqlil")},
            extra_phonemes=("emphatic_fatha",),
        ),
    ),
    # Warsh: مُصَلّىٗۖ وَعَهِدْنَآ
    VariantCase(
        id="coupled-fathatan-mask",
        site=Site(warsh=("2:125", (11, 12))),
        selector=KhilafId.LAM_DHAT_YAA,
        faces={
            "fath_tafkheem": Expect(
                read=explicit(ibtidaa=11, waqf=(11, 12)),
                phonemes=(
                    "m u sˤ aˤ lˤlˤ aˤ:",
                    "w a ʕ a h i d Q n a:",
                ),
                char_rules={"ل": R("tafkheem")},
                sound_rules={"lˤlˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "taqlil_tarqiq": Expect(
                read=explicit(ibtidaa=11, waqf=(11, 12)),
                phonemes=(
                    "m u sˤ aˤ ll ɛ:",
                    "w a ʕ a h i d Q n a:",
                ),
                char_rules={"ل": R("tarqeeq")},
                sound_rules={"ll": R("tarqeeq"), "ɛ:": R("taqlil")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
        default="fath_tafkheem",
        masked=Expect(
            read=through(),
            phonemes=(
                "m u sˤ aˤ lˤlˤ aˤ",
                "w̃ a ʕ a h i d Q n a:",
            ),
            char_rules={"ل": R("tafkheem")},
            sound_rules={"lˤlˤ": R("tafkheem"), "aˤ[2]": R("tafkheem")},
            absent_sound_rules={"aˤ[2]": R("taqlil")},
            extra_phonemes=("emphatic_fatha",),
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_inclination(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(QUALITY_VARIANT_CASES))
def test_inclination_quality_variants(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(COUPLED_VARIANT_CASES))
def test_coupled_inclination_and_lam_variants(run):
    assert_case(run)
