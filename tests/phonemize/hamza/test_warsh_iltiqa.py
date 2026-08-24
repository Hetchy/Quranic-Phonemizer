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
    # Warsh: قُلُ اُ۟دْعُواْ
    StateCase(id="damm-copy-lexical", site=Site(warsh=("7:195", (20, 21))), states={
        "joined": Expect(read=through(),
                         phonemes=("q u l u", "d Q ʕ u:"),
                         char_rules={"ا[1]": R("hamza_wasl_silent")},
                         silent=("ا[1]",)),
        "restarted": Expect(read=explicit(ibtidaa=20, waqf=(20, 21)),
                            phonemes=("q u l", "ʔ u d Q ʕ u:"),
                            char_rules={"ا[1]": R("hamza_wasl_damma")},
                            sound_rules={"ʔ": R("hamza_wasl_damma")},
                            absent_char_rules={"ا[1]": R("hamza_wasl_silent")}),
    }),
    # Warsh: بَعْضٍۖ اُ۟نظُرْ
    StateCase(id="damm-copy-tanwin", site=Site(warsh=("6:65", (21, 22))), states={
        "joined": Expect(read=through(),
                         phonemes=("b a ʕ dˤ i n u", "ŋ ðˤ u rˤ"),
                         char_rules={"ا": R("hamza_wasl_silent")},
                         sound_rules={"u[1]": R("iltiqa_haraka")}),
        "stopped": Expect(read=explicit(ibtidaa=21, waqf=(21, 22)),
                          phonemes=("b a ʕ dˤ", "ʔ u ŋ ðˤ u rˤ"),
                          char_rules={"ا": R("hamza_wasl_damma")},
                          sound_rules={"ʔ": R("hamza_wasl_damma")},
                          absent_sound_rules={"u[1]": R("iltiqa_haraka")}),
    }),
    # Warsh: أَنِ اِ۪تَّقُواْ
    Case(id="damm-needs-original-stem-vowel", site=Site(warsh=("4:131", (16, 17))),
         read=through(),
         phonemes=("ʔ a n i", "tt a q u:"),
         char_rules={"ا[1]": R("hamza_wasl_silent")}),
    # Warsh: وَقَالَتُ اُ۟خْرُجْ
    Case(id="damm-copy-feminine-taa", site=Site(warsh=("12:31", (14, 15))),
         read=through(),
         phonemes=("w a q aˤ: l a t u", "x rˤ u ʒ Q"),
         char_rules={"ا[2]": R("hamza_wasl_silent")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_iltiqa(run):
    assert_case(run)
