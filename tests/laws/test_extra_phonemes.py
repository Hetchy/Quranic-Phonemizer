"""The public `Phonemizer()` default for each toggle, distinct from the
harness gate the per-rule files assert. Toggling changes no node and no
edge, only the token."""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.phonemize import UnknownExtraPhoneme


def _sound_index(r, predicate) -> int:
    for i, sound in enumerate(r.sounds):
        if predicate(sound):
            return i
    raise AssertionError("no sound in this ref matches")


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


def test_tashil_defaults_off():
    off = Phonemizer().phonemize("41:44")
    on = Phonemizer(extra_phonemes=("tashil",)).phonemize("41:44")
    i = _sound_index(off, lambda s: s.kind.value == "consonant" and s.eased)
    assert off.phonemes()[i] == "ʔ"
    assert on.phonemes()[i] == "ʔ̞"


def test_emphatic_fatha_defaults_off():
    off = Phonemizer().phonemize("41:44")
    on = Phonemizer(extra_phonemes=("emphatic_fatha",)).phonemize("41:44")
    i = _sound_index(off, lambda s: s.kind.value == "vowel" and s.emphatic)
    assert off.phonemes()[i] == "a:"
    assert on.phonemes()[i] == "aˤ:"


def test_emphatic_ikhfaa_defaults_off():
    off = Phonemizer().phonemize("2:4")
    on = Phonemizer(extra_phonemes=("emphatic_ikhfaa",)).phonemize("2:4")
    i = _sound_index(off, lambda s: s.ghunnah and s.emphatic)
    assert off.phonemes()[i] == "ŋ"
    assert on.phonemes()[i] == "ŋˤ"


def test_imala_defaults_off():
    off = Phonemizer().phonemize("11:41:6")
    on = Phonemizer(extra_phonemes=("imala",)).phonemize("11:41:6")
    i = _sound_index(off, lambda s: s.quality and s.quality.value == "e")
    assert off.phonemes()[i] == "i:"
    assert on.phonemes()[i] == "e:"


def test_qalqala_degree_defaults_to_one_token():
    off = Phonemizer().phonemize("96:1")
    on = Phonemizer(extra_phonemes=("qalqala_degree",)).phonemize("96:1")
    sughra = _sound_index(off, lambda s: s.degree and s.degree.value == "sughra")
    kubra = _sound_index(off, lambda s: s.degree and s.degree.value == "kubra")
    assert (off.phonemes()[sughra], on.phonemes()[sughra]) == ("Q", "Q")
    assert (off.phonemes()[kubra], on.phonemes()[kubra]) == ("Q", "QQ")


def test_an_unknown_extra_phoneme_is_rejected():
    with pytest.raises(UnknownExtraPhoneme):
        Phonemizer(extra_phonemes=("not_a_toggle",))
