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
    # Warsh: دَعَانِۦۖ فَلْيَسْتَجِيبُواْ
    StateCase(
        id="ordinary-long",
        site=Site(warsh=("2:186", (11, 12))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("d a ʕ a: n i:", "f a l j a s t a ʒ i: b u:"),
                char_rules={
                    "@small_yaa[1]": R("madd_yaa_zawaid", "madd_tabii")
                },
                sound_rules={"i:[1]": R("madd_yaa_zawaid", "madd_tabii")},
                absent_sound_rules={"i:[1]": R("madd_silah")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=11, waqf=(11, 12)),
                phonemes=("d a ʕ a: n", "f a l j a s t a ʒ i: b u:"),
                absent_char_rules={
                    "@small_yaa[1]": R(
                        "madd_yaa_zawaid", "madd_tabii", "madd_silah"
                    )
                },
            ),
        },
    ),
    # Warsh: اَ۬لدَّاعِۦٓ إِذَا
    StateCase(
        id="before-qata",
        site=Site(warsh=("2:186", (9, 10))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("ʔ a dd a: ʕ i:", "ʔ i ð a:"),
                char_rules={
                    "@small_yaa": R("madd_yaa_zawaid", "madd_munfasil")
                },
                sound_rules={"i:": R("madd_yaa_zawaid", "madd_munfasil")},
                absent_char_rules={"إ": R("madd_munfasil")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=9, waqf=(9, 10)),
                phonemes=("ʔ a dd a: ʕ", "ʔ i ð a:"),
                absent_char_rules={
                    "@small_yaa": R("madd_yaa_zawaid", "madd_munfasil")
                },
            ),
        },
    ),
    # Warsh: دُعَآءِۦۖ رَبَّنَا
    StateCase(
        id="after-hamza-badal",
        site=Site(warsh=("14:40", (9, 10))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("d u ʕ a: ʔ i:", "rˤ aˤ bb a n a:"),
                char_rules={"@small_yaa": R("madd_yaa_zawaid", "madd_badal")},
                sound_rules={"i:": R("madd_yaa_zawaid", "madd_badal")},
                absent_sound_rules={"i:": R("madd_tabii", "madd_silah")},
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=9, waqf=(9, 10)),
                phonemes=("d u ʕ a: ʔ", "rˤ aˤ bb a n a:"),
                absent_char_rules={
                    "@small_yaa": R(
                        "madd_yaa_zawaid", "madd_badal", "madd_tabii"
                    )
                },
            ),
        },
    ),
)


NAML_CASES = (
    # Warsh: ءَات۪يٰنِۦَ اَ۬للَّهُ
    StateCase(
        id="naml-consonantal",
        site=Site(warsh=("27:36", (8, 9))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("ʔ a: t ɛ: n i j a", "lˤlˤ aˤ: h"),
                char_rules={"ا[2]": R("hamza_wasl_silent")},
                absent_sound_rules={
                    "j": R("madd_yaa_zawaid", "madd_tabii"),
                    "a[2]": R("madd_yaa_zawaid", "madd_tabii"),
                },
            ),
            "host-waqf": Expect(
                read=explicit(ibtidaa=8, waqf=(8, 9)),
                phonemes=("ʔ a: t ɛ: n", "ʔ a lˤlˤ aˤ: h"),
            ),
        },
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_yaa_zawaid(run):
    assert_case(run)


@pytest.mark.parametrize("run", case_runs(NAML_CASES))
def test_warsh_yaa_zawaid_naml_interaction(run):
    assert_case(run)
