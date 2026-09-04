from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated

CASES = (
    # Warsh: كَهَيْـَٔةِ
    Case(
        id="yaa-medial",
        site=Site(warsh=("3:49", (16,))),
        read=isolated(),
        phonemes="k a h a j ʔ a h",
        char_rules={"ي": R("madd_leen_mahmuz")},
        sound_rules={"j": R("madd_leen_mahmuz")},
        absent_char_rules={"@hamza_mark": R("madd_leen_mahmuz")},
    ),
    # Warsh: شَےْءٖ
    Case(
        id="yaa-final-hamza",
        site=Site(warsh=("2:20", (24,))),
        read=isolated(),
        phonemes="ʃ a j ʔ",
        char_rules={"ے": R("madd_leen_mahmuz")},
        sound_rules={"j": R("madd_leen_mahmuz")},
        absent_sound_rules={"j": R("madd_leen")},
    ),
    # Warsh: لِشَاْےْءٍ
    Case(
        id="yaa-source-alif-bridge",
        site=Site(warsh=("18:23", (3,))),
        read=isolated(),
        phonemes="l i ʃ a j ʔ",
        char_rules={"ے": R("madd_leen_mahmuz")},
        sound_rules={"j": R("madd_leen_mahmuz")},
    ),
    # Warsh: سَوْءَٰتِهِمَاۖ
    Case(
        id="sawat-keeps-both-identities",
        site=Site(warsh=("7:20", (10,))),
        read=isolated(),
        phonemes="s a w ʔ a: t i h i m a:",
        char_rules={
            "و": R("madd_leen_mahmuz"),
            "@dagger_alif": R("madd_badal"),
        },
        sound_rules={
            "w": R("madd_leen_mahmuz"),
            "a:[1]": R("madd_badal"),
        },
    ),
    # Warsh: مَوْئِلاٗۖ
    Case(
        id="mawilan-exclusion",
        site=Site(warsh=("18:58", (19,))),
        read=isolated(),
        phonemes="m a w ʔ i l a:",
        absent_char_rules={"و": R("madd_leen_mahmuz")},
        absent_sound_rules={"w": R("madd_leen_mahmuz")},
    ),
    # Warsh: اَ۬لْمَوْءُۥدَةُ
    Case(
        id="mawudati-exclusion-and-second-waw-badal",
        site=Site(warsh=("81:8", (2,))),
        read=isolated(),
        phonemes="ʔ a l m a w ʔ u: d a h",
        sound_rules={"u:": R("madd_badal")},
        absent_sound_rules={"w": R("madd_leen_mahmuz")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_madd_leen_mahmuz(run):
    assert_case(run)
