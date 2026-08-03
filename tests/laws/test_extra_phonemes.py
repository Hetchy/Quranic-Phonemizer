"""Item 39: the four optional phonemes, gated at the notation.

`01-contract` section 3.2 -- switching one on changes no node and no edge,
only the token `phonemes()` reads off the same `Sound`.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer import Phonemizer
from quranic_phonemizer.phonemize import UnknownExtraPhoneme


def _sound_index(r, predicate) -> int:
    for i, sound in enumerate(r.sounds):
        if predicate(sound):
            return i
    raise AssertionError("no sound in this ref matches")


def test_emphatic_fatha_defaults_off():
    """41:44:9's raa/lam heaviness spreads onto its following fatha."""
    off = Phonemizer().phonemize("41:44")
    on = Phonemizer(extra_phonemes=("emphatic_fatha",)).phonemize("41:44")
    i = _sound_index(off, lambda s: s.kind.value == "vowel" and s.emphatic)
    assert off.phonemes()[i] == "a:"
    assert on.phonemes()[i] == "aˤ:"


def test_the_toggle_changes_no_node_and_no_edge():
    """`token` is the one field a toggle may move; every other field of
    every sound, and every edge, stays identical between the two documents."""
    import dataclasses

    off = Phonemizer().phonemize("41:44")
    on = Phonemizer(extra_phonemes=("emphatic_fatha",)).phonemize("41:44")
    bare = lambda sounds: [dataclasses.replace(s, token="") for s in sounds]
    assert bare(off.sounds) == bare(on.sounds)
    assert off.attributions == on.attributions
    assert off.modifiers == on.modifiers
    assert off.phonemes() != on.phonemes()


def test_tashil_gates_the_alphabet_directly():
    """No corpus site reaches this today -- `Consonant.eased` is validated
    by `Alphabet` but nothing in the engine's own default fill sets it, so
    the toggle is exercised at the notation layer it belongs to."""
    from quranic_phonemizer.api import alphabet
    from quranic_phonemizer.model.canon import CanonLetter
    from quranic_phonemizer.model.performance import Consonant

    a = alphabet()
    hamza = Consonant(letter=CanonLetter.HAMZA, eased=True)
    assert a.token(hamza, extra_phonemes=frozenset()) == "ʔ"
    assert a.token(hamza, extra_phonemes=frozenset({"tashil"})) == "ʔ̞"


def test_emphatic_ikhfaa_defaults_off():
    off = Phonemizer().phonemize("2:4")
    on = Phonemizer(extra_phonemes=("emphatic_ikhfaa",)).phonemize("2:4")
    i = _sound_index(off, lambda s: s.ghunnah and s.emphatic)
    assert off.phonemes()[i] == "ŋ"
    assert on.phonemes()[i] == "ŋˤ"


def test_qalqala_degree_defaults_to_one_token():
    """96:1 carries both a sughra and a kubra site; the toggle doubles only
    the kubra one, since sughra and its extended form share a token."""
    off = Phonemizer().phonemize("96:1")
    on = Phonemizer(extra_phonemes=("qalqala_degree",)).phonemize("96:1")
    sughra = _sound_index(off, lambda s: s.degree and s.degree.value == "sughra")
    kubra = _sound_index(off, lambda s: s.degree and s.degree.value == "kubra")
    assert (off.phonemes()[sughra], on.phonemes()[sughra]) == ("Q", "Q")
    assert (off.phonemes()[kubra], on.phonemes()[kubra]) == ("Q", "QQ")


def test_an_unknown_extra_phoneme_is_rejected():
    with pytest.raises(UnknownExtraPhoneme):
        Phonemizer(extra_phonemes=("not_a_toggle",))
