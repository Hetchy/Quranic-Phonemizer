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


CASES = (
    # وَقُل رَّبِّ
    StateCase(id="qul-rabbi", site=Site.shared("23:118", (1, 2)), states={
        "joined": Expect(read=through(), phonemes=("w a q u", "rˤrˤ aˤ bb Q"),
                         char_rules={"ل": R("idgham_mutaqaribayn"),
                                     "ر": R("idgham_mutaqaribayn")},
                         sound_rules={"rˤrˤ": R("idgham_mutaqaribayn")}),
        "ibtidaa-on-host": Expect(read=explicit(ibtidaa=1, waqf=1),
                          phonemes=("w a q u l", "rˤ aˤ bb i"),
                          absent_char_rules={"ل": R("idgham_mutaqaribayn"),
                                             "ر": R("idgham_mutaqaribayn")}),
    }),
    # بَل رَّفَعَهُ
    StateCase(id="bal-rafah", site=Site.shared("4:158", (1, 2)), states={
        "joined": Expect(read=through(), phonemes=("b a", "rˤrˤ aˤ f a ʕ a h"),
                         char_rules={"ل": R("idgham_mutaqaribayn"),
                                     "ر": R("idgham_mutaqaribayn")},
                         sound_rules={"rˤrˤ": R("idgham_mutaqaribayn")}),
        "ibtidaa-on-host": Expect(read=explicit(ibtidaa=1, waqf=1),
                          phonemes=("b a l", "rˤ aˤ f a ʕ a h u"),
                          absent_char_rules={"ل": R("idgham_mutaqaribayn"),
                                             "ر": R("idgham_mutaqaribayn")}),
    }),
    # نَخْلُقكُّم
    Case(id="nakhluqkum", site=Site.shared("77:20", (2,)), read=isolated(),
         phonemes="n a x l u kk u m",
         char_rules={"ق": R("idgham_mutaqaribayn"),
                     "ك": R("idgham_mutaqaribayn")},
         sound_rules={"kk": R("idgham_mutaqaribayn")},
         absent_char_rules={"ق": R(
             "tafkheem", "qalqala_sughra", "qalqala_kubra", "qalqala_akbar")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_mutaqaribayn(run):
    assert_case(run)
