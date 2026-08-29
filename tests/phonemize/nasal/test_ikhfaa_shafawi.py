from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Case,
    Expect,
    R,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    explicit,
    through,
)

CASES = (
    # Hafs: هُم بِمُؤْمِنِينَ
    VariantCase(
        id="meem-before-baa-boundary",
        site=Site(hafs=("2:8", (10, 11))),
        selector=KhilafId.IKHFAA_SHAFAWI_NASAL,
        faces={
            "open": Expect(
                read=through(),
                phonemes=("h u ŋ", "b i m u ʔ m i n i: n"),
                char_rules={"م[1]": R("ikhfaa_shafawi")},
                sound_rules={"ŋ": R("ikhfaa_shafawi")},
            ),
            "closed": Expect(
                read=through(),
                phonemes=("h u m̃", "b i m u ʔ m i n i: n"),
                char_rules={"م[1]": R("ikhfaa_shafawi")},
                sound_rules={"m̃": R("ikhfaa_shafawi")},
            ),
        },
        default="open",
        masked=Expect(
            read=explicit(ibtidaa=10, waqf=(10, 11)),
            phonemes=("h u m", "b i m u ʔ m i n i: n"),
            char_rules={"م[1]": R("izhar_shafawi")},
            sound_rules={"m[1]": R("izhar_shafawi")},
            absent_char_rules={"م[1]": R("ikhfaa_shafawi")},
            absent_sound_rules={"m[1]": R("ikhfaa_shafawi")},
        ),
    ),
    # Warsh: هُم بِمُومِنِينَ — the single-hamza ibdal in the second word is
    # independent of the nasal rendering choice.
    VariantCase(
        id="meem-before-baa-boundary-warsh",
        site=Site(warsh=("2:8", (10, 11))),
        selector=KhilafId.IKHFAA_SHAFAWI_NASAL,
        faces={
            "open": Expect(
                read=through(),
                phonemes=("h u ŋ", "b i m u: m i n i: n"),
                char_rules={"م[1]": R("ikhfaa_shafawi")},
                sound_rules={"ŋ": R("ikhfaa_shafawi")},
            ),
            "closed": Expect(
                read=through(),
                phonemes=("h u m̃", "b i m u: m i n i: n"),
                char_rules={"م[1]": R("ikhfaa_shafawi")},
                sound_rules={"m̃": R("ikhfaa_shafawi")},
            ),
        },
        default="open",
        masked=Expect(
            read=explicit(ibtidaa=10, waqf=(10, 11)),
            phonemes=("h u m", "b i m u: m i n i: n"),
            char_rules={"م[1]": R("izhar_shafawi")},
            sound_rules={"m[1]": R("izhar_shafawi")},
            absent_char_rules={"م[1]": R("ikhfaa_shafawi")},
            absent_sound_rules={"m[1]": R("ikhfaa_shafawi")},
        ),
    ),
    # Hafs: ذَٰلِكُم بَلَآءٌ
    # Warsh: ذَٰلِكُم بَلَآءٞ
    Case(
        id="second-pronominal-shape",
        site=Site.shared("2:49", (14, 15)),
        read=through(),
        phonemes=("ð a: l i k u ŋ", "b a l a: ʔ"),
        char_rules={"م": R("ikhfaa_shafawi")},
        sound_rules={"ŋ": R("ikhfaa_shafawi")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_ikhfaa_shafawi(run):
    assert_case(run)
