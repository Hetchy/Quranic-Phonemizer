from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, joining


CASES = (
    # Warsh: ءَادَمَ
    Case(
        id="ordinary",
        site=Site(warsh=("2:31", (2,))),
        read=isolated(),
        phonemes="ʔ a: d a m",
        char_rules={"ا": R("madd_badal")},
        sound_rules={"a:": R("madd_badal")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # Warsh: مَـَٔابٖۖ
    Case(
        id="pausal-arid-overlap",
        site=Site(warsh=("13:29", (8,))),
        read=isolated(),
        phonemes="m a ʔ a: b Q",
        char_rules={"ا": R("madd_badal", "madd_arid_lissukun")},
        sound_rules={"a:": R("madd_badal", "madd_arid_lissukun")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # Warsh: يُومِنُونَ
    Case(
        id="general-ibdal-is-not-badal",
        site=Site(warsh=("2:3", (2,))),
        read=isolated(),
        phonemes="j u: m i n u: n",
        char_rules={"و[1]": R("ibdal_hamza", "madd_tabii")},
        sound_rules={"u:[1]": R("ibdal_hamza", "madd_tabii")},
        absent_sound_rules={"u:[1]": R("madd_badal")},
    ),
    # Warsh: يُوَ۬اخِذُ
    Case(
        id="ibdal-changed-badal",
        site=Site(warsh=("16:61", (2,))),
        read=isolated(),
        phonemes="j u w a: x i ð",
        char_rules={
            "و": R("ibdal_hamza"),
            "ا": R("madd_badal"),
        },
        sound_rules={
            "w": R("ibdal_hamza"),
            "a:": R("madd_badal"),
        },
        absent_sound_rules={
            "w": R("madd_badal"),
            "a:": R("ibdal_hamza", "madd_tabii"),
        },
    ),
    # Warsh: بَلَداً اٰمِناٗ (superscript alif after source alif, not maddah)
    Case(
        id="naql-changed-badal",
        site=Site(warsh=("2:126", (7, 8))),
        read=joining(),
        phonemes=("b a l a d a n a", "a: m i n a"),
        char_rules={
            "ا[2]": R("naql"),
            "@dagger_alif": R("madd_badal"),
        },
        sound_rules={"a:": R("madd_badal")},
        absent_sound_rules={"a:": R("madd_tabii")},
    ),
    # Warsh: إِسْرَآءِيلَ
    Case(
        id="fixed-qasr-israel-keeps-badal",
        site=Site(warsh=("2:40", (2,))),
        read=isolated(),
        phonemes="ʔ i s rˤ aˤ: ʔ i: l",
        char_rules={"ي": R("madd_badal", "madd_arid_lissukun")},
        sound_rules={"i:": R("madd_badal", "madd_arid_lissukun")},
        absent_sound_rules={"i:": R("madd_tabii")},
    ),
    # Warsh: مَسْـُٔولاٗۖ
    Case(
        id="sakin-before-hamza-keeps-badal",
        site=Site(warsh=("17:34", (17,))),
        read=isolated(),
        phonemes="m a s ʔ u: l a:",
        char_rules={"و": R("madd_badal")},
        sound_rules={"u:": R("madd_badal")},
        absent_sound_rules={"u:": R("madd_tabii")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_warsh_madd_badal(run):
    assert_case(run)
