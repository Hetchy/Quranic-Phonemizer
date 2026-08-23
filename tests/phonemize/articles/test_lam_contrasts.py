from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, through


CASES = (
    # يَوْمَ ٱلْتَقَى
    Case(
        id="lexical-lam",
        site=Site(hafs=("3:155", (5, 6))),
        read=through(),
        phonemes=("j a w m a", "l t a q aˤ:"),
        absent_char_rules={"ل": R("lam_shamsiyyah", "lam_qamariyyah")},
    ),
    # وَلِبَاسُ ٱلتَّقْوَىٰ
    Case(
        id="article-lam",
        site=Site(hafs=("7:26", (10, 11))),
        read=through(),
        phonemes=("w a l i b a: s u", "tt a q Q w a:"),
        char_rules={"ل[2]": R("lam_shamsiyyah")},
        sound_rules={"tt": R("lam_shamsiyyah")},
    ),
    # ٱلَّيْلِ
    Case(
        id="one-lam-rasm",
        site=Site(hafs=("2:164", (7,))),
        read=isolated(),
        phonemes="ʔ a ll a j l",
        absent_char_rules={"ل[1]": R("lam_shamsiyyah")},
        absent_sound_rules={"ll": R("lam_shamsiyyah")},
    ),
    # ءَالذَّكَرَيْنِ
    Case(
        id="interrogative-article",
        site=Site(hafs=("6:143", (10,))),
        read=isolated(),
        phonemes="ʔ a: ðð a k a rˤ aˤ j n",
        char_rules={"ل": R("lam_shamsiyyah")},
        sound_rules={"ðð": R("lam_shamsiyyah")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_lam_contrasts(run):
    assert_case(run)
