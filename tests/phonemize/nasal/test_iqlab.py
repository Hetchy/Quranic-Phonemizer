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
    isolated,
    pick,
    through,
)


CASES = (
    # يَنبَغِى
    Case(
        id="internal-noon",
        site=Site.shared("19:92", (2,)),
        read=isolated(),
        phonemes="j a ŋ b a ɣ i:",
        char_rules={"ن": R("iqlab")},
        sound_rules={"ŋ": R("iqlab")},
    ),
    # مِّن بَعْدِ
    VariantCase(
        id="written-noon-boundary",
        site=Site(hafs=("2:56", (3, 4))),
        selector=KhilafId.IQLAB_NASAL,
        faces={
            "assimilated": Expect(
                read=through(),
                phonemes=("m i ŋ", "b a ʕ d Q"),
                char_rules={"ن": R("iqlab")},
                sound_rules={"ŋ": R("iqlab")},
            ),
            "bilabial": Expect(
                read=through(),
                phonemes=("m i m̃", "b a ʕ d Q"),
                char_rules={"ن": R("iqlab")},
                sound_rules={"m̃": R("iqlab")},
            ),
        },
        default="assimilated",
        masked=Expect(
            read=explicit(ibtidaa=3, waqf=(3, 4)),
            phonemes=("m i n", "b a ʕ d Q"),
            char_rules={"ن": R("izhar")},
            sound_rules={"n": R("izhar")},
            absent_char_rules={"ن": R("iqlab")},
            absent_sound_rules={"n": R("iqlab")},
        ),
    ),
    # صُمٌّ بُكْمٌ
    Case(
        id="dammatan",
        site=Site.shared("2:18", (1, 2)),
        read=through(),
        phonemes=("sˤ u m̃ u ŋ", "b u k m"),
        char_rules=pick(
            hafs_uthmani={"@dammatan[1]": R("iqlab")},
            hafs_indopak={"@mini_meem": R("iqlab")},
            warsh_uthmani={"@mini_meem": R("iqlab")},
        ),
        sound_rules={"ŋ": R("iqlab")},
    ),
    # ذُرِّيَّةً بَعْضُهَا
    Case(
        id="fathatan",
        site=Site.shared("3:34", (1, 2)),
        read=through(),
        phonemes=("ð u rr i jj a t a ŋ", "b a ʕ dˤ u h a:"),
        char_rules=pick(
            hafs_uthmani={"@fathatan": R("iqlab")},
            hafs_indopak={"@mini_meem": R("iqlab")},
            warsh_uthmani={"@mini_meem": R("iqlab")},
        ),
        sound_rules={"ŋ": R("iqlab")},
    ),
    # كَافِرٍ بِهِۦ
    Case(
        id="kasratan",
        site=Site.shared("2:41", (10, 11)),
        read=through(),
        phonemes=("k a: f i r i ŋ", "b i h"),
        char_rules=pick(
            hafs_uthmani={"@kasratan": R("iqlab")},
            hafs_indopak={"@mini_meem": R("iqlab")},
            warsh_uthmani={"@mini_meem": R("iqlab")},
        ),
        sound_rules={"ŋ": R("iqlab")},
    ),
    # قُصُورًا بَلْ
    Case(
        id="verse-seam",
        site=Site.shared("25:10", (17, 18)),
        read=explicit(ibtidaa=17, wasl=17, waqf=18),
        phonemes=("q u sˤ u: rˤ aˤ ŋ", "b a l"),
        char_rules=pick(
            hafs_uthmani={"@fathatan": R("iqlab")},
            hafs_indopak={"@fathatan": R("iqlab")},
            warsh_uthmani={"@mini_meem": R("iqlab")},
        ),
        sound_rules={"ŋ": R("iqlab")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_iqlab(run):
    assert_case(run)
