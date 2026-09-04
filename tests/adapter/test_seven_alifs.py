"""The seven alifs are sited by word location, not by vocalised skeleton.

Falsified by any of these reverting to skeleton-based lexicon matching,
which cannot tell an ordinary long `أَنَا` from one of the seven alifs.
"""
from __future__ import annotations

import pytest
from conftest import score_for

from quranic_phonemizer.model.address import Script, VerseRef

#: Every `أَنَا` / `وَأَنَا` / `فَأَنَا` site where Uthmani draws no `۠`. A
#: vocalised skeleton cannot tell these from the seven; the location can.
NOT_ONE_OF_THE_SEVEN = [
    (2, 160, 9), (15, 49, 4), (15, 89, 3), (20, 13, 1), (20, 14, 2),
    (27, 9, 3), (28, 30, 16),
]

#: A representative site Uthmani does mark `۠`, unreachable in IndoPak
#: except through the Ledger.
ONE_OF_THE_SEVEN = (2, 258, 21)


@pytest.mark.parametrize("surah,ayah,word", NOT_ONE_OF_THE_SEVEN)
def test_an_unmarked_ana_is_an_ordinary_long_a(packed, hafs, surah, ayah, word):
    score = score_for(packed, hafs, surah, ayah)
    nucleus = score.words[word - 1].slots[-1].nucleus
    assert nucleus.is_long
    assert not nucleus.is_pausal_long


@pytest.mark.parametrize("script", [Script.UTHMANI, Script.INDOPAK])
def test_a_marked_ana_is_pausal_in_both_scripts(sources, hafs, script):
    surah, ayah, word = ONE_OF_THE_SEVEN
    verse = VerseRef(surah, ayah)
    words = sources[script][(surah, ayah)]
    score = hafs.build(hafs.read(script, verse, words)).score
    assert score.words[word - 1].slots[-1].nucleus.is_pausal_long
