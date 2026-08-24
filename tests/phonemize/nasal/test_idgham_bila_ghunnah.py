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
    # مِّن رَّبِّهِمْ
    Case(
        id="noon-raa",
        site=Site.shared("2:5", (4, 5)),
        read=through(),
        phonemes=("m i", "rˤrˤ aˤ bb i h i m"),
        char_rules={"ن": R("idgham_bila_ghunnah"),
                    "ر": R("idgham_bila_ghunnah")},
        sound_rules={"rˤrˤ": R("idgham_bila_ghunnah", "tafkheem")},
    ),
    # فَإِن لَّمْ
    StateCase(
        id="noon-lam-boundary",
        site=Site.shared("2:24", (1, 2)),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("f a ʔ i", "ll a m"),
                char_rules={"ن": R("idgham_bila_ghunnah"),
                            "ل": R("idgham_bila_ghunnah")},
                sound_rules={"ll": R("idgham_bila_ghunnah")},
            ),
            "stopped": Expect(
                read=explicit(ibtidaa=1, waqf=(1, 2)),
                phonemes=("f a ʔ i n", "l a m"),
                char_rules={"ن": R("izhar")},
                sound_rules={"n": R("izhar")},
                absent_char_rules={"ن": R("idgham_bila_ghunnah"),
                                   "ل": R("idgham_bila_ghunnah")},
            ),
        },
    ),
    # غَفُورٌ رَّحِيمٌ
    Case(
        id="tanwin-raa",
        site=Site.shared("2:173", (24, 25)),
        read=through(),
        phonemes=("ɣ aˤ f u: rˤ u", "rˤrˤ aˤ ħ i: m"),
        char_rules={"@dammatan[1]": R("idgham_bila_ghunnah"),
                    "ر[2]": R("idgham_bila_ghunnah")},
        sound_rules={"rˤrˤ": R("idgham_bila_ghunnah", "tafkheem")},
    ),
    # عَلِيمٌ لَّا
    Case(
        id="tanwin-lam-verse-seam",
        site=Site.shared("2:224", (14, 15)),
        read=explicit(ibtidaa=14, wasl=14, waqf=15),
        phonemes=("ʕ a l i: m u", "ll a:"),
        char_rules={"@dammatan": R("idgham_bila_ghunnah"),
                    "ل[2]": R("idgham_bila_ghunnah")},
        sound_rules={"ll": R("idgham_bila_ghunnah")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_idgham_bila_ghunnah(run):
    assert_case(run)
