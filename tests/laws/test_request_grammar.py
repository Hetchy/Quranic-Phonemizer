"""The ref grammar and the two things a ref may not do (01-contract sec 1.1)."""
from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import Location
from quranic_phonemizer.phonemize.request import (
    ClippedLedgerWordError,
    resolve_words,
)


@pytest.mark.parametrize(
    "ref",
    ["2", "2:255", "2:255-2:257", "2:255:3", "2:255:3-2:256:1"],
)
def test_same_depth_endpoints_resolve(hafs, ref):
    assert resolve_words(hafs.corpus, hafs.ledger, ref)


@pytest.mark.parametrize(
    "ref", ["2:255-3", "2-2:255", "2:255:3-2:256", "2:255-2:255:3"]
)
def test_mixed_depth_endpoints_raise(hafs, ref):
    with pytest.raises(ValueError, match="different depths"):
        resolve_words(hafs.corpus, hafs.ledger, ref)


def test_a_ref_outside_the_corpus_raises(hafs):
    with pytest.raises(ValueError):
        resolve_words(hafs.corpus, hafs.ledger, "999:1")


def test_a_range_clipping_a_ledger_addressed_word_raises(hafs):
    # 18:38 لَّـٰكِنَّا۠ -- the ledger addresses word 1 as a whole (seven alifs).
    with pytest.raises(ClippedLedgerWordError):
        resolve_words(hafs.corpus, hafs.ledger, "18:38:2-18:38:8")


@pytest.mark.parametrize("ref", ["18:38", "18:38:1-18:38:8", "18:38:1"])
def test_a_range_keeping_the_ledger_word_does_not_raise(hafs, ref):
    assert resolve_words(hafs.corpus, hafs.ledger, ref)[0] == Location(18, 38, 1)


def test_a_sub_verse_range_untouched_by_the_ledger_does_not_raise(hafs):
    # 2:7 has no ledger-addressed word; a partial range is unremarkable.
    words = resolve_words(hafs.corpus, hafs.ledger, "2:7:3-2:7:12")
    assert words[0] == Location(2, 7, 3)
    assert words[-1] == Location(2, 7, 12)
    assert len(words) == 10
