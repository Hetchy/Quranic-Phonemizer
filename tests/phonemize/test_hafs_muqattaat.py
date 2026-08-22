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
    explicit,
    joining,
)


CASES = (
    # يسٓ وَٱلْقُرْءَانِ
    VariantCase(
        id="yaseen-wasl",
        site=Site(hafs=("36:1", (1, 2))),
        selector=KhilafId.NOON_YASEEN_WASL,
        faces={
            "izhar": Expect(
                read=explicit(ibtidaa=1, wasl=1),
                phonemes=("j a: s i: n", "w a l q u rˤ ʔ a: n i"),
                sound_rules={"n[1]": R("izhar")},
            ),
            "idgham": Expect(
                read=explicit(ibtidaa=1, wasl=1),
                phonemes=("j a: s i:", "w̃ a l q u rˤ ʔ a: n i"),
                char_rules={"و": R("idgham_bi_ghunnah")},
                sound_rules={"w̃": R("idgham_bi_ghunnah")},
            ),
        },
        default="izhar",
        masked=Expect(
            read=explicit(ibtidaa=1, waqf=1),
            phonemes=("j a: s i: n", "w a l q u rˤ ʔ a: n i"),
            sound_rules={"n[1]": R("izhar")},
            absent_char_rules={"و": R("idgham_bi_ghunnah")},
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_muqattaat_variants(run):
    assert_case(run)
