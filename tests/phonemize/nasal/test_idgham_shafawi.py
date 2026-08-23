from __future__ import annotations

import pytest

from tests.support import (
    Case,
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    explicit,
    through,
)


CASES = (
    # قُلُوبِهِم مَّرَضٌ
    StateCase(
        id="meem-meem-boundary",
        site=Site(hafs=("2:10", (2, 3))),
        states={
            "joined": Expect(
                read=through(),
                phonemes=("q u l u: b i h i", "m̃ a rˤ aˤ dˤ"),
                char_rules={
                    "م[1]": R("idgham_shafawi"),
                    "م[2]": R("idgham_shafawi"),
                },
                sound_rules={"m̃": R("idgham_shafawi")},
            ),
            "ibtidaa-on-host": Expect(
                read=explicit(ibtidaa=2, waqf=(2, 3)),
                phonemes=("q u l u: b i h i m", "m a rˤ aˤ dˤ"),
                char_rules={
                    "م[1]": R("izhar_shafawi"),
                },
                sound_rules={
                    "m[1]": R("izhar_shafawi"),
                },
                absent_char_rules={"م[1]": R("idgham_shafawi"),
                                   "م[2]": R("idgham_shafawi")},
            ),
        },
    ),
    # أَهْوَآءَهُم مَّثَلُ
    Case(
        id="verse-seam",
        site=Site(hafs=("47:14", (13, 14))),
        read=explicit(ibtidaa=13, wasl=13, waqf=14),
        phonemes=("ʔ a h w a: ʔ a h u", "m̃ a θ a l"),
        char_rules={"م[1]": R("idgham_shafawi"),
                    "م[2]": R("idgham_shafawi")},
        sound_rules={"m̃": R("idgham_shafawi")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_idgham_shafawi(run):
    assert_case(run)
