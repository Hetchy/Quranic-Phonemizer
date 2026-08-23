from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, pick, through


def elision(
    case_id: str,
    ref: str,
    words: tuple[int, int],
    phonemes: tuple[str, str],
    indopak_alif: str,
) -> Case:
    source = pick(
        hafs_uthmani={"ٱ": R("hamza_wasl_silent")},
        hafs_indopak={indopak_alif: R("hamza_wasl_silent")},
    )
    silent = pick(
        hafs_uthmani=("ٱ",),
        hafs_indopak=(indopak_alif,),
    )
    return Case(
        id=case_id,
        site=Site(hafs=(ref, words)),
        read=through(),
        phonemes=phonemes,
        char_rules=source,
        silent=silent,
    )


CASES = (
    # ذَٰلِكَ ٱلْكِتَابُ
    elision(
        "article", "2:2", (1, 2),
        ("ð a: l i k a", "l k i t a: b Q"), "ا",
    ),
    # قَالَ ٱدْخُلُوا
    elision(
        "verb", "7:38", (1, 2),
        ("q aˤ: l a", "d Q x u l u:"), "ا[2]",
    ),
    # إِنَّ ٱبْنِى
    elision(
        "conventional-noun", "11:45", (6, 7),
        ("ʔ i ñ a", "b Q n i:"), "ا[2]",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hamza_wasl_silent(run):
    assert_case(run)
