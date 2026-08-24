from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # Hafs: وَمِمَّا
    # Warsh: وَمِمَّا
    Case(
        id="doubled-meem",
        site=Site.shared("2:3", (6,)),
        read=isolated(),
        phonemes="w a m i m̃ a:",
        char_rules={"م[2]": R("ghunnah_mushaddadah")},
        sound_rules={"m̃": R("ghunnah_mushaddadah")},
    ),
    # Hafs: ٱلنَّاسِ
    # Warsh: اَ۬لنَّاسِ
    Case(
        id="article-doubled-noon",
        site=Site.shared("2:8", (2,)),
        read=isolated(),
        phonemes="ʔ a ñ a: s",
        char_rules={
            "ل": R("lam_shamsiyyah"),
            "ن": R("ghunnah_mushaddadah"),
        },
        sound_rules={"ñ": R("ghunnah_mushaddadah", "lam_shamsiyyah")},
    ),
    # Hafs: ٱلْمَغْضُوبِ
    # Warsh: اِ۬لْمَغْضُوبِ
    Case(
        id="plain-meem-contrast",
        site=Site.shared("1:7", (6,)),
        read=isolated(),
        phonemes="ʔ a l m a ɣ dˤ u: b Q",
        absent_char_rules={"م": R("ghunnah_mushaddadah")},
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_ghunnah_mushaddadah(run):
    assert_case(run)
