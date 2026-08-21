"""The mini seen of a seen/saad khilaf: whether the script writes it, how the
riwayah's default and the variant decide the sound, and -- now decided -- that
where the script writes it the native builder makes it its own paired unit."""
from __future__ import annotations

from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import LetterUnitKind
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah
from quranic_phonemizer.session import phonemize_request
from tests.support import KhilafId, Option, Script, Site, VariantSelection, reading

SEEN_ABOVE = "ۜ"
SEEN_BELOW = "ۣ"
SEEN_MARKS = (SEEN_ABOVE, SEEN_BELOW)

YABSUT = Site(hafs=("2:245", (14,)))        # written, default plain
MUSAYTIRUN = Site(hafs=("52:37", (7,)))     # written, default emphatic
BIMUSAYTIR = Site(hafs=("88:22", (3,)))     # Uthmani writes no mark


def _selection(khilaf, option):
    return VariantSelection((Option(khilaf, option),))


def _marks(site, script, word):
    a = reading(site, script=script, isolated=word)._assembled
    return [g.char for g in a.glyphs if g.word == word - 1 and g.char in SEEN_MARKS]


def test_whether_the_mark_is_written_is_a_script_fact():
    assert _marks(YABSUT, Script.UTHMANI, 14)
    assert not _marks(BIMUSAYTIR, Script.UTHMANI, 3)
    assert _marks(BIMUSAYTIR, Script.INDOPAK, 3)


def test_selecting_the_variant_flips_the_sound_at_a_written_site():
    # وَيَبْصُطُ, default plain, saad emphatic
    default = reading(YABSUT, isolated=14)
    saad = reading(
        YABSUT, selection=_selection(KhilafId.SEEN_SAD_YABSUT, "saad"),
        isolated=14,
    )
    assert "sˤ" not in default.phonemes(14)
    assert "sˤ" in saad.phonemes(14)


def test_at_the_unwritten_site_one_unit_carries_the_variant_sound():
    """Uthmani writes no mark, so there is no second scalar; the variant still
    changes the single word's sound, and IndoPak reads the same default."""
    assert not _marks(BIMUSAYTIR, Script.UTHMANI, 3)
    default = reading(BIMUSAYTIR, isolated=3)
    seen = reading(
        BIMUSAYTIR, selection=_selection(KhilafId.SEEN_SAD_BIMUSAYTIR, "seen"),
        isolated=3,
    )
    assert "sˤ" in default.phonemes(3)
    assert "sˤ" not in seen.phonemes(3)
    indopak = reading(BIMUSAYTIR, script=Script.INDOPAK, isolated=3)
    assert indopak.phonemes(3) == default.phonemes(3)


def test_a_written_mini_seen_tokenizes_as_its_own_paired_unit():
    """The decided fold: at a written site the seen is its own letter unit,
    riding the base it pairs with, and the pair is two units."""
    ref = "2:245:14"
    session = phonemize_request(recitation(Riwayah("hafs")), ref)
    view = build_source_view(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    seen = next(u for u in view.units if u.text in SEEN_MARKS)
    assert seen.kind is LetterUnitKind.LETTER
    assert seen.written_on_unit_id is not None
    assert seen.written_on_unit_id != seen.id


def test_the_position_states_nothing_about_the_default():
    """The mark rides below in Uthmani and above in IndoPak at the same site,
    yet the emphatic default is the riwayah's and is one in both scripts."""
    assert _marks(MUSAYTIRUN, Script.UTHMANI, 7) == [SEEN_BELOW]
    assert _marks(MUSAYTIRUN, Script.INDOPAK, 7) == [SEEN_ABOVE]
    uthmani = reading(MUSAYTIRUN, script=Script.UTHMANI, isolated=7)
    indopak = reading(MUSAYTIRUN, script=Script.INDOPAK, isolated=7)
    assert "sˤ" in uthmani.phonemes(7)
    assert uthmani.phonemes(7) == indopak.phonemes(7)
