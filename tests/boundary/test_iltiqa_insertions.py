"""Two quiescent letters meet across a join and a vowel is put in to break
them. The vowel is added; nothing is merged away, so the repair leaves no
merger record behind.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.model import performance as pf
from quranic_phonemizer.model.canon import Rule

from tests.support import Site, reading

#: A tanween noon meeting the bare letter an elided prosthetic hamza leaves.
A_TANWEEN_TAKING_A_KASRA = [
    ("2:61", 30, "xaˤjrˤuni", "hbitˤu:"),      # خَيْرٌ ٱهْبِطُوا۟
    ("11:42", 8, "nu:ħuni", "bQnah"),          # نُوحٌ ٱبْنَهُۥ
    ("9:30", 3, "ʕuzajrˤuni", "bQn"),          # عُزَيْرٌ ٱبْنُ
    ("4:171", 31, "θala:θatuni", "ŋtahu:"),    # ثَلَـٰثَةٌ ٱنتَهُوا۟
    ("7:8", 2, "jawmaʔiðini", "lħaqqQ"),       # يَوْمَئِذٍ ٱلْحَقُّ
]

#: The one place a spelled-out opening runs into an elided prosthetic hamza.
ALIF_LAM_MEEM_ALLAH = Site(hafs=("3:1", (1,)))


def _at_boundary(r, rule: Rule, word: int) -> pf.Occurrence:
    """The occurrence of `rule` resolving the junction after `word`."""
    found = [
        occurrence for occurrence in r.performance.occurrences
        if occurrence.rule is rule and occurrence.boundary == word - 1
    ]
    assert len(found) == 1, f"{rule.value} at {word}: {found}"
    return found[0]


def _mergers(r, occurrence: pf.Occurrence):
    return [
        edge for edge in r.performance.attributions
        if isinstance(edge, pf.MergedInto) and edge.by == occurrence.id
    ]


def _hosted(r, occurrence: pf.Occurrence):
    return [
        edge for edge in r.performance.attributions
        if isinstance(edge, (pf.Hosts, pf.Inserted)) and edge.by == occurrence.id
    ]


@pytest.mark.parametrize(
    ("ref", "word", "first", "second"), A_TANWEEN_TAKING_A_KASRA
)
def test_a_tanween_noon_takes_a_kasra_to_reach_the_next_word(
    ref, word, first, second
):
    r = reading(Site(hafs=(ref, (word, word + 1))), ibtidaa=word, waqf=word + 1)
    assert (r.phonemes(word), r.phonemes(word + 1)) == (first, second)
    occurrence = _at_boundary(r, Rule.ILTIQA_KASRA, word)
    assert occurrence.subjects == (r.score.words[word - 1].slots[-1].id,)
    assert occurrence.context == (r.score.words[word].slots[0].id,)


@pytest.mark.parametrize(
    ("ref", "word", "first", "second"), A_TANWEEN_TAKING_A_KASRA
)
def test_that_kasra_is_put_in_rather_than_merged(ref, word, first, second):
    """The falsifier for a repair read as an assimilation: a `MergedInto`
    citing it would say a letter was lost, and none is."""
    r = reading(Site(hafs=(ref, (word, word + 1))), ibtidaa=word, waqf=word + 1)
    occurrence = _at_boundary(r, Rule.ILTIQA_KASRA, word)
    assert _mergers(r, occurrence) == []
    assert len(_hosted(r, occurrence)) == 1


def test_a_spelled_out_opening_takes_a_fatha_to_reach_the_divine_name():
    # الٓمٓ ٱللَّهُ
    r = reading(ALIF_LAM_MEEM_ALLAH, ibtidaa=1, wasl=1)
    assert (r.phonemes(1), r.phonemes(2)) == ("ʔalifla:m̃i:ma", "lla:hu")
    occurrence = _at_boundary(r, Rule.ILTIQA_FATHA, 1)
    assert occurrence.subjects == (r.score.words[0].slots[-1].id,)
    assert occurrence.context == (r.score.words[1].slots[0].id,)


def test_that_fatha_is_put_in_rather_than_merged():
    # الٓمٓ ٱللَّهُ
    r = reading(ALIF_LAM_MEEM_ALLAH, ibtidaa=1, wasl=1)
    occurrence = _at_boundary(r, Rule.ILTIQA_FATHA, 1)
    assert _mergers(r, occurrence) == []
    assert len(_hosted(r, occurrence)) == 1


def test_the_opening_stopped_on_needs_no_fatha_at_all():
    # الٓمٓ
    r = reading(ALIF_LAM_MEEM_ALLAH, isolated=1)
    assert r.phonemes(1) == "ʔalifla:m̃i:m"
    assert Rule.ILTIQA_FATHA not in {
        occurrence.rule for occurrence in r.performance.occurrences
    }
