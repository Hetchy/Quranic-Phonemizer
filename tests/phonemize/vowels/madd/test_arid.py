from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick


CASES = (
    # يُنفِقُونَ
    Case(id="ordinary", site=Site.shared("2:3", (8,)), read=isolated(),
         phonemes="j u ŋ f i q u: n",
         char_rules={"و": R("madd_arid_lissukun")},
         sound_rules={"u:": R("madd_arid_lissukun")}),
    # عَظِيمٌ
    Case(id="tanwin-drops", site=Site.shared("2:7", (12,)), read=isolated(),
         phonemes="ʕ a ðˤ i: m",
         char_rules={"ي": R("madd_arid_lissukun")},
         sound_rules={"i:": R("madd_arid_lissukun")}),
    # مُوسَىٰ
    Case(id="final-long-negative", site=Site.shared("20:9", (4,)), read=isolated(),
         phonemes="m u: s a:", absent_char_rules={"و": R("madd_arid_lissukun")}),
    # مِهَادًا
    Case(id="iwad-negative", site=Site.shared("78:6", (4,)), read=isolated(),
         phonemes="m i h a: d a:",
         absent_char_rules={"@dagger_alif": R("madd_arid_lissukun")}),
    # مَـَٔابٍ
    Case(id="badal-overlap", site=Site(hafs=("13:29", (8,))), read=isolated(),
         phonemes="m a ʔ a: b Q",
         char_rules=pick(
             hafs_uthmani={"ا": R("madd_badal", "madd_arid_lissukun")},
             hafs_indopak={
                 "@dagger_alif": R("madd_badal", "madd_arid_lissukun")
             },
         ),
         sound_rules={"a:": R("madd_badal", "madd_arid_lissukun")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_arid(run):
    assert_case(run)
