"""The lexicon: its sections are data, and its budgets are this gate.

The ceiling used to be raised from `load_lexicon`, so a breach was a package
that would not import. Here it is a red test with the numbers in the message.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from quranic_phonemizer.canon.lexicon import (
    EMPTY,
    MatchMode,
    LexiconError,
    load_clitic_pronouns,
    load_lexicon,
)
from quranic_phonemizer.riwayat.hafs.resources import DATA

SHARED = DATA.parents[1] / "shared"


@pytest.fixture(scope="module")
def lexicon():
    return load_lexicon(
        DATA / "lexicon.yaml",
        clitics=load_clitic_pronouns(SHARED / "morphology.yaml"),
    )


def _text(name: str = "lexicon.yaml") -> str:
    root = SHARED if name == "morphology.yaml" else DATA
    return (root / name).read_text(encoding="utf-8")


def _load(tmp_path: Path, text: str):
    path = tmp_path / "lexicon.yaml"
    path.write_text(text, encoding="utf-8")
    return load_lexicon(path, clitics=frozenset({"هم"}))


# -- the budget -----------------------------------------------------------
def test_no_section_is_over_its_budget(lexicon):
    """A rise past a ceiling means a rule is missing, not that the corpus is
    irregular. Reviewable here; it used to break the import instead."""
    over = {
        name: (len(section.entries), section.budget)
        for name, section in lexicon.sections.items()
        if len(section.entries) > section.budget
    }
    assert not over, f"sections over budget (size, ceiling): {over}"


def test_every_section_declares_a_budget(lexicon):
    """Falsifier: `wasl_kasra` had no ceiling and was spliced past the table
    that held them, so the one section nobody bounded was invisible."""
    assert lexicon.sections
    assert all(section.budget > 0 for section in lexicon.sections.values())


# -- the four match modes -------------------------------------------------
def test_exact_takes_the_key_and_nothing_else(lexicon):
    assert lexicon.is_divine_name("له")
    assert not lexicon.is_divine_name("لهو")


def test_clitic_takes_a_stem_plus_one_attached_pronoun(lexicon):
    assert lexicon.is_form_eight_lam("ءلتقط")
    assert lexicon.is_form_eight_lam("ءلتقطه")
    assert not lexicon.is_form_eight_lam("ءلتقطون")


def test_inflected_also_takes_a_stem_of_three_as_a_prefix(lexicon):
    assert lexicon.is_wasl_exempt("ءمن")
    assert lexicon.is_wasl_exempt("ءمنكم")
    assert lexicon.is_wasl_exempt("ءمنهم")


def test_a_stem_under_three_letters_is_not_a_prefix(lexicon):
    """`ءل` is an entry, and matching it as a prefix would swallow the whole
    definite article. Length is what keeps a short entry specific."""
    assert lexicon.is_wasl_exempt("ءل")
    assert not lexicon.is_wasl_exempt("ءلكتب")


def test_proclitic_takes_the_key_after_exactly_one_proclitic(lexicon):
    assert lexicon.is_pausal("ءaنa")
    assert lexicon.is_pausal("وaءaنa")
    assert not lexicon.is_pausal("وaلaءaنa")


def test_a_lexicon_with_no_sections_answers_no_to_everything():
    assert not EMPTY.is_divine_name("له")
    assert not EMPTY.is_wasl_exempt("ءمن")
    assert not EMPTY.pausal_lexemes


# -- what the file must say about itself ----------------------------------
def test_an_unknown_match_mode_is_a_load_error(tmp_path):
    """The sections are data and the modes are code: a mode the resolver has
    no branch for must not load as one it does."""
    text = _text().replace("match: exact", "match: roughly", 1)
    with pytest.raises(LexiconError, match="not a match mode"):
        _load(tmp_path, text)


def test_a_section_missing_its_budget_is_a_load_error(tmp_path):
    text = _text().replace("    budget: 5\n", "", 1)
    assert text != _text()
    with pytest.raises(ValueError, match="budget"):
        _load(tmp_path, text)


def test_a_repeated_entry_is_a_load_error(tmp_path):
    """A set would swallow it before the budget counts it, so the file would
    show more rows than the ceiling ever sees."""
    text = _text().replace('entries: ["له", "لهم"]', 'entries: ["له", "له"]')
    with pytest.raises(LexiconError, match="twice"):
        _load(tmp_path, text)


def test_the_schema_version_is_checked(tmp_path):
    with pytest.raises(LexiconError, match="schema_version"):
        _load(tmp_path, _text().replace("schema_version: 2", "schema_version: 1"))


def test_every_declared_mode_is_one_the_resolver_has(lexicon):
    """Falsifier for the enum being closed: a mode with no matcher would
    resolve to no match rather than to an error."""
    assert {s.match for s in lexicon.sections.values()} <= set(MatchMode)


# -- the shared half ------------------------------------------------------
def test_the_clitic_pronouns_are_shared_not_this_riwayah_s(lexicon):
    """Which pronouns attach to a word is a fact about Arabic. Under `hafs/`
    it would assert something false about every other riwayah."""
    assert (SHARED / "morphology.yaml").exists()
    assert not (DATA / "morphology.yaml").exists()
    assert lexicon.clitics


def test_a_repeated_clitic_pronoun_is_a_load_error(tmp_path):
    path = tmp_path / "morphology.yaml"
    path.write_text(
        _text("morphology.yaml").replace('"ه", "هم"', '"ه", "ه"'), encoding="utf-8"
    )
    with pytest.raises(LexiconError, match="twice"):
        load_clitic_pronouns(path)
