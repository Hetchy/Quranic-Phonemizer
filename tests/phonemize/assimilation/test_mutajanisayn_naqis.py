from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # بَسَطتَ
    Case(id="basatta", site=Site.shared("5:28", (2,)), read=isolated(),
         phonemes="b a s a tˤ t",
         char_rules={"ط": R("idgham_mutajanisayn_naqis"),
                     "ت": R("idgham_mutajanisayn_naqis")},
         sound_rules={"tˤ": R("idgham_mutajanisayn_naqis"),
                      "t": R("idgham_mutajanisayn_naqis")},
         absent_char_rules={"ط": R(
             "qalqala_sughra", "qalqala_kubra", "qalqala_akbar")}),
    # أَحَطتُ
    Case(id="ahattu", site=Site.shared("27:22", (5,)), read=isolated(),
         phonemes="ʔ a ħ a tˤ t",
         char_rules={"ط": R("idgham_mutajanisayn_naqis"),
                     "ت": R("idgham_mutajanisayn_naqis")},
         sound_rules={"tˤ": R("idgham_mutajanisayn_naqis"),
                      "t": R("idgham_mutajanisayn_naqis")}),
    # فَرَّطتُمْ
    Case(id="farrattum", site=Site.shared("12:80", (21,)), read=isolated(),
         phonemes="f a rˤrˤ aˤ tˤ t u m",
         char_rules={"ط": R("idgham_mutajanisayn_naqis"),
                     "ت": R("idgham_mutajanisayn_naqis")},
         sound_rules={"tˤ": R("idgham_mutajanisayn_naqis"),
                      "t": R("idgham_mutajanisayn_naqis")}),
    # فَرَّطتُ
    Case(id="farrattu", site=Site.shared("39:56", (7,)), read=isolated(),
         phonemes="f a rˤrˤ aˤ tˤ t",
         char_rules={"ط": R("idgham_mutajanisayn_naqis"),
                     "ت": R("idgham_mutajanisayn_naqis")},
         sound_rules={"tˤ": R("idgham_mutajanisayn_naqis"),
                      "t": R("idgham_mutajanisayn_naqis")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_mutajanisayn_naqis(run):
    assert_case(run)
