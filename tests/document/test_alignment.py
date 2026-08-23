"""Tests for phonemize/pairing.py over real sites."""
from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import Script
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.inscription import SilenceReason
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd
from quranic_phonemizer.phonemize.assemble import Assembled, assemble
from quranic_phonemizer.phonemize.pairing import alignment
from quranic_phonemizer.session import phonemize_request

#: Chosen for the fact-vocabulary and rule families they exercise:
#: mergers, tanween's three outcomes, tafkheem, madd, qalqala, waqf, wasl,
#: muqattaat and a broad sweep of the noon/meem families.
SAMPLE = (
    [(1, n) for n in range(1, 8)]
    + [(2, n) for n in range(1, 30)]
    + [(112, n) for n in range(1, 5)]
    + [
        (2, 256), (11, 42), (7, 176), (5, 28), (27, 22), (23, 118), (77, 20),
        (13, 4), (9, 109), (2, 85), (12, 11), (41, 44), (7, 1), (1, 7),
        (46, 4), (2, 255), (18, 1),
    ]
)


@pytest.fixture
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _assembled(hafs, pen, alphabet, ref, **boundary):
    session = phonemize_request(hafs, ref, **boundary)
    return assemble(session, pen, alphabet)


def _structural(a, text: str, glyphs) -> set[int]:
    """The `Structural` edge decides this, never `kind` and not `word`
    either. `rendered` carries no edges, so `word` is all it has."""
    if text == "source":
        return {s.glyph for s in a.spellings if isinstance(s, ed.Structural)}
    return {i for i, g in enumerate(glyphs) if g.word is None}


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_every_glyph_is_in_exactly_one_pairing_or_none(hafs, pen, alphabet, surah, ayah):
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    for text, glyphs in (("source", a.glyphs), ("recited", a.rendered)):
        for grouping in ("glyph", "cell"):
            seen: set[int] = set()
            for pairing in alignment(a, text=text, grouping=grouping):
                for g in pairing.glyphs:
                    assert g not in seen, (surah, ayah, text, grouping, g)
                    seen.add(g)
            included = set(range(len(glyphs))) - _structural(a, text, glyphs)
            assert seen == included, (surah, ayah, text, grouping)


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_every_source_glyph_carries_a_spelling_edge(hafs, pen, alphabet, surah, ayah):
    """A glyph with no edge at all is unreachable from any pairing, whatever
    `word` happens to say."""
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    named = {s.glyph for s in a.spellings}
    missing = [i for i in range(len(a.glyphs)) if i not in named]
    assert not missing, (surah, ayah, missing)


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_every_sound_is_owned_exactly_once(hafs, pen, alphabet, surah, ayah):
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    for text in ("source", "recited"):
        for grouping in ("glyph", "cell"):
            owned: set[int] = set()
            for pairing in alignment(a, text=text, grouping=grouping):
                for s in pairing.sounds:
                    assert s not in owned, (surah, ayah, text, grouping, s)
                    owned.add(s)
                for s in pairing.shares:
                    assert s not in pairing.sounds
            assert owned <= set(range(len(a.sounds)))
            if text == "recited":
                # Under text="recited" no sound takes a gap.
                assert owned == set(range(len(a.sounds))), (surah, ayah)


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_recited_alignment_has_no_gap_and_no_silence(hafs, pen, alphabet, surah, ayah):
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    for grouping in ("glyph", "cell"):
        for pairing in alignment(a, text="recited", grouping=grouping):
            assert pairing.after is None
            assert pairing.silent == ()


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_structural_glyphs_take_no_pairing(hafs, pen, alphabet, surah, ayah):
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    for text, glyphs in (("source", a.glyphs), ("recited", a.rendered)):
        for grouping in ("glyph", "cell"):
            named = {g for p in alignment(a, text=text, grouping=grouping) for g in p.glyphs}
            assert named.isdisjoint(_structural(a, text, glyphs))


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_a_cell_holds_two_letter_glyphs_only_for_a_tanween_noon(hafs, pen, alphabet, surah, ayah):
    """A muqattaat glyph names several units' letters through one glyph and is
    not this case at all -- no clause can split a single glyph."""
    from quranic_phonemizer.phonemize import edges as ed
    from quranic_phonemizer.phonemize.nodes import UnitOrigin

    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    letter_units = {}
    for s in a.spellings:
        if isinstance(s, ed.Supplies) and s.fact is ed.Fact.LETTER:
            letter_units.setdefault(s.glyph, []).append(s.unit)
    for pairing in alignment(a, text="source", grouping="cell"):
        glyphs = [g for g in pairing.glyphs if g in letter_units]
        if len(glyphs) <= 1:
            continue
        assert len(glyphs) == 2, (surah, ayah, pairing)
        units = [u for g in glyphs for u in letter_units[g]]
        tanween = [u for u in units if a.units[u].origin is UnitOrigin.TANWEEN]
        assert len(tanween) == 1, (surah, ayah, pairing, units)


def test_length_owns_before_quality_and_a_seat_owns_nothing(hafs, pen, alphabet):
    """`ٱلرَّحْمَـٰنِ`'s dagger vowel is owned by the dagger supplying its
    length. The fatha supplies only quality and the seat supplies nothing,
    so both present it and neither owns it."""
    a = _assembled(hafs, pen, alphabet, "1:1")
    source = alignment(a, text="source", grouping="glyph")
    dagger = next(
        p for p in source
        if a.glyphs[p.glyphs[0]].char == "ٰ" and p.sounds
    )
    for char in ("ـ", "َ"):
        presenting = [
            p for p in source
            if a.glyphs[p.glyphs[0]].char == char and p.shares == dagger.sounds
        ]
        assert presenting, char
        assert not any(p.sounds for p in presenting), char


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_the_silence_instances_are_the_tail_of_the_rules(hafs, pen, alphabet,
                                                         surah, ayah):
    """Assembly appends them last and nothing else mints one, which is how a
    copied document finds them again without being told where they start."""
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    at = [
        i for i, r in enumerate(a.rules)
        if r.rule is SilenceReason.ORTHOGRAPHIC
    ]
    assert at == list(range(len(a.rules) - len(at), len(a.rules)))

    # What the derivation gambles on is not contiguity but that a document
    # rebuilt from the published arrays lands every glyph on the same rule.
    copy = Assembled(
        words=a.words, glyphs=a.glyphs, rendered=a.rendered, units=a.units,
        sounds=a.sounds, rules=a.rules, spellings=a.spellings,
        attributions=a.attributions, modifiers=a.modifiers,
    )
    assert copy.orthographic_silence == a.orthographic_silence
    named = {i for i in a.orthographic_silence.values()}
    assert all(0 <= i < len(a.rules) for i in named)
    assert named >= set(at)


def test_a_seat_is_its_own_kind_and_not_structural(hafs, pen, alphabet):
    """Every tatweel in the corpus seats a mark, so none belongs to no word."""
    a = _assembled(hafs, pen, alphabet, "1:1")
    seats = [g for g in a.glyphs if g.char == "ـ"]
    assert seats
    assert all(g.kind is nd.GlyphKind.TATWEEL for g in seats)
    assert all(g.word is not None for g in seats)


def test_a_carrier_whose_length_was_taken_back_sounds_nothing(hafs, pen, alphabet):
    """فِى before a sakin: the reading keeps a short kasra, so the yaa that
    was written for the length shows the rule and presents no sound."""
    a = _assembled(hafs, pen, alphabet, "2:27:16-2:27:17")
    source = alignment(a, text="source", grouping="glyph")
    yaa = next(p for p in source if a.glyphs[p.glyphs[0]].char == "ى")
    assert not yaa.sounds and not yaa.shares
    assert yaa.silent == yaa.glyphs
    assert Rule.ILTIQA_SHORTENING in {a.rules[r].rule for r in yaa.rules}

    kasra = next(p for p in source if a.glyphs[p.glyphs[0]].char == "ِ")
    assert kasra.sounds and not a.sounds[kasra.sounds[0]].long

    # Presenting nothing must not part it from the letter it was written on.
    cell = next(
        c for c in alignment(a, text="source", grouping="cell")
        if yaa.glyphs[0] in c.glyphs
    )
    assert len(cell.glyphs) > 1
    assert a.glyphs[cell.glyphs[0]].char == "ف"


def test_the_divine_names_carrier_joins_its_owning_cell(hafs, pen, alphabet):
    # ٱللَّهِ at 2:27:4 -- one source cell, closed against it.
    a = _assembled(hafs, pen, alphabet, "2:27:2-2:27:8")
    source = alignment(a, text="source", grouping="cell")
    recited = alignment(a, text="recited", grouping="cell")
    from quranic_phonemizer.model.canon import Rule

    lam_cell = next(
        p for p in source
        if len(p.sounds) == 2
        and any(a.rules[r].rule is Rule.LAM_SHAMSIYYAH for r in p.rules)
    )
    assert len(lam_cell.sounds) == 2

    from quranic_phonemizer.phonemize.respell import respelling

    blocks = respelling(a, grouping="cell")
    block = next(b for b in blocks if source.index(lam_cell) in b.source)
    assert block.source, "the divine name's carrier must not empty the source"
    recited_text = [
        "".join(a.rendered[g].char for g in recited[i].glyphs) for i in block.recited
    ]
    assert len(recited_text) == 2


def test_a_soundless_insertion_takes_an_empty_source_block(hafs, pen, alphabet):
    # مِّن رَّبِّهِمْ style: a stop's inserted sukun owns no sound at all.
    from quranic_phonemizer.phonemize.respell import respelling

    a = _assembled(hafs, pen, alphabet, "2:5:3-2:5:4")
    blocks = respelling(a, grouping="glyph")
    assert any(not b.source and b.recited for b in blocks)

