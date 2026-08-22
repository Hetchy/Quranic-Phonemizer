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
    pick,
)


CASES = (
    # هُدًى مِّن
    StateCase(id="fathatan-maqsura", site=Site(hafs=("2:5", (3,))), states={
        "joined": Expect(read=joining(), phonemes="h u d a",
                         absent_char_rules=pick(
                             hafs_uthmani={"ى": R("iwad")},
                             hafs_indopak={"ي": R("iwad")},
                         )),
        "stopped": Expect(read=isolated(), phonemes="h u d a:",
                          char_rules=pick(
                              hafs_uthmani={"ى": R("iwad")},
                              hafs_indopak={"ي": R("iwad")},
                          ),
                          sound_rules={"a:": R("iwad")}),
    }),
    # إِثْمًا عَظِيمًا
    StateCase(id="fathatan-alif", site=Site(hafs=("4:48", (19,))), states={
        "joined": Expect(read=joining(), phonemes="ʔ i θ m a n",
                         absent_char_rules=pick(
                             hafs_uthmani={"ا": R("iwad")},
                             hafs_indopak={"ا[2]": R("iwad")},
                         )),
        "stopped": Expect(read=isolated(), phonemes="ʔ i θ m a:",
                          char_rules=pick(
                              hafs_uthmani={"ا": R("iwad")},
                              hafs_indopak={"ا[2]": R("iwad")},
                          ),
                          sound_rules={"a:": R("iwad")}),
    }),
    # غَفُورٌ حَلِيمٌ
    StateCase(id="dammatan-negative", site=Site(hafs=("2:225", (13,))), states={
        "joined": Expect(read=joining(), phonemes="ɣ aˤ f u: rˤ u n",
                         absent_char_rules={"@dammatan": R("iwad")}),
        "stopped": Expect(read=isolated(), phonemes="ɣ aˤ f u: rˤ",
                          absent_char_rules={"@dammatan": R("iwad")}),
    }),
    # لِقَوْمٍ آخَرِينَ
    StateCase(id="kasratan-negative", site=Site(hafs=("5:41", (23,))), states={
        "joined": Expect(read=joining(), phonemes="l i q aˤ w m i n",
                         absent_char_rules={"@kasratan": R("iwad")}),
        "stopped": Expect(read=isolated(), phonemes="l i q aˤ w m",
                          absent_char_rules={"@kasratan": R("iwad")}),
    }),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_iwad(run):
    assert_case(run)
