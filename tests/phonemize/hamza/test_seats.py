from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated


CASES = (
    # وَلُؤْلُؤًا
    Case(
        id="waw-seat",
        site=Site.shared("22:23", (19,)),
        read=isolated(),
        phonemes="w a l u ʔ l u ʔ a:",
    ),
    # يُؤْمِنُونَ
    Case(
        id="sakin-hamza-waw-seat",
        site=Site(hafs=("2:3", (2,))),
        read=isolated(),
        phonemes="j u ʔ m i n u: n",
    ),
    # يَأْكُلُونَ
    Case(
        id="sakin-hamza-alif-seat",
        site=Site(hafs=("2:275", (2,))),
        read=isolated(),
        phonemes="j a ʔ k u l u: n",
    ),
    # خَاطِئَةٍ
    Case(
        id="moving-hamza-yaa-seat",
        site=Site.shared("96:16", (3,)),
        read=isolated(),
        phonemes="x aˤ: tˤ i ʔ a h",
    ),
    # لِلْمَلَـٰٓئِكَةِ
    Case(
        id="seat-after-madd",
        site=Site.shared("2:30", (4,)),
        read=isolated(),
        phonemes="l i l m a l a: ʔ i k a h",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hamza_seats(run):
    assert_case(run)
