from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # يُنفِقُونَ
    Case(id="ordinary", site=Site(hafs=("2:3", (8,))), read=isolated(),
         phonemes="j u ŋ f i q u: n",
         char_rules={"و": R("madd_arid_lil_sukun")},
         sound_rules={"u:": R("madd_arid_lil_sukun")}),
    # عَظِيمٌ
    Case(id="tanwin-drops", site=Site(hafs=("2:7", (12,))), read=isolated(),
         phonemes="ʕ a ðˤ i: m",
         char_rules={"ي": R("madd_arid_lil_sukun")},
         sound_rules={"i:": R("madd_arid_lil_sukun")}),
    # مُوسَىٰ
    Case(id="final-long-negative", site=Site(hafs=("20:9", (4,))), read=isolated(),
         phonemes="m u: s a:", absent_char_rules={"و": R("madd_arid_lil_sukun")}),
    # مِهَادًا
    Case(id="iwad-negative", site=Site(hafs=("78:6", (4,))), read=isolated(),
         phonemes="m i h a: d a:",
         absent_char_rules={"@dagger_alif": R("madd_arid_lil_sukun")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_arid(run):
    assert_case(run)
