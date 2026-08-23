from __future__ import annotations

import pytest

from tests.support import (
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    isolated,
    joining,
)


def _case(name: str, ref: str, word: int, joined: str, stopped: str, ending: str):
    return StateCase(id=name, site=Site(hafs=(ref, (word,))), states={
        "joined": Expect(read=joining(), phonemes=joined,
                         absent_char_rules={"ة": R("waqf_taa_marbuta")}),
        "stopped": Expect(read=isolated(), phonemes=stopped,
                          char_rules={"ة": R("waqf_taa_marbuta")},
                          sound_rules={"h": R("waqf_taa_marbuta")},
                          silent=(ending,)),
    })


CASES = (
    # بَعُوضَةً
    _case("fathatan", "2:26", 9, "b a ʕ u: dˤ aˤ t a ŋ", "b a ʕ u: dˤ aˤ h",
          "@fathatan"),
    # سِنَةٌ
    _case("dammatan", "2:255", 10, "s i n a t u", "s i n a h", "@dammatan"),
    # وَاحِدَةٍ
    _case("kasratan", "4:1", 9, "w a: ħ i d a t i", "w a: ħ i d a h",
          "@kasratan"),
    # قُوَّةَ
    _case("fatha", "18:39", 10, "q u ww a t a", "q u ww a h", "@fatha[2]"),
    # تِجَارَةً
    _case("fathatan-heavy-raa", "2:282", 99, "t i ʒ a: rˤ aˤ t a n",
          "t i ʒ a: rˤ aˤ h", "@fathatan"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_taa_marbuta(run):
    assert_case(run)
