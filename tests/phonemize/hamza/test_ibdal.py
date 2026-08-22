from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, isolated, pick, through


REPLACEMENT_RULES = R("ibdal_hamza", "madd_badal", "madd_tabii")


def _started(case_id: str, ref: str, word: int, phonemes: str, root: str) -> Case:
    return Case(
        id=case_id,
        site=Site(hafs=(ref, (word,))),
        read=isolated(),
        phonemes=phonemes,
        char_rules=pick(
            hafs_uthmani={"ٱ": R("wasl_start"), root: REPLACEMENT_RULES},
            hafs_indopak={"ا": R("wasl_start"), "@hamza_mark": REPLACEMENT_RULES},
        ),
        sound_rules={"ʔ": R("wasl_start"), phonemes.split()[1]: REPLACEMENT_RULES},
    )


def _joined(
    case_id: str,
    ref: str,
    words: tuple[int, int],
    phonemes,
    root: str,
    wasl: str = "[2]",
) -> Case:
    return Case(
        id=case_id,
        site=Site(hafs=(ref, words)),
        read=through(),
        phonemes=phonemes,
        char_rules=pick(
            hafs_uthmani={f"ٱ{wasl}": R("wasl_elision")},
            hafs_indopak={f"ا{wasl}": R("wasl_elision")},
        ),
        absent_char_rules=pick(
            hafs_uthmani={root: R("ibdal_hamza")},
            hafs_indopak={"@hamza_mark": R("ibdal_hamza")},
        ),
    )


CASES = (
    # ٱئْتُونِى
    _started("iti-start", "46:4", 18, "ʔ i: t u: n i:", "ئ"),
    # ٱلْمَلِكُ ٱئْتُونِى
    _joined(
        "iti-joined", "12:50", (2, 3),
        ("ʔ a l m a l i k u", "ʔ t u: n i:"), "ئ",
    ),
    # ٱئْذَن
    _started("ithan-start", "9:49", 4, "ʔ i: ð a n", "ئ"),
    # يَقُولُ ٱئْذَن
    _joined(
        "ithan-joined", "9:49", (3, 4),
        ("j a q u: l u", "ʔ ð a n"), "ئ", wasl="",
    ),
    # ٱؤْتُمِنَ
    _started("utumin-start", "2:283", 16, "ʔ u: t u m i n", "ؤ"),
    # ٱلَّذِى ٱؤْتُمِنَ
    _joined(
        "utumin-joined", "2:283", (15, 16),
        ("ʔ a ll a ð i", "ʔ t u m i n"), "ؤ",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_ibdal(run):
    assert_case(run)
