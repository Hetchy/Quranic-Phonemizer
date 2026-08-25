from __future__ import annotations

import pytest

from tests.support import (
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    explicit,
    pick,
    through,
)


def elision(
    case_id: str,
    ref: str,
    words: tuple[int, int],
    joined: tuple[str, str],
    restarted: tuple[str, str],
    start_rule: str,
    indopak_alif: str,
    warsh_alif: str | None = None,
) -> StateCase:
    def per_script(rule: str):
        return pick(
            hafs_uthmani={"ٱ": R(rule)},
            hafs_indopak={indopak_alif: R(rule)},
            warsh_uthmani={warsh_alif or indopak_alif: R(rule)},
        )

    return StateCase(
        id=case_id,
        site=Site.shared(ref, words),
        states={
            "joined": Expect(
                read=through(),
                phonemes=joined,
                char_rules=per_script("hamza_wasl_silent"),
                silent=pick(
                    hafs_uthmani=("ٱ",),
                    hafs_indopak=(indopak_alif,),
                    warsh_uthmani=(warsh_alif or indopak_alif,),
                ),
            ),
            "restarted": Expect(
                read=explicit(ibtidaa=words[0], waqf=words),
                phonemes=restarted,
                char_rules=per_script(start_rule),
                absent_char_rules=per_script("hamza_wasl_silent"),
            ),
        },
    )


CASES = (
    # Hafs: ذَٰلِكَ ٱلْكِتَـٰبُ
    # Warsh: ذَٰلِكَ اَ۬لْكِتَٰبُ
    elision(
        "article", "2:2", (1, 2),
        ("ð a: l i k a", "l k i t a: b Q"),
        ("ð a: l i k", "ʔ a l k i t a: b Q"),
        "hamza_wasl_fatha", "ا",
    ),
    # Hafs: قَالَ ٱدْخُلُوا۟
    # Warsh: قَالَ اَ۟دْخُلُواْ
    elision(
        "verb", "7:38", (1, 2),
        ("q aˤ: l a", "d Q x u l u:"),
        ("q aˤ: l", "ʔ u d Q x u l u:"),
        "hamza_wasl_damma", "ا[2]",
    ),
    # Hafs: إِنَّ ٱبْنِى
    # Warsh: إِنَّ اَ۪بْنِے
    elision(
        "conventional-noun", "11:45", (6, 7),
        ("ʔ i ñ a", "b Q n i:"),
        ("ʔ i ñ", "ʔ i b Q n i:"),
        "hamza_wasl_kasra", "ا[2]", "ا",
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hamza_wasl_silent(run):
    assert_case(run)
