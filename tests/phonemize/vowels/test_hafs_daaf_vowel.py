from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from quranic_phonemizer.model.canon import Quality
from tests.support import (
    Expect,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    isolated,
    selected,
)

DAAF = Site(hafs=("30:54", (5, 10, 17)))

CASES = (
    # Hafs: ضَعْفٍ
    VariantCase(
        id="daaf-vowel",
        site=Site(hafs=("30:54", (5,))),
        selector=KhilafId.DAAF_HARAKA,
        faces={
            "fatha": Expect(read=isolated(), phonemes="dˤ aˤ ʕ f"),
            "damma": Expect(read=isolated(), phonemes="dˤ u ʕ f"),
        },
        default="fatha",
    ),
)

REGISTER = (
    pytest.param(5, id="30-54-5"),
    pytest.param(10, id="30-54-10"),
    pytest.param(17, id="30-54-17"),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_hafs_daaf_vowel(run):
    assert_case(run)


@pytest.mark.parametrize("word", REGISTER)
def test_daaf_register_accepts_both_vowels(word):
    opened = selected(DAAF, word, KhilafId.DAAF_HARAKA, "fatha")
    rounded = selected(DAAF, word, KhilafId.DAAF_HARAKA, "damma")
    assert opened.score.words[word - 1].slots[0].nucleus.quality is Quality.A
    assert rounded.score.words[word - 1].slots[0].nucleus.quality is Quality.U
