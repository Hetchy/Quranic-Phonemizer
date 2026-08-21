"""`Phonemizer`/`PhonemizeResult` API tests.

The contract's worked example anchors the first case; module
functions are checked over a small sample.
"""
from __future__ import annotations

import dataclasses
import gc

import pytest

from quranic_phonemizer import Phonemizer, PhonemizeResult
from quranic_phonemizer import supported_riwayat, tajweed_rules
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.phonemize import edges as ed


def test_the_contracts_own_example_runs():
    r = Phonemizer().phonemize("2:255")
    assert r.phonemes()[:12] == (
        "ʔ", "a", "lˤlˤ", "aˤ:", "h", "u", "l", "a:", "ʔ", "i", "l", "a:",
    )
    assert (len(r.rules), len(r.spellings), len(r.attributions), len(r.modifiers)) == (
        83, 474, 295, 69,
    )


def _units_a_rule_acted_on(r) -> dict[int, set[int]]:
    """Per rule index, the units its own edges name, read off the published
    arrays alone: a modifier names a sound, so it reaches that sound's unit."""
    units_of_sound: dict[int, set[int]] = {}
    for a in r.attributions:
        if isinstance(a, ed.Hosts):
            units_of_sound.setdefault(a.sound, set()).add(a.unit)
    out: dict[int, set[int]] = {}
    for a in r.attributions:
        if a.by is not None:
            out.setdefault(a.by, set()).add(a.unit)
    for m in r.modifiers:
        out.setdefault(m.by, set()).update(units_of_sound.get(m.sound, ()))
    return out


def test_a_rule_publishes_only_a_unit_its_own_edges_name():
    """`host` is the unit beside the source that the rule itself acted on, so
    a consumer can reproduce it from the edges. A unit a rule only read to
    decide -- the letter a madd is classified against -- is not published."""
    r = Phonemizer().phonemize("2:255")
    acted_on = _units_a_rule_acted_on(r)
    for i, rule in enumerate(r.rules):
        if rule.host is not None:
            assert rule.host in acted_on[i], rule.rule.value
    merger_by = {
        a.by for a in r.attributions
        if isinstance(a, ed.MergedInto) and a.by is not None
    }
    assert merger_by and all(r.rules[i].host is not None for i in merger_by)
    classifying = [i for i, rule in enumerate(r.rules)
                   if rule.rule.value == "madd_munfasil"]
    assert classifying
    assert all(r.rules[i].host is None for i in classifying)


def test_an_ibdal_publishes_the_hamza_it_softened():
    """Started on, `ٱئْتُونِى` reads its quiescent hamza as the madd the kasra
    before it opens. That hamza is the rule's host, so a consumer drawing the
    letter can name what happened to it."""
    r = Phonemizer().phonemize("46:4:18")
    ibdal = [rule for rule in r.rules if rule.rule.value == "ibdal_hamza"]
    assert len(ibdal) == 1
    assert ibdal[0].host is not None and ibdal[0].host != ibdal[0].source


def test_the_document_is_its_sixteen_members_and_nothing_else():
    """Two instances over the same ref compare and print alike, and the
    document carries no hidden member beside the published ones."""
    a = Phonemizer().phonemize("1:1")
    b = Phonemizer().phonemize("1:1")
    assert a == b
    assert "_assembled" not in repr(a)
    field_names = {f.name for f in dataclasses.fields(PhonemizeResult)}
    assert "_assembled" not in field_names
    assert len(field_names) == 16


def test_a_copied_result_projects_the_same():
    """Every projection reads the published members, so `replace` returns a
    document that works rather than one whose every method raises."""
    r = Phonemizer().phonemize("2:255")
    copy = dataclasses.replace(r, ref="elsewhere")
    assert copy.ref == "elsewhere"
    assert copy.phonemes() == r.phonemes()
    assert copy.text("recited") == r.text("recited")
    for text in ("source", "recited"):
        for grouping in ("glyph", "cell"):
            got = copy.alignment(text=text, grouping=grouping)
            assert got == r.alignment(text=text, grouping=grouping)
    assert copy.respelling() == r.respelling()


def test_non_variant_identity_fields_are_flat():
    r = Phonemizer().phonemize("1:1")
    assert r.ref == "1:1"
    assert r.riwayah == "hafs"
    assert r.script == "uthmani"
    assert isinstance(r.extra_phonemes, frozenset)
    assert r.schema_version == "1"
    assert len(r.canon_digest) > 0


def test_a_different_ref_changes_the_digest_bearing_fields():
    a = Phonemizer().phonemize("1:1")
    b = Phonemizer().phonemize("1:2")
    assert a.ref != b.ref
    assert a.words[0].text != b.words[0].text


def test_phonemes_by_word_nests_one_tuple_per_word():
    r = Phonemizer().phonemize("1:1")
    by_word = r.phonemes(by="word")
    assert len(by_word) == len(r.words)
    assert tuple(t for word in by_word for t in word) == r.phonemes()


def test_phonemes_by_rejects_an_unknown_grouping():
    r = Phonemizer().phonemize("1:1")
    with pytest.raises(ValueError):
        r.phonemes(by="verse")


def test_source_text_concatenates_to_the_glyph_array():
    """Concatenating `char` in `source_index` order reproduces the source
    text."""
    r = Phonemizer().phonemize("1:1")
    assert r.text("source") == "".join(g.char for g in r.glyphs)


def test_recited_text_concatenates_to_the_rendered_array():
    r = Phonemizer().phonemize("1:1")
    assert r.text("recited") == "".join(g.char for g in r.rendered)


def test_text_rejects_an_unknown_side():
    r = Phonemizer().phonemize("1:1")
    with pytest.raises(ValueError):
        r.text("target")


def test_alignment_and_respelling_delegate_to_the_same_assembly():
    r = Phonemizer().phonemize("1:1")
    cells = r.alignment(text="source", grouping="cell")
    glyphs = r.alignment(text="source", grouping="glyph")
    assert len(cells) <= len(glyphs)
    blocks = r.respelling()
    assert blocks


def test_every_glyph_names_a_word_or_carries_no_word_at_all():
    """A structural glyph (a verse's own text has none) is absent here; the
    field exists and is exercised by the multi-word case instead."""
    r = Phonemizer().phonemize("2:255-2:256")
    assert any(g.word is None for g in r.glyphs)


def test_module_functions_answer_without_an_instance():
    assert supported_riwayat() == ("hafs",)
    rules = tajweed_rules("hafs")
    identifiers = {row[0] for row in rules}
    assert identifiers == {rule.value for rule in Rule}
    for identifier, english, arabic, summary in rules:
        assert identifier and english and arabic
        assert summary.endswith(".") and len(summary.split()) >= 5


def test_a_bare_phonemizer_is_hafs_uthmani():
    r = Phonemizer().phonemize("1:1")
    assert (r.riwayah, r.script) == ("hafs", "uthmani")


def test_suspended_gc_preserves_output_and_restores_enabled_state():
    phonemizer = Phonemizer()
    expected = phonemizer.phonemize("1")
    assert gc.isenabled()
    assert phonemizer.phonemize("1", suspend_gc=True) == expected
    assert gc.isenabled()


def test_suspended_gc_preserves_a_disabled_state_on_failure():
    gc.disable()
    try:
        with pytest.raises(ValueError):
            Phonemizer().phonemize("not-a-ref", suspend_gc=True)
        assert not gc.isenabled()
    finally:
        gc.enable()


def test_the_retired_projections_are_gone():
    with pytest.raises(ModuleNotFoundError):
        __import__("quranic_phonemizer.render.anchored")
    with pytest.raises(ModuleNotFoundError):
        __import__("quranic_phonemizer.render.recite")


def test_result_is_the_documented_dataclass_shape():
    r = Phonemizer().phonemize("1:1")
    assert isinstance(r, PhonemizeResult)
    for edge in r.spellings:
        assert isinstance(edge, ed.Supplies | ed.Witnesses | ed.Decorates | ed.Structural)
