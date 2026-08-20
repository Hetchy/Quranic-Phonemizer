"""Composed marks stay inside the unit they qualify. None supplies an opening
fact, so none mints a unit of its own."""
from __future__ import annotations

import pytest

from quranic_phonemizer.phonemize import edges as ed

from .support import built, only, opens_unit, supplies, units_named

# Each site names a mark that qualifies the letter it sits on.
SHADDA = ("52:1:1", "ّ")
MADDAH = ("2:255:2", "ٓ")
SILENCE_MARK = ("2:6:3", "۟")      # the zero over a silent alif
ISHMAM = ("12:11:6", "۫")
TASHIL = ("41:44:9", "۬")
TATWEEL = ("2:255:3", "ـ")
PAUSAL_ALIF = ("5:28:7", "ا")      # silent at wasl, said long at a pause

FOLDS = (SHADDA, MADDAH, SILENCE_MARK, ISHMAM, TASHIL, TATWEEL, PAUSAL_ALIF)


def _letter_units(a):
    return {
        s.unit for s in a.spellings
        if isinstance(s, ed.Supplies) and s.fact is ed.Fact.LETTER
    }


@pytest.mark.parametrize(("ref", "char"), FOLDS)
def test_a_composed_mark_opens_no_unit(ref, char):
    # ّ ٓ ۟ ۫ ۬ ـ ا
    a = built(ref)
    mark = only(a, char=char, word=0)
    assert not opens_unit(a, mark)
    assert ed.Fact.LETTER not in supplies(a, mark)


@pytest.mark.parametrize(("ref", "char"), FOLDS)
def test_a_composed_mark_folds_onto_a_letter_that_opens(ref, char):
    """The discriminating half: every unit the mark touches is one a letter
    already opened, so the mark qualifies a unit rather than being one."""
    # ّ ٓ ۟ ۫ ۬ ـ ا
    a = built(ref)
    mark = only(a, char=char, word=0)
    touched = units_named(a, mark)
    assert touched
    assert touched <= _letter_units(a)
