"""
core/loader.py
==============
Load the word-by-word DB and resolve a *reference string* into an ordered
list of location keys (``"s:v:w"``).

Accepted reference formats
--------------------------
    • ``"32"``                   → whole surah 32
    • ``"32:5"``                 → verse 5 of surah 32
    • ``"32:5-32:8"``            → verse range, inclusive, valid across surahs
    • ``"32:5:3-32:5:7"``        → word range, inclusive, valid across verses/surahs
All numbers are 1-based, no zero-padding required.

Storage formats
---------------
The runtime DB exposes a dict-like ``db[location_key] -> word_text`` interface.
Four on-disk formats are supported (controlled by ``QURAN_DB_FORMAT`` env
var, with autodetect that prefers smaller/faster siblings when present):

  - ``texts`` : ``quran_db_texts.json`` — just ``[text, text, ...]`` in
                canonical order. Keys reconstructed from ``surah_info.json``
                at load time. Smallest disk + fastest load.  *Default if
                the file is shipped.*
  - ``flat``  : ``quran_db_flat.json`` — ``[keys, texts]`` parallel arrays.
  - ``blob``  : ``quran_db_blob.bin`` — packed binary, lazy UTF-8 decode.
  - ``json``  : original ``Quran.json`` with 6 fields per word (legacy).

All slim formats are stored in canonical sort order, so the bisect index
is built without an extra sort step.
"""

from __future__ import annotations

import array
import json
import mmap
import os
import struct
from pathlib import Path
from typing import Dict, List, Tuple

import bisect


# ----------------------------------------------------------------------
# DB caches (keyed by resolved path string)
# ----------------------------------------------------------------------

_db_cache: Dict[str, "_DBLike"] = {}
_index_cache: Dict[str, Tuple[List[Tuple[int, int, int]], List[str]]] = {}

# Path to surah_info, used by the texts-only loader to reconstruct keys.
_SURAH_INFO_PATH = Path(__file__).resolve().parent / "resources" / "surah_info.json"


def _build_canonical_keys_and_tuples() -> Tuple[List[str], List[Tuple[int, int, int]]]:
    """Reconstruct canonical key strings + (s, v, w) tuples from surah_info.

    Not cached globally — the lists are short-lived: they're consumed by
    the loader to populate ``_db_cache`` and ``_index_cache`` and then go
    out of scope. Re-running this function on a second load is cheap
    (~10ms for 77k entries).
    """
    with _SURAH_INFO_PATH.open(encoding="utf-8") as fh:
        info = json.load(fh)
    keys: List[str] = []
    tuples: List[Tuple[int, int, int]] = []
    a_keys = keys.append
    a_tuples = tuples.append
    for s in range(1, 115):
        s_str = str(s)
        s_data = info.get(s_str)
        if not s_data:
            continue
        for v_info in s_data["verses"]:
            v = v_info["verse"]
            prefix = s_str + ":" + str(v) + ":"
            for w in range(1, v_info["num_words"] + 1):
                a_keys(prefix + str(w))
                a_tuples((s, v, w))
    return keys, tuples


# ----------------------------------------------------------------------
# DB-like wrappers — common interface: db[loc] -> str (the word text)
# ----------------------------------------------------------------------

class _DictDB:
    """Dict-backed DB. Built from json_full, json_slim, or json_flat."""

    __slots__ = ("_d",)

    def __init__(self, d: Dict[str, str]):
        self._d = d

    def __getitem__(self, key: str) -> str:
        return self._d[key]

    def __contains__(self, key: str) -> bool:
        return key in self._d

    def keys(self):
        return self._d.keys()

    def items(self):
        return self._d.items()


class _BlobDB:
    """Binary-blob DB with lazy UTF-8 decode per lookup. Lowest RSS."""

    __slots__ = ("_blob", "_offsets", "_key_to_idx", "_keys")

    def __init__(self, blob: bytes, offsets: array.array, keys: List[str]):
        self._blob = blob
        self._offsets = offsets
        self._keys = keys
        self._key_to_idx = {k: i for i, k in enumerate(keys)}

    def __getitem__(self, key: str) -> str:
        i = self._key_to_idx[key]
        return self._blob[self._offsets[i]:self._offsets[i + 1]].decode("utf-8")

    def __contains__(self, key: str) -> bool:
        return key in self._key_to_idx

    def keys(self):
        return self._keys

    def items(self):
        b, o = self._blob, self._offsets
        for i, k in enumerate(self._keys):
            yield k, b[o[i]:o[i + 1]].decode("utf-8")


# ----------------------------------------------------------------------
# Format-specific load functions
# ----------------------------------------------------------------------

def _load_json_full(path: Path) -> _DictDB:
    """Legacy format: {key: {6 fields}}. Strip down to {key: text}."""
    with path.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    sample = next(iter(raw.values()), None)
    if isinstance(sample, dict) and "text" in sample:
        return _DictDB({k: v["text"] for k, v in raw.items()})
    return _DictDB(raw)


def _load_json_flat(path: Path) -> _DictDB:
    """Parallel arrays format: [keys, texts]."""
    with path.open(encoding="utf-8") as fh:
        keys, texts = json.load(fh)
    return _DictDB(dict(zip(keys, texts)))


def _load_texts_only(path: Path) -> Tuple[_DictDB, List[str], List[Tuple[int, int, int]]]:
    """Just [text, text, ...] in canonical order; keys reconstructed from
    surah_info.json. Smallest on-disk size; loads fastest because the
    canonical ordering lets us skip the sort that builds the bisect index.

    Returns ``(db, keys, tuples)`` so the caller can populate the bisect
    index without recomputing.
    """
    with path.open(encoding="utf-8") as fh:
        texts = json.load(fh)
    keys, tuples = _build_canonical_keys_and_tuples()
    if len(keys) != len(texts):
        raise ValueError(
            f"texts file has {len(texts)} entries but surah_info implies "
            f"{len(keys)}; rebuild quran_db_texts.json"
        )
    return _DictDB(dict(zip(keys, texts))), keys, tuples


def _load_binary_blob(path: Path) -> _BlobDB:
    """Packed binary format. See build_db_formats.py for layout."""
    with path.open("rb") as fh:
        data = fh.read()
    n = struct.unpack_from("<I", data, 0)[0]
    offsets_size = (n + 1) * 4
    offsets = array.array("I")
    offsets.frombytes(data[4:4 + offsets_size])
    pos = 4 + offsets_size
    text_blob_len = struct.unpack_from("<I", data, pos)[0]; pos += 4
    text_blob = data[pos:pos + text_blob_len]
    pos += text_blob_len
    keys_len = struct.unpack_from("<I", data, pos)[0]; pos += 4
    keys = data[pos:pos + keys_len].decode("ascii").rstrip("\n").split("\n")
    return _BlobDB(text_blob, offsets, keys)


_LOADERS = {
    "json": _load_json_full,
    "flat": _load_json_flat,
    "blob": _load_binary_blob,
    "texts": _load_texts_only,
}

# Formats that ship their keys in canonical sort order. Their loaders
# guarantee db.keys() is already sorted, so _build_index can skip the
# explicit sort step.
_PRE_SORTED_FORMATS = {"flat", "blob", "texts"}


_SIBLING_FILENAMES = {
    "texts": "quran_db_texts.json",
    "flat":  "quran_db_flat.json",
    "blob":  "quran_db_blob.bin",
}


def _resolve_format_and_path(db_path: str | Path) -> Tuple[str, Path]:
    """Resolve which on-disk format to use given the requested path.

    Resolution order:
      1. ``QURAN_DB_FORMAT`` env var (``texts``/``flat``/``blob``/``json``)
         overrides everything. If the requested path is the legacy
         ``Quran.json``, swap to the named slim sibling.
      2. Filename autodetect (``.bin`` -> blob, ``_texts.json`` -> texts,
         ``_flat.json`` -> flat).
      3. If the legacy ``Quran.json`` was requested, prefer the smallest
         sibling that exists (texts > flat > blob > json).
      4. Fall back to legacy ``json`` loader.
    """
    p = Path(db_path).expanduser()
    fmt = os.environ.get("QURAN_DB_FORMAT", "").lower().strip()
    if fmt in _LOADERS:
        if p.name == "Quran.json" and fmt in _SIBLING_FILENAMES:
            p = p.with_name(_SIBLING_FILENAMES[fmt])
        return fmt, p

    if p.suffix == ".bin":
        return "blob", p
    if p.name.endswith("_texts.json"):
        return "texts", p
    if p.name.endswith("_flat.json"):
        return "flat", p

    if p.name == "Quran.json":
        for f in ("texts", "flat", "blob"):
            sibling = p.with_name(_SIBLING_FILENAMES[f])
            if sibling.exists():
                return f, sibling

    return "json", p


def load_db(db_path: str | Path):
    """Read the Qurʾān word-by-word database (cached)."""
    fmt, p = _resolve_format_and_path(db_path)
    path_str = str(p.resolve())
    if path_str in _db_cache:
        return _db_cache[path_str]

    if fmt == "texts":
        # Loader returns (db, sorted_keys, sorted_tuples) — populate index directly.
        db, sorted_keys, sorted_tuples = _LOADERS[fmt](p)
        _index_cache[path_str] = (sorted_tuples, sorted_keys)
    else:
        db = _LOADERS[fmt](p)
        _build_index(path_str, db, pre_sorted=fmt in _PRE_SORTED_FORMATS)
    _db_cache[path_str] = db
    return db


def _build_index(path_str: str, db, *, pre_sorted: bool = False) -> None:
    """Build a sorted index of keys for binary search lookups.

    If ``pre_sorted`` is True (the file format guarantees canonical order),
    skip the sort step and just compute (s, v, w) tuples from the keys.
    """
    if pre_sorted:
        keys_view = db.keys()
        sorted_keys = list(keys_view) if not isinstance(keys_view, list) else keys_view
        sorted_tuples = [_key_to_tuple(k) for k in sorted_keys]
    else:
        keys = list(db.keys())
        tuples = [_key_to_tuple(k) for k in keys]
        sorted_pairs = sorted(zip(tuples, keys), key=lambda x: x[0])
        sorted_tuples = [pair[0] for pair in sorted_pairs]
        sorted_keys = [pair[1] for pair in sorted_pairs]
    _index_cache[path_str] = (sorted_tuples, sorted_keys)


def _get_index(db_path: str | Path) -> Tuple[List[Tuple[int, int, int]], List[str]]:
    """Get the sorted index for a database path."""
    fmt, p = _resolve_format_and_path(db_path)
    path_str = str(p.resolve())
    if path_str not in _index_cache:
        load_db(db_path)
    return _index_cache[path_str]


# ----------------------------------------------------------------------
# Reference parsing helpers
# ----------------------------------------------------------------------

def _key_to_tuple(key: str) -> Tuple[int, int, int]:
    """'s:v:w' → (s, v, w) with *w* defaulting to 0 for comparisons."""
    s, v, *rest = key.split(":")
    w = rest[0] if rest else 0
    return int(s), int(v), int(w)


def _parse_endpoint(spec: str) -> Tuple[int | None, int | None, int | None]:
    """
    Turn 'n', 'n:n', or 'n:n:n' into a tuple (s, v, w_or_None).
    """
    parts = [int(p) for p in spec.split(":")]
    if len(parts) == 1:        # surah
        return parts[0], None, None
    if len(parts) == 2:        # verse
        return parts[0], parts[1], None
    if len(parts) == 3:        # word
        return parts[0], parts[1], parts[2]
    raise ValueError(f"Bad reference component: {spec}")


def keys_for_reference(ref: str, db, db_path: str | Path = None) -> List[str]:
    """
    Return an **ordered** list of location keys matching *ref*.
    Uses binary search on pre-sorted index for O(log n) performance.
    """
    if "-" not in ref:                               # single spec
        start = end = _parse_endpoint(ref)
    else:                                            # range
        left, right = ref.split("-", 1)
        start, end = _parse_endpoint(left.strip()), _parse_endpoint(right.strip())

    def canon(tpl, is_end=False) -> Tuple[int, int, int]:
        s, v, w = tpl
        if v is None:
            return (s, 0 if not is_end else 10_000, 0 if not is_end else 10_000)
        if w is None:
            return (s, v, 0 if not is_end else 10_000)
        return (s, v, w)

    lo = canon(start)
    hi = canon(end, is_end=True)

    index_path = None
    for cached_path, cached_db in _db_cache.items():
        if cached_db is db:
            index_path = cached_path
            break

    if index_path and index_path in _index_cache:
        sorted_tuples, sorted_keys = _index_cache[index_path]
        start_idx = bisect.bisect_left(sorted_tuples, lo)
        end_idx = bisect.bisect_right(sorted_tuples, hi)
        return sorted_keys[start_idx:end_idx]
    else:
        selected = [k for k in db.keys() if lo <= _key_to_tuple(k) <= hi]
        return sorted(selected, key=_key_to_tuple)

