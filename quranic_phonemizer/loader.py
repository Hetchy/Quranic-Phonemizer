"""
Loader for the Qurʾān word-by-word database.

The runtime DB is a deduplicated binary blob (``resources/quran_db.bin``).
Word texts repeat heavily across the corpus — only ~20.7k of the 77.4k
words are unique — so the file stores one copy of each unique text and a
``uint16`` index per word slot. Keys are not persisted; they are
reconstructed on demand from ``surah_info.json``.

File layout (little-endian):
    <u32 n_words>                          number of word slots (77_433)
    <u32 n_unique>                         number of unique texts
    <(n_unique + 1) * u32> text_offsets    cumulative byte offsets into text_blob
    <u32 text_blob_len>                    length of the text blob
    <text_blob_len bytes> text_blob        UTF-8 concatenated unique texts
    <n_words * u16> word_indices           per-word slot -> unique-text index

Reference-string parsing follows the existing ``"s"`` / ``"s:v"`` /
``"s:v:w"`` / ``"a-b"`` grammar.
"""

from __future__ import annotations

import array
import bisect
import json
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_RESOURCES = Path(__file__).resolve().parent / "resources"
_DB_PATH = _RESOURCES / "quran_db.bin"
_SURAH_INFO_PATH = _RESOURCES / "surah_info.json"


# ----------------------------------------------------------------------
# Module-level caches (one DB ships with the package, loaded once)
# ----------------------------------------------------------------------

_db: Optional["_DB"] = None
_index: Optional[Tuple[List[Tuple[int, int, int]], List[str]]] = None
_surah_info: Optional[Dict[str, Any]] = None


# ----------------------------------------------------------------------
# Surah-info helpers
# ----------------------------------------------------------------------

def _load_surah_info() -> Dict[str, Any]:
    global _surah_info
    if _surah_info is None:
        with _SURAH_INFO_PATH.open(encoding="utf-8") as fh:
            _surah_info = json.load(fh)
    return _surah_info


def _build_verse_start() -> Tuple[Dict[Tuple[int, int], int], int]:
    """``(s, v) -> base word-index``, plus total word count."""
    info = _load_surah_info()
    verse_start: Dict[Tuple[int, int], int] = {}
    base = 0
    for s in range(1, 115):
        s_data = info.get(str(s))
        if not s_data:
            continue
        for v_idx, v_info in enumerate(s_data["verses"], start=1):
            verse_start[(s, v_idx)] = base
            base += v_info["num_words"]
    return verse_start, base


# ----------------------------------------------------------------------
# DB
# ----------------------------------------------------------------------

class _DB:
    """Eager-decoded deduplicated DB. ``db[location_key]`` returns the
    word's text via ``unique_texts[word_indices[word_idx]]``.
    """

    __slots__ = ("_unique_texts", "_word_indices", "_verse_start")

    def __init__(self, unique_texts: List[str], word_indices: array.array,
                 verse_start: Dict[Tuple[int, int], int]):
        self._unique_texts = unique_texts
        self._word_indices = word_indices
        self._verse_start = verse_start

    def __getitem__(self, key: str) -> str:
        s_str, v_str, w_str = key.split(":", 2)
        idx = self._verse_start[(int(s_str), int(v_str))] + int(w_str) - 1
        return self._unique_texts[self._word_indices[idx]]

    def __contains__(self, key: str) -> bool:
        try:
            s_str, v_str, w_str = key.split(":", 2)
            return (int(s_str), int(v_str)) in self._verse_start
        except (KeyError, ValueError):
            return False


def load_db(db_path: str | Path = _DB_PATH) -> _DB:
    """Open the packed binary DB and decode unique texts. Cached after first call."""
    global _db
    if _db is not None:
        return _db

    with Path(db_path).open("rb") as fh:
        data = fh.read()
    n, m = struct.unpack_from("<II", data, 0)
    pos = 8
    offsets = array.array("I")
    offsets.frombytes(data[pos:pos + (m + 1) * 4])
    pos += (m + 1) * 4
    text_blob_len = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    text_blob = data[pos:pos + text_blob_len]
    pos += text_blob_len
    word_indices = array.array("H")
    word_indices.frombytes(data[pos:pos + 2 * n])

    unique_texts = [
        text_blob[offsets[i]:offsets[i + 1]].decode("utf-8")
        for i in range(m)
    ]
    verse_start, n_total = _build_verse_start()
    if n_total != n:
        raise ValueError(
            f"DB has {n} word slots but surah_info.json implies {n_total}; "
            "regenerate quran_db.bin"
        )

    _db = _DB(unique_texts, word_indices, verse_start)
    return _db


# ----------------------------------------------------------------------
# Reference-range resolution
# ----------------------------------------------------------------------

def _key_to_tuple(key: str) -> Tuple[int, int, int]:
    s, v, *rest = key.split(":")
    w = rest[0] if rest else 0
    return int(s), int(v), int(w)


def _parse_endpoint(spec: str) -> Tuple[int | None, int | None, int | None]:
    parts = [int(p) for p in spec.split(":")]
    if len(parts) == 1:
        return parts[0], None, None
    if len(parts) == 2:
        return parts[0], parts[1], None
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    raise ValueError(f"Bad reference component: {spec}")


def keys_for_reference(ref: str, db: _DB | None = None,
                       db_path: str | Path | None = None) -> List[str]:
    """Return canonical-order ``"s:v:w"`` keys covering ``ref``.

    Walks ``surah_info.json`` and emits keys only for the requested
    range — no upfront 77k-tuple list, no bisect.
    """
    if "-" not in ref:
        start = end = _parse_endpoint(ref)
    else:
        left, right = ref.split("-", 1)
        start, end = _parse_endpoint(left.strip()), _parse_endpoint(right.strip())

    def canon(tpl, is_end: bool = False) -> Tuple[int, int, int]:
        s, v, w = tpl
        if v is None:
            return (s, 0 if not is_end else 10_000, 0 if not is_end else 10_000)
        if w is None:
            return (s, v, 0 if not is_end else 10_000)
        return (s, v, w)

    lo = canon(start)
    hi = canon(end, is_end=True)
    s_lo, v_lo, w_lo = lo
    s_hi, v_hi, w_hi = hi

    info = _load_surah_info()
    keys: List[str] = []
    append = keys.append
    for s in range(max(s_lo, 1), min(s_hi, 114) + 1):
        s_data = info.get(str(s))
        if not s_data:
            continue
        verses = s_data["verses"]
        n_verses = len(verses)
        v_start = max(v_lo if s == s_lo else 1, 1)
        v_end = min(v_hi if s == s_hi else n_verses, n_verses)
        s_str = str(s)
        for v_idx in range(v_start, v_end + 1):
            nw = verses[v_idx - 1]["num_words"]
            prefix = s_str + ":" + str(v_idx) + ":"
            w_start = max(w_lo if (s == s_lo and v_idx == v_lo) else 1, 1)
            w_end = min(w_hi if (s == s_hi and v_idx == v_hi) else nw, nw)
            for w in range(w_start, w_end + 1):
                append(prefix + str(w))
    return keys
