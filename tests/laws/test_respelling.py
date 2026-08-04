"""`phonemize/respell.py`: the block law of 02-gate section 4.6."""
from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.phonemize.assemble import assemble
from quranic_phonemizer.phonemize.pairing import alignment
from quranic_phonemizer.phonemize.respell import respelling
from quranic_phonemizer.phonemize.session import phonemize_request

#: A verse each from the noon/meem, madd, tafkheem, waqf and muqattaat
#: families -- the block law is a closure over `alignment`, already swept
#: broadly by `test_pairing.py`.
SAMPLE = [
    (1, 1), (1, 7), (2, 2), (2, 255), (2, 256), (7, 1), (11, 42), (18, 1),
    (77, 20), (112, 4),
]


@pytest.fixture
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _assembled(hafs, pen, alphabet, ref):
    return assemble(phonemize_request(hafs, ref), pen, alphabet)


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_blocks_partition_both_alignments(hafs, pen, alphabet, surah, ayah):
    a = _assembled(hafs, pen, alphabet, f"{surah}:{ayah}")
    for grouping in ("glyph", "cell"):
        source = alignment(a, text="source", grouping=grouping)
        recited = alignment(a, text="recited", grouping=grouping)
        seen_source: set[int] = set()
        seen_recited: set[int] = set()
        for block in respelling(a, grouping=grouping):
            assert block.source or block.recited
            assert seen_source.isdisjoint(block.source)
            assert seen_recited.isdisjoint(block.recited)
            seen_source.update(block.source)
            seen_recited.update(block.recited)
        assert seen_source == set(range(len(source)))
        assert seen_recited == set(range(len(recited)))


def test_the_iwad_carrier_joins_the_block_its_sound_is_in(hafs, pen, alphabet):
    """01-contract 6.3's sound-ownership closure: the silenced fathatan
    reaches the recited madd through `from_glyphs` alone, but the alif that
    owns the lengthened sound joins only because both sides present it."""
    a = _assembled(hafs, pen, alphabet, "78:6")
    source = alignment(a, text="source", grouping="glyph")
    recited = alignment(a, text="recited", grouping="glyph")
    alif = next(
        i for i, p in enumerate(source)
        if p.sounds and "".join(a.glyphs[g].char for g in p.glyphs) == "ا"
    )
    fathatan = next(
        i for i, p in enumerate(source)
        if "".join(a.glyphs[g].char for g in p.glyphs) == "ً"
    )
    block = next(b for b in respelling(a, grouping="glyph") if alif in b.source)
    assert fathatan in block.source
    assert block.recited and set(source[alif].sounds) & set(
        recited[block.recited[0]].sounds
    )


def test_the_cross_word_merger_is_one_block(hafs, pen, alphabet):
    # هُدًى مِّن, 2:5:3-4 -- the seat the merger drops has an empty recited.
    a = _assembled(hafs, pen, alphabet, "2:5:3-2:5:4")
    source = alignment(a, text="source", grouping="cell")
    blocks = {b for b in respelling(a, grouping="cell") if not b.recited}
    assert blocks, "the silenced alif maqsura must give a block with no recited side"
    for block in blocks:
        assert block.source
        chars = "".join(
            a.glyphs[g].char for i in block.source for g in source[i].glyphs
        )
        assert chars == "ى"
