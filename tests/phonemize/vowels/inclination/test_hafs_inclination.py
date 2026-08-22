from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # مَجْر۪ىٰهَا
    Case(
        id="majraha-collapsed",
        site=Site(hafs=("11:41", (6,))),
        read=isolated(),
        phonemes="m a ʒ Q r i: h a:",
        char_rules={"@imala_mark": R("imala")},
        sound_rules={"i:": R("imala")},
        extra_phonemes=(),
    ),
    # مَجْر۪ىٰهَا
    Case(
        id="majraha-rendered",
        site=Site(hafs=("11:41", (6,))),
        read=isolated(),
        phonemes="m a ʒ Q r e: h a:",
        char_rules={"@imala_mark": R("imala")},
        sound_rules={"e:": R("imala")},
        extra_phonemes=("imala",),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_inclination(run):
    assert_case(run)
