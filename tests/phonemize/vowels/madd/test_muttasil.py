from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, joining


CASES = (
    # Hafs: سَوَآءٌ
    # Warsh: سَوَآءٌ
    Case(id="ordinary", site=Site.shared("2:6", (4,)), read=isolated(),
         phonemes="s a w a: ʔ", char_rules={"ا": R("madd_muttasil")},
         sound_rules={"a:": R("madd_muttasil")}),
    # Hafs: هَآؤُمُ
    # Warsh: هَآؤُمُ
    Case(id="lexical-hamza", site=Site.shared("69:19", (7,)), read=joining(),
         phonemes="h a: ʔ u m u", char_rules={"ا": R("madd_muttasil")},
         sound_rules={"a:": R("madd_muttasil")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_muttasil(run):
    assert_case(run)
