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
)


def _case(
    case_id: str,
    selector: KhilafId,
    ref: str,
    word: int,
    seen: str,
    saad: str,
    default: str,
) -> VariantCase:
    return VariantCase(
        id=case_id,
        site=Site(hafs=(ref, (word,))),
        selector=selector,
        faces={
            "seen": Expect(
                read=isolated(),
                phonemes=seen,
                absent_char_rules={"ص": R("tafkheem")},
                absent_sound_rules={"s": R("tafkheem")},
            ),
            "saad": Expect(
                read=isolated(),
                phonemes=saad,
                char_rules={"ص": R("tafkheem")},
                sound_rules={"sˤ": R("tafkheem")},
            ),
        },
        default=default,
    )


CASES = (
    # Hafs: وَيَبْصُۜطُ
    _case("yabsut", KhilafId.YABSUT, "2:245", 14,
          "w a j a b Q s u tˤ Q", "w a j a b Q sˤ u tˤ Q", "seen"),
    # Hafs: بَصْۜطَةً ۖ
    _case("bastah", KhilafId.BASTAH, "7:69", 22,
          "b a s tˤ aˤ h", "b a sˤ tˤ aˤ h", "seen"),
    # Hafs: ٱلْمُصَۣيْطِرُونَ
    _case("almusaytirun", KhilafId.ALMUSAYTIRUN, "52:37", 7,
          "ʔ a l m u s a j tˤ i rˤ u: n",
          "ʔ a l m u sˤ aˤ j tˤ i rˤ u: n", "saad"),
    # Hafs: بِمُصَيْطِرٍ
    _case("bimusaytir", KhilafId.BIMUSAYTIR, "88:22", 3,
          "b i m u s a j tˤ i r", "b i m u sˤ aˤ j tˤ i r", "saad"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_seen_sad(run):
    assert_case(run)
