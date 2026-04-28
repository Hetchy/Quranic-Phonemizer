"""
core/loader.py
==============
Load the word-by-word JSON and resolve a *reference string* into an
ordered list of location keys  (``"s:v:w"``).

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
Three on-disk formats are supported (controlled by the ``QURAN_DB_FORMAT``
environment variable, default ``"json"`` for backwards compatibility):

  - ``json``  : original ``Quran.json`` with 6 fields per word (legacy).
  - ``flat``  : ``quran_db_flat.json`` containing ``[keys, texts]`` parallel
                arrays. Same Python dict API but ~57% less RAM.
  - ``blob``  : ``quran_db_blob.bin`` packed binary; lazy UTF-8 decode on access.
                Smallest RSS (~63% less than ``json``).
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
}


def _resolve_format_and_path(db_path: str | Path) -> Tuple[str, Path]:
    """Resolve which on-disk format to use given the requested path.

    Resolution order:
      1. ``QURAN_DB_FORMAT`` env var (``json``/``flat``/``blob``) — overrides
         everything. If the value is ``flat`` or ``blob`` and the requested
         path points at the legacy ``Quran.json``, swap to the slim sibling.
      2. Filename autodetect (``.bin`` -> blob, ``_flat.json`` -> flat).
      3. If the legacy ``Quran.json`` was requested but a sibling
         ``quran_db_flat.json`` exists, prefer it (transparent upgrade for
         packaged installs).
      4. Fall back to legacy ``json`` loader.
    """
    p = Path(db_path).expanduser()
    fmt = os.environ.get("QURAN_DB_FORMAT", "").lower().strip()
    if fmt in _LOADERS:
        if p.name == "Quran.json":
            if fmt == "flat":
                p = p.with_name("quran_db_flat.json")
            elif fmt == "blob":
                p = p.with_name("quran_db_blob.bin")
        return fmt, p

    if p.suffix == ".bin":
        return "blob", p
    if p.name.endswith("_flat.json"):
        return "flat", p

    if p.name == "Quran.json":
        sibling_flat = p.with_name("quran_db_flat.json")
        if sibling_flat.exists():
            return "flat", sibling_flat

    return "json", p


def load_db(db_path: str | Path):
    """Read the Qurʾān word-by-word database (cached)."""
    fmt, p = _resolve_format_and_path(db_path)
    path_str = str(p.resolve())
    if path_str not in _db_cache:
        _db_cache[path_str] = _LOADERS[fmt](p)
        _build_index(path_str, _db_cache[path_str])
    return _db_cache[path_str]


def _build_index(path_str: str, db) -> None:
    """Build a sorted index of keys for binary search lookups."""
    keys = list(db.keys())
    tuples = [_key_to_tuple(k) for k in keys]
    sorted_pairs = sorted(zip(tuples, keys), key=lambda x: x[0])
    sorted_tuples = [p[0] for p in sorted_pairs]
    sorted_keys = [p[1] for p in sorted_pairs]
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

