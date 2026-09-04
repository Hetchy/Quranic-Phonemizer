from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated

CASES = (
    # Hafs: ءَا۬عْجَمِىٌّ
    Case(
        id="aajamiyy-collapsed",
        site=Site(hafs=("41:44", (9,))),
        read=isolated(),
        phonemes="ʔ a ʔ a ʕ ʒ a m i jj",
        char_rules={"ا": R("tashil")},
        sound_rules={"ʔ[2]": R("tashil")},
        extra_phonemes=(),
    ),
    # Hafs: ءَا۬عْجَمِىٌّ
    Case(
        id="aajamiyy-rendered",
        site=Site(hafs=("41:44", (9,))),
        read=isolated(),
        phonemes="ʔ a ʔ̞ a ʕ ʒ a m i jj",
        char_rules={"ا": R("tashil")},
        sound_rules={"ʔ̞": R("tashil")},
        extra_phonemes=("tashil",),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_tashil(run):
    assert_case(run)
