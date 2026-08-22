from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Expect,
    R,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    isolated,
    joining,
)


CASES = (
    # ءَاتَىٰنِۦَ
    VariantCase(
        id="aatani-waqf",
        site=Site(hafs=("27:36", (8,))),
        selector=KhilafId.YAA_AATANI_WAQF,
        faces={
            "hadhf": Expect(read=isolated(), phonemes="ʔ a: t a: n"),
            "ithbat": Expect(
                read=isolated(),
                phonemes="ʔ a: t a: n i:",
                sound_rules={"i:": R("madd_tabii")},
            ),
        },
        default="hadhf",
        masked=Expect(read=joining(), phonemes="ʔ a: t a: n i j a"),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_aatani(run):
    assert_case(run)
