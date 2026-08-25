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
    # Hafs: هُدًى
    StateCase(id="fathatan-maqsura", site=Site(hafs=("2:5", (3,))), states={
        "joined": Expect(read=joining(), phonemes="h u d a",
                         absent_char_rules=pick(
                             hafs_uthmani={"ى": R("madd_iwad")},
                             hafs_indopak={"ي": R("madd_iwad")},
                         )),
        "stopped": Expect(read=isolated(), phonemes="h u d a:",
                          char_rules=pick(
                              hafs_uthmani={"ى": R("madd_iwad", "madd_tabii")},
                              hafs_indopak={},
                          ),
                          sound_rules={"a:": R("madd_iwad", "madd_tabii")}),
    }),
    # Hafs: إِثْمًا
    # Warsh: إِثْماً
    StateCase(id="fathatan-alif", site=Site.shared("4:48", (19,)), states={
        "joined": Expect(read=joining(), phonemes="ʔ i θ m a n",
                         absent_char_rules=pick(
                             hafs_uthmani={"ا": R("madd_iwad")},
                             hafs_indopak={"ا[2]": R("madd_iwad")},
                             warsh_uthmani={"ا": R("madd_iwad")},
                         )),
        "stopped": Expect(read=isolated(), phonemes="ʔ i θ m a:",
                          char_rules=pick(
                              hafs_uthmani={"ا": R("madd_iwad", "madd_tabii")},
                              hafs_indopak={"ا[2]": R("madd_iwad", "madd_tabii")},
                              warsh_uthmani={"ا": R("madd_iwad", "madd_tabii")},
                          ),
                          sound_rules={"a:": R("madd_iwad", "madd_tabii")}),
    }),
    # Hafs: مَآءً
    # Warsh: مَآءٗ
    StateCase(id="fathatan-after-hamza", site=Site.shared("2:22", (11,)), states={
        "joined": Expect(
            read=joining(), phonemes="m a: ʔ a ŋ",
            char_rules={"ا": R("madd_muttasil"),
                        "@fathatan": R("ikhfaa")},
            sound_rules={"a:": R("madd_muttasil"),
                         "ŋ": R("ikhfaa")},
        ),
        "stopped": Expect(
            read=isolated(), phonemes="m a: ʔ a:",
            char_rules={"ا": R("madd_muttasil"),
                        "@inserted/ا": R("madd_iwad", "madd_tabii")},
            sound_rules={"a:[1]": R("madd_muttasil"),
                         "a:[2]": R("madd_iwad", "madd_tabii")},
        ),
    }),
    # Hafs: غَفُورٌ
    # Warsh: غَفُورٌ
    StateCase(id="dammatan-negative", site=Site.shared("2:225", (13,)), states={
        "joined": Expect(read=joining(), phonemes="ɣ aˤ f u: rˤ u n"),
        "stopped": Expect(read=isolated(), phonemes="ɣ aˤ f u: rˤ"),
    }),
    # Hafs: قَوْمٍ
    # Warsh: قَوْمٍ
    StateCase(id="kasratan-negative", site=Site.shared("13:7", (14,)), states={
        "joined": Expect(read=joining(), phonemes="q aˤ w m i n"),
        "stopped": Expect(read=isolated(), phonemes="q aˤ w m"),
    }),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_iwad(run):
    assert_case(run)
