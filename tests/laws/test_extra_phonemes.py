"""Item 39: switching a toggle on changes no node and no edge, only the
token `phonemes()` reads off the same `Sound`. Each toggle's own off/on
site lives in the file that owns its rule."""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.phonemize import UnknownExtraPhoneme


def test_the_toggle_changes_no_node_and_no_edge():
    """`token` is the one field a toggle may move; every other field of
    every sound, and every edge, stays identical between the two documents."""
    off = Phonemizer().phonemize("41:44")
    on = Phonemizer(extra_phonemes=("emphatic_fatha",)).phonemize("41:44")
    bare = lambda sounds: [dataclasses.replace(s, token="") for s in sounds]
    assert bare(off.sounds) == bare(on.sounds)
    assert off.attributions == on.attributions
    assert off.modifiers == on.modifiers
    assert off.phonemes() != on.phonemes()


def test_an_unknown_extra_phoneme_is_rejected():
    with pytest.raises(UnknownExtraPhoneme):
        Phonemizer(extra_phonemes=("not_a_toggle",))
