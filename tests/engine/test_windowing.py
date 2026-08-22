"""Request window assembly and multi-verse phonemization."""
from __future__ import annotations

from quranic_phonemizer.model.address import Junction, Location
from quranic_phonemizer.phonemize import span
from quranic_phonemizer.phonemize.session import phonemize_request
from quranic_phonemizer.phonemize.span import windows
from quranic_phonemizer.phonemize.legacy_views import phonemes_by_word


def test_windows_own_machinery_is_not_public():
    """`Window` and `OVERLAP_WORDS` are `windows()`'s implementation, not a
    consumer's; no caller needs anything but what `windows()` yields."""
    assert "Window" not in span.__all__
    assert "OVERLAP_WORDS" not in span.__all__


def test_a_multi_verse_range_is_one_index_space(hafs, alphabet):
    # 2:7 عَظِيمٌ | 2:8 وَمِنَ -- a tanween at a verse end merging into the next
    # verse's noon, covered by the semantic nasal suite.
    session = phonemize_request(hafs, "2:7-2:8")
    assert session.locations[0] == Location(2, 7, 1)
    assert session.locations[-1] == Location(2, 8, 11)
    assert len(session.locations) == 12 + 11
    words = phonemes_by_word(session.performance, session.score, alphabet)
    assert "".join(words[11]) == "ʕaðˤi:mu"
    assert session.boundaries.after(11) is Junction.JOIN
    assert session.boundaries.after(len(session.locations) - 1) is Junction.EDGE


def test_a_sub_verse_start_takes_no_backward_context(hafs):
    # 2:7 has no ledger-addressed word, so words 3-12 are a clean sub-range.
    session = phonemize_request(hafs, "2:7:3-2:7:12")
    assert session.locations[0] == Location(2, 7, 3)
    assert session.boundaries.started_on(0)
    assert session.boundaries.before(0) is None


def test_stop_refs_stops_after_the_named_word(hafs):
    session = phonemize_request(hafs, "2:7-2:8", stop_refs=("2:7:12",))
    index = session.locations.index(Location(2, 7, 12))
    assert session.boundaries.after(index) is Junction.STOP
    assert session.boundaries.stopped_on(index)


def test_stop_signs_stops_at_every_word_carrying_one(hafs):
    # 2:7 word 6 carries `preferred_continue` advice.
    session = phonemize_request(hafs, "2:7", stop_signs=("preferred_continue",))
    assert session.boundaries.after(5) is Junction.STOP


def test_no_stop_request_leaves_the_advice_word_joined(hafs):
    session = phonemize_request(hafs, "2:7")
    assert session.boundaries.after(5) is Junction.JOIN


def test_sakt_is_a_junction_no_stop_request_can_remove(hafs):
    # 83:14 بَلْ ۜ -- word 2 carries a sakt the reader may not join through.
    session = phonemize_request(hafs, "83:14")
    index = session.locations.index(Location(83, 14, 2))
    assert session.boundaries.after(index) is Junction.SAKT


def test_chunked_assembly_matches_one_shot_assembly(hafs, alphabet):
    session = phonemize_request(hafs, "2:7-2:8")
    whole = phonemes_by_word(session.performance, session.score, alphabet)

    pieces: list[tuple[str, ...]] = []
    for window in windows(hafs, session.locations, chunk_words=3):
        by_word = phonemes_by_word(window.performance, window.score, alphabet)
        kept = by_word[window.offset : window.offset + len(window.kept)]
        pieces.extend(kept)

    assert pieces == list(whole)
