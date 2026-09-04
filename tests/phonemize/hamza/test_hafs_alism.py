from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Expect,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    explicit,
    isolated,
)

CASES = (
    # Hafs: ٱلِٱسْمُ
    VariantCase(
        id="alism-ibtidaa",
        site=Site(hafs=("49:11", (30,))),
        selector=KhilafId.ALISM_IBTIDAA,
        faces={
            "hamza": Expect(read=isolated(), phonemes="ʔ a l i s m"),
            "lam": Expect(read=isolated(), phonemes="l i s m"),
        },
        default="hamza",
        masked=Expect(
            read=explicit(ibtidaa=29, wasl=30),
            phonemes="l i s m u",
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_alism(run):
    assert_case(run)
