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


CASES = (
    # يَوْمِ
    StateCase(id="waw", site=Site.shared("1:4", (2,)), states={
        "joined": Expect(read=joining(), phonemes="j a w m i",
                         absent_char_rules={"و": R("madd_leen")}),
        "stopped": Expect(read=isolated(), phonemes="j a w m",
                          char_rules={"و": R("madd_leen")},
                          sound_rules={"w": R("madd_leen")}),
    }),
    # قُرَيْشٍ
    StateCase(id="yaa", site=Site.shared("106:1", (2,)), states={
        "joined": Expect(read=joining(), phonemes="q u rˤ aˤ j ʃ i n",
                         absent_char_rules={"ي": R("madd_leen")}),
        "stopped": Expect(read=isolated(), phonemes="q u rˤ aˤ j ʃ",
                          char_rules={"ي": R("madd_leen")},
                          sound_rules={"j": R("madd_leen")}),
    }),
    # قَوْلِى
    StateCase(id="final-long-negative", site=Site.shared("20:28", (2,)), states={
        "joined": Expect(read=joining(), phonemes="q aˤ w l i:",
                         absent_char_rules={"و": R("madd_leen")}),
        "stopped": Expect(read=isolated(), phonemes="q aˤ w l i:",
                          absent_char_rules={"و": R("madd_leen")}),
    }),
    # عَيْنًا
    StateCase(id="iwad-negative", site=Site.shared("2:60", (13,)), states={
        "joined": Expect(read=joining(), phonemes="ʕ a j n a ŋ",
                         absent_char_rules={"ي": R("madd_leen")}),
        "stopped": Expect(read=isolated(), phonemes="ʕ a j n a:",
                          absent_char_rules={"ي": R("madd_leen")}),
    }),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_leen(run):
    assert_case(run)
