"""`تَأْمَ۫نَّا` at 12:11 is the only ishmam in this reading.

The lips round on a letter that is otherwise said as written, so the rule
names a sound it does not make and owns none of its own.
"""
from __future__ import annotations

from quranic_phonemizer.model import performance as pf
from quranic_phonemizer.model.canon import Rule

from tests.support import Site, for_each_riwayah

TAMANNA = Site(hafs=("12:11", (6,)))


def _the_ishmam(r) -> pf.Occurrence:
    found = [
        occurrence for occurrence in r.performance.occurrences
        if occurrence.rule is Rule.ISHMAM
    ]
    assert len(found) == 1
    return found[0]


@for_each_riwayah(TAMANNA, isolated=6)
def test_the_ishmam_names_one_letter_and_reads_nothing_beside_it(r):
    # تَأْمَ۫نَّا
    assert r.phonemes(6) == "taʔmaña:"
    occurrence = _the_ishmam(r)
    assert occurrence.subjects == (r.score.words[5].slots[2].id,)
    assert occurrence.context == ()
    assert occurrence.boundary is None
    assert r.source_of("ishmam") == "م"
    assert r.host_of("ishmam") is None


@for_each_riwayah(TAMANNA, isolated=6)
def test_the_ishmam_classifies_the_consonant_and_owns_no_sound(r):
    """Its only edge is a classification, so a consumer drawing the meem can
    name the rule without the reading crediting it with the sound."""
    # تَأْمَ۫نَّا
    occurrence = _the_ishmam(r)
    assert [
        edge for edge in r.performance.attributions
        if edge.by == occurrence.id
    ] == []
    modifiers = [
        modifier for modifier in r.performance.modifiers
        if modifier.by == occurrence.id
    ]
    assert len(modifiers) == 1
    assert isinstance(modifiers[0], pf.Classifies)
    assert r.rules_on_sound(6, "m") == {"ishmam"}


@for_each_riwayah(TAMANNA, ibtidaa=6, wasl=6)
def test_the_rounding_holds_whichever_way_the_word_is_read(r):
    """It is a fact of the word, not of the junction after it."""
    # تَأْمَ۫نَّا
    assert r.phonemes(6) == "taʔmaña:"
    assert "ishmam" in r.rules_on_char(6, "۫")
