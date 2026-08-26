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


DIRECT_CASES = (
    # Warsh: صَلَوَٰتٞ
    Case(
        id="sad-open-before-consonantal-waw",
        site=Site(warsh=("2:157", (3,))),
        read=isolated(),
        phonemes="sˤ aˤ lˤ aˤ w a: t",
        char_rules={"ل": R("tafkheem"), "@fatha[2]": R("tafkheem")},
        sound_rules={"lˤ": R("tafkheem"), "aˤ[2]": R("tafkheem")},
        absent_char_rules={
            "و": R("tafkheem"),
            "@dagger_alif": R("tafkheem"),
        },
        absent_sound_rules={"a:": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: اَ۬لصَّلَوٰةَ
    Case(
        id="sad-open-long-a",
        site=Site(warsh=("2:3", (5,))),
        read=isolated(),
        phonemes="ʔ a sˤsˤ aˤ lˤ aˤ: h",
        char_rules={
            "ل[2]": R("tafkheem"),
            "@dagger_alif": R("tafkheem"),
        },
        sound_rules={"lˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: وَأَصْلَحُواْ
    Case(
        id="sad-sakin-short-a",
        site=Site(warsh=("2:160", (4,))),
        read=isolated(),
        phonemes="w a ʔ a sˤ lˤ aˤ ħ u:",
        char_rules={"ل": R("tafkheem"), "@fatha[3]": R("tafkheem")},
        sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: طَلَّقَهَا
    Case(
        id="taa-open-geminated-lam",
        site=Site(warsh=("2:230", (2,))),
        read=isolated(),
        phonemes="tˤ aˤ lˤlˤ aˤ q aˤ h a:",
        char_rules={"ل": R("tafkheem"), "@fatha[2]": R("tafkheem")},
        sound_rules={"lˤlˤ": R("tafkheem"), "aˤ[2]": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: مَطْلَعِ
    Case(
        id="taa-sakin-short-a",
        site=Site(warsh=("97:5", (4,))),
        read=isolated(),
        phonemes="m a tˤ Q lˤ aˤ ʕ",
        char_rules={"ل": R("tafkheem"), "@fatha[2]": R("tafkheem")},
        sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: ظَلَمْتُمُۥٓ
    Case(
        id="zhaa-open-short-a",
        site=Site(warsh=("2:54", (7,))),
        read=isolated(),
        phonemes="ðˤ aˤ lˤ aˤ m t u m",
        char_rules={"ل": R("tafkheem"), "@fatha[2]": R("tafkheem")},
        sound_rules={"lˤ": R("tafkheem"), "aˤ[2]": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: تُظْلَمُونَۖ
    Case(
        id="zhaa-sakin-short-a",
        site=Site(warsh=("2:272", (28,))),
        read=isolated(),
        phonemes="t u ðˤ lˤ aˤ m u: n",
        char_rules={"ل": R("tafkheem"), "@fatha[1]": R("tafkheem")},
        sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
)


NEGATIVE_CASES = (
    # Warsh: بَٰطِلاٗ
    Case(
        id="kasra-trigger-negative",
        site=Site(warsh=("3:191", (17,))),
        read=isolated(),
        phonemes="b a: tˤ i l a:",
        absent_char_rules={"ل": R("tafkheem")},
        absent_sound_rules={"l": R("tafkheem"), "a:[2]": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: ظُلَلٖ
    Case(
        id="damma-trigger-negative",
        site=Site(warsh=("2:210", (8,))),
        read=isolated(),
        phonemes="ðˤ u l a l",
        absent_char_rules={"ل[1]": R("tafkheem")},
        absent_sound_rules={"l[1]": R("tafkheem"), "a": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: مُصْلِحُونَۖ
    Case(
        id="closed-target-negative",
        site=Site(warsh=("2:11", (11,))),
        read=isolated(),
        phonemes="m u sˤ l i ħ u: n",
        absent_char_rules={"ل": R("tafkheem")},
        absent_sound_rules={"l": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: صَلْداٗۖ
    Case(
        id="sakin-target-negative",
        site=Site(warsh=("2:264", (27,))),
        read=isolated(),
        phonemes="sˤ aˤ l d a:",
        absent_char_rules={"ل": R("tafkheem")},
        absent_sound_rules={"l": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: اِ۬لْقَصَصَ لَعَلَّهُمْ
    Case(
        id="cross-word-negative",
        site=Site(warsh=("7:176", (28, 29))),
        read=through(),
        phonemes=(
            "ʔ a l q aˤ sˤ aˤ sˤ aˤ",
            "l a ʕ a ll a h u m",
        ),
        absent_char_rules={"ل[2]": R("tafkheem")},
        absent_sound_rules={"l[2]": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
)


COUPLED_CASES = (
    # Warsh: صَلّ۪ىٰۖ
    Case(
        id="verse-head-taqlil-tarqiq",
        site=Site(warsh=("75:31", (4,))),
        read=isolated(),
        phonemes="sˤ aˤ ll ɛ:",
        char_rules={"ل": R("tarqeeq"), "ى": R("taqlil")},
        sound_rules={"ll": R("tarqeeq"), "ɛ:": R("taqlil")},
        absent_sound_rules={"ll": R("tafkheem"), "ɛ:": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
)


SALSAL_CASES = (
    # Warsh: صَلْصَٰلٖ مِّنْ حَمَإٖ
    Case(
        id="salsal-first-lam-only",
        site=Site(warsh=("15:26", (5, 6, 7))),
        read=through(),
        phonemes=(
            "sˤ aˤ l sˤ aˤ: l i",
            "m̃ i n",
            "ħ a m a ʔ",
        ),
        char_rules={"ل[1]": R("tarqeeq")},
        sound_rules={"l[1]": R("tarqeeq")},
        absent_char_rules={"ل[2]": R("tafkheem", "tarqeeq")},
        absent_sound_rules={"l[2]": R("tafkheem", "tarqeeq")},
        extra_phonemes=("emphatic_fatha",),
    ),
)


SEPARATED_CASES = (
    # Warsh: طَالَ
    Case(
        id="separated-taala-at-waqf",
        site=Site(warsh=("21:44", (6,))),
        read=isolated(),
        phonemes="tˤ aˤ: lˤ",
        char_rules={"ل": R("tafkheem")},
        sound_rules={"lˤ": R("tafkheem")},
        extra_phonemes=("emphatic_fatha",),
    ),
    # Warsh: فِصَالاً عَن
    StateCase(
        id="separated-fisal-tanwin-and-iwad",
        site=Site(warsh=("2:233", (36, 37))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("f i sˤ aˤ: lˤ aˤ n", "ʕ a n"),
                char_rules={"ل": R("tafkheem")},
                sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=36, waqf=(36, 37)),
                phonemes=("f i sˤ aˤ: lˤ aˤ:", "ʕ a n"),
                char_rules={
                    "ل": R("tafkheem"),
                    "ا[2]": R("tafkheem", "madd_iwad", "madd_tabii"),
                },
                sound_rules={
                    "lˤ": R("tafkheem"),
                    "aˤ:[2]": R("tafkheem", "madd_iwad", "madd_tabii"),
                },
                extra_phonemes=("emphatic_fatha",),
            ),
        },
    ),
)


COUPLED_BOUNDARY_CASES = (
    # Warsh: مُصَلّىٗۖ وَعَهِدْنَآ
    StateCase(
        id="dhat-yaa-boundary-mask",
        site=Site(warsh=("2:125", (11, 12))),
        states={
            "joined": Expect(
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
            "stopped": Expect(
                read=explicit(ibtidaa=11, waqf=(11, 12)),
                phonemes=(
                    "m u sˤ aˤ lˤlˤ aˤ:",
                    "w a ʕ a h i d Q n a:",
                ),
                char_rules={
                    "ل": R("tafkheem"),
                    "ى": R("tafkheem", "madd_iwad", "madd_tabii"),
                },
                sound_rules={
                    "lˤlˤ": R("tafkheem"),
                    "aˤ:": R("tafkheem", "madd_iwad", "madd_tabii"),
                },
                extra_phonemes=("emphatic_fatha",),
            ),
        },
    ),
    # Warsh: يَصْلَى اَ۬لنَّارَ
    StateCase(
        id="dhat-yaa-iltiqa-mask",
        site=Site(warsh=("87:12", (2, 3))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("j a sˤ lˤ aˤ", "ñ a: rˤ"),
                char_rules={"ل[1]": R("tafkheem")},
                sound_rules={"lˤ": R("tafkheem"), "aˤ": R("tafkheem")},
                extra_phonemes=("emphatic_fatha",),
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=2, waqf=(2, 3)),
                phonemes=("j a sˤ lˤ aˤ:", "ʔ a ñ a: rˤ"),
                char_rules={"ل[1]": R("tafkheem"), "ى": R("tafkheem")},
                sound_rules={"lˤ": R("tafkheem"), "aˤ:": R("tafkheem")},
                extra_phonemes=("emphatic_fatha",),
            ),
        },
    ),
)


@pytest.mark.parametrize("run", case_runs(DIRECT_CASES))
def test_direct_lam_tafkheem(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(NEGATIVE_CASES))
def test_nearby_lams_are_not_claimed(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(COUPLED_CASES))
def test_inclination_coupling(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(COUPLED_BOUNDARY_CASES))
def test_inclination_coupling_at_boundary_masks(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(SEPARATED_CASES))
def test_alif_separated_lams(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(SALSAL_CASES))
def test_salsal_first_lam(run):
    assert_case(run)
