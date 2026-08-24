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


def _case(
    name: str, ref: str, word: int, joined: str, stopped: str, ending: str,
    *, warsh: bool = True,
):
    site = Site.shared(ref, (word,)) if warsh else Site(hafs=(ref, (word,)))
    return StateCase(id=name, site=site, states={
        "joined": Expect(read=joining(), phonemes=joined,
                         absent_char_rules={"ة": R("waqf_taa_marbuta")}),
        "stopped": Expect(read=isolated(), phonemes=stopped,
                          char_rules={"ة": R("waqf_taa_marbuta")},
                          sound_rules={"h": R("waqf_taa_marbuta")},
                          silent=(ending,)),
    })


CASES = (
    # Hafs: بَعُوضَةً
    # Warsh: بَعُوضَةٗ
    _case("fathatan", "2:26", 9, "b a ʕ u: dˤ aˤ t a ŋ", "b a ʕ u: dˤ aˤ h",
          "@fathatan"),
    # Hafs: سِنَةٌ
    # Warsh: سِنَةٞ
    _case("dammatan", "2:255", 10, "s i n a t u", "s i n a h", "@dammatan"),
    # Hafs: وَٰحِدَةٍ
    # Warsh: وَٰحِدَةٖ
    _case("kasratan", "4:1", 9, "w a: ħ i d a t i", "w a: ħ i d a h",
          "@kasratan"),
    # Hafs: قُوَّةَ
    # Warsh: قُوَّةَ
    _case("fatha", "18:39", 10, "q u ww a t a", "q u ww a h", "@fatha[2]"),
    # Hafs: تِجَـٰرَةً
    _case("fathatan-heavy-raa", "2:282", 99, "t i ʒ a: rˤ aˤ t a n",
          "t i ʒ a: rˤ aˤ h", "@fathatan", warsh=False),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_taa_marbuta(run):
    assert_case(run)
