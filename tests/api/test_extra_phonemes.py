"""The public `Phonemizer()` default for each toggle, distinct from the
harness gate the per-rule files assert. Toggling changes no node and no
edge, only the token."""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer import Phonemizer, UnknownExtraPhoneme


def _differences(off, on) -> list[tuple[str, str]]:
    return [pair for pair in zip(off.phonemes(), on.phonemes()) if pair[0] != pair[1]]


def test_the_toggle_changes_no_node_and_no_edge():
    """`token` is the one field a toggle may move; every other field of
    every sound, and every edge, stays identical between the two documents."""
    off = Phonemizer().analyse("2:29")
    on = Phonemizer(extra_phonemes=("emphatic_fatha",)).analyse("2:29")
    bare = lambda sounds: [dataclasses.replace(s, token="") for s in sounds]
    assert bare(off.sounds) == bare(on.sounds)
    assert off.words == on.words
    assert off.boundaries == on.boundaries
    assert off.rule_occurrences == on.rule_occurrences
    assert off.mergers == on.mergers
    assert off.phonemes() != on.phonemes()


def test_hafs_tashil_defaults_off():
    off = Phonemizer().analyse("41:44")
    on = Phonemizer(extra_phonemes=("tashil",)).analyse("41:44")
    assert ("ʔ", "ʔ̞") in _differences(off, on)


def test_warsh_tashil_is_always_rendered_and_not_an_extra():
    result = Phonemizer(riwayah="warsh").analyse("6:19:19")
    assert "ʔ̞" in result.phonemes()
    assert result.analysis.extra_phonemes == frozenset()

    with pytest.raises(UnknownExtraPhoneme):
        Phonemizer(riwayah="warsh", extra_phonemes=("tashil",))


def test_emphatic_fatha_defaults_off_but_emphatic_alef_is_always_written():
    short_off = Phonemizer().analyse("2:29")
    short_on = Phonemizer(extra_phonemes=("emphatic_fatha",)).analyse("2:29")
    assert ("a", "aˤ") in _differences(short_off, short_on)

    alef_off = Phonemizer().analyse("41:44")
    alef_on = Phonemizer(extra_phonemes=("emphatic_fatha",)).analyse("41:44")
    assert "aˤ:" in alef_off.phonemes()
    assert "aˤ:" in alef_on.phonemes()


def test_emphatic_ikhfaa_defaults_off():
    off = Phonemizer().analyse("2:4")
    on = Phonemizer(extra_phonemes=("emphatic_ikhfaa",)).analyse("2:4")
    assert ("ŋ", "ŋˤ") in _differences(off, on)


def test_imala_defaults_off():
    off = Phonemizer().analyse("11:41:6")
    on = Phonemizer(extra_phonemes=("imala",)).analyse("11:41:6")
    assert ("i:", "e:") in _differences(off, on)


def test_qalqala_degree_defaults_to_one_token():
    off = Phonemizer().analyse("96:1")
    on = Phonemizer(extra_phonemes=("qalqala_degree",)).analyse("96:1")
    assert "Q" in off.phonemes()
    assert ("Q", "QQ") in _differences(off, on)


def test_an_unknown_extra_phoneme_is_rejected():
    with pytest.raises(UnknownExtraPhoneme):
        Phonemizer(extra_phonemes=("not_a_toggle",))
