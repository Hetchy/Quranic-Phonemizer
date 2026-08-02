from __future__ import annotations

import pytest

from tests.support import Site, reading

MUTLAQ = [
    ("2:85", 38, "ʔaddunja:"),  # ٱلدُّنْيَا
    ("37:97", 4, "bunja:na:"),  # بُنْيَـٰنًا
    ("13:4", 10, "sˤinwa:n"),   # صِنْوَانٌ
    ("6:99", 23, "qinwa:n"),    # قِنْوَانٌ
]


@pytest.mark.parametrize(("ref", "word", "expected"), MUTLAQ)
def test_the_four_words_hold_their_noon_against_a_glide(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected
