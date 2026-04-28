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
from typing import Any, Dict, List, Optional, Tuple

import bisect


# ----------------------------------------------------------------------
# DB caches (keyed by resolved path string)
# ----------------------------------------------------------------------

_db_cache: Dict[str, "_DBLike"] = {}
_index_cache: Dict[str, Tuple[List[Tuple[int, int, int]], List[str]]] = {}

# Path to surah_info, used by the texts-only loader to reconstruct keys.
_SURAH_INFO_PATH = Path(__file__).resolve().parent / "resources" / "surah_info.json"

# Cached parsed surah_info. Loaded lazily on first need; ~288 KB. Reused
# both by the loader (to build verse_start) and by keys_for_reference()
# to walk the canonical key sequence without materialising a 5 MB
# sorted_tuples list.
_surah_info_cache: Optional[Dict[str, Any]] = None


def _load_surah_info() -> Dict[str, Any]:
    global _surah_info_cache
    if _surah_info_cache is None:
        with _SURAH_INFO_PATH.open(encoding="utf-8") as fh:
            _surah_info_cache = json.load(fh)
    return _surah_info_cache


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
        for v_idx, v_info in enumerate(s_data["verses"], start=1):
            prefix = s_str + ":" + str(v_idx) + ":"
            for w in range(1, v_info["num_words"] + 1):
                a_keys(prefix + str(w))
                a_tuples((s, v_idx, w))
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


class _MmapLazyDB:
    """Pay-as-you-go DB:
      - texts are kept on disk via mmap; only pages actually touched stay
        resident. UTF-8 is decoded per lookup.
      - the canonical (s, v, w) tuples are pre-built (~600 KB) so the
        bisect index works without re-sorting, but the per-word *string*
        keys are never materialised — db[key] parses the key directly.

    Idle RSS for this DB layer is ~10 MB total. Trade-off vs the eager
    dict format: per-lookup is ~2 µs slower (mmap slice + UTF-8 decode).
    Verse call (50 lookups) ~ +100 µs. Full Quran (77k lookups) ~ +50–150 ms.
    """

    __slots__ = ("_mm", "_file", "_offsets", "_text_blob_start",
                 "_verse_start", "_sorted_tuples")

    def __init__(self, mm, file_obj, offsets, text_blob_start,
                 verse_start, sorted_tuples):
        self._mm = mm
        self._file = file_obj
        self._offsets = offsets
        self._text_blob_start = text_blob_start
        self._verse_start = verse_start
        self._sorted_tuples = sorted_tuples

    def _idx(self, key: str) -> int:
        s_str, v_str, w_str = key.split(":", 2)
        return self._verse_start[(int(s_str), int(v_str))] + int(w_str) - 1

    def __getitem__(self, key: str) -> str:
        i = self._idx(key)
        b = self._text_blob_start
        o = self._offsets
        return self._mm[b + o[i]:b + o[i + 1]].decode("utf-8")

    def __contains__(self, key: str) -> bool:
        try:
            self._idx(key)
            return True
        except (KeyError, ValueError):
            return False

    def keys(self):
        # Generate canonical keys on-demand. Used by code paths that call
        # ``db.keys()`` directly (rare); the hot path uses
        # ``keys_for_reference`` which bypasses this and builds keys for
        # only the requested range.
        for s, v, w in self._sorted_tuples:
            yield f"{s}:{v}:{w}"

    def items(self):
        b = self._text_blob_start
        o = self._offsets
        mm = self._mm
        for i, (s, v, w) in enumerate(self._sorted_tuples):
            yield f"{s}:{v}:{w}", mm[b + o[i]:b + o[i + 1]].decode("utf-8")

    def sorted_tuples(self):
        return self._sorted_tuples


class _DedupMmapDB:
    """Like _MmapLazyDB but the underlying binary stores deduplicated word
    texts. Uses ~3x less disk and ~5 MB less idle RSS by exploiting the
    fact that only 20,696 of 77,433 word texts are unique.

    File layout (see build_quran_db.py):
      <u32 n_words> <u32 n_unique>
      <(n_unique+1) * u32 offsets>
      <u32 text_blob_len> <text_blob_bytes>
      <n_words * u16 word_idx>     -- word_idx[w] -> index into offsets/text_blob

    No 77k canonical (s, v, w) tuple list is kept in memory; iteration
    walks surah_info on demand. Idle RSS is ~5 MB lower as a result.
    """

    __slots__ = ("_mm", "_file", "_offsets", "_text_blob_start",
                 "_word_indices", "_verse_start")

    def __init__(self, mm, file_obj, offsets, text_blob_start,
                 word_indices, verse_start):
        self._mm = mm
        self._file = file_obj
        self._offsets = offsets
        self._text_blob_start = text_blob_start
        self._word_indices = word_indices
        self._verse_start = verse_start

    def _word_idx(self, key: str) -> int:
        s_str, v_str, w_str = key.split(":", 2)
        return self._verse_start[(int(s_str), int(v_str))] + int(w_str) - 1

    def __getitem__(self, key: str) -> str:
        word_idx = self._word_idx(key)
        u_idx = self._word_indices[word_idx]
        b = self._text_blob_start
        o = self._offsets
        return self._mm[b + o[u_idx]:b + o[u_idx + 1]].decode("utf-8")

    def __contains__(self, key: str) -> bool:
        try:
            self._word_idx(key)
            return True
        except (KeyError, ValueError):
            return False

    def keys(self):
        info = _load_surah_info()
        for s in range(1, 115):
            s_data = info.get(str(s))
            if not s_data:
                continue
            s_str = str(s)
            for v_idx, v_info in enumerate(s_data["verses"], start=1):
                prefix = s_str + ":" + str(v_idx) + ":"
                for w in range(1, v_info["num_words"] + 1):
                    yield prefix + str(w)

    def items(self):
        for k in self.keys():
            yield k, self[k]


class _DedupEagerDB:
    """Deduplicated DB with eager UTF-8 decode of unique texts.

    77k word slots all point into a list of ~20.7k Python str objects
    via uint16 indices. Best of both worlds: small disk file *and*
    sub-microsecond lookups, at the cost of decoding all unique texts
    up-front.
    """

    __slots__ = ("_unique_texts", "_word_indices", "_verse_start",
                 "_sorted_tuples")

    def __init__(self, unique_texts, word_indices, verse_start, sorted_tuples):
        self._unique_texts = unique_texts
        self._word_indices = word_indices
        self._verse_start = verse_start
        self._sorted_tuples = sorted_tuples

    def _word_idx(self, key: str) -> int:
        s_str, v_str, w_str = key.split(":", 2)
        return self._verse_start[(int(s_str), int(v_str))] + int(w_str) - 1

    def __getitem__(self, key: str) -> str:
        return self._unique_texts[self._word_indices[self._word_idx(key)]]

    def __contains__(self, key: str) -> bool:
        try:
            self._word_idx(key)
            return True
        except (KeyError, ValueError):
            return False

    def keys(self):
        for s, v, w in self._sorted_tuples:
            yield f"{s}:{v}:{w}"

    def items(self):
        for k in self.keys():
            yield k, self[k]


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


def _read_dedup_blob_header(mm_or_bytes, n_total_expected=None):
    """Parse the dedup-blob header. Returns (n, n_unique, offsets,
    text_blob_start, word_indices) where text_blob_start is a byte offset
    into mm_or_bytes pointing at the start of the deduplicated text blob.
    """
    n, m = struct.unpack_from("<II", mm_or_bytes, 0)
    pos = 8
    offsets_size = (m + 1) * 4
    offsets = array.array("I")
    offsets.frombytes(bytes(mm_or_bytes[pos:pos + offsets_size]))
    pos += offsets_size
    text_blob_len = struct.unpack_from("<I", mm_or_bytes, pos)[0]
    pos += 4
    text_blob_start = pos
    pos += text_blob_len
    word_indices = array.array("H")
    word_indices.frombytes(bytes(mm_or_bytes[pos:pos + 2 * n]))
    return n, m, offsets, text_blob_start, word_indices


def _load_dedup_eager(path: Path) -> Tuple[_DedupEagerDB, List[Tuple[int, int, int]]]:
    """Read the dedup blob and eagerly decode the ~20.7k unique strings.

    Memory model:
      - one Python str per UNIQUE text (~20.7k objects)
      - uint16 array of per-word indices (~155 KB)
      - small (s, v) -> base_idx dict for key parsing

    Returns (db, sorted_tuples) — caller stashes both into the caches.
    """
    with path.open("rb") as fh:
        data = fh.read()
    n, m, offsets, tstart, word_indices = _read_dedup_blob_header(data)
    # Eagerly decode the unique texts so all subsequent lookups are pure
    # dict-style pointer fetches.
    unique_texts = [data[tstart + offsets[i]:tstart + offsets[i + 1]].decode("utf-8")
                    for i in range(m)]

    verse_start, sorted_tuples = _build_verse_index_and_tuples()
    if len(sorted_tuples) != n:
        raise ValueError(
            f"dedup blob has {n} word slots but surah_info implies "
            f"{len(sorted_tuples)}; rebuild quran_db_dedup.bin"
        )
    return _DedupEagerDB(unique_texts, word_indices, verse_start, sorted_tuples), sorted_tuples


def _load_dedup_mmap(path: Path) -> _DedupMmapDB:
    """Read the dedup blob via mmap. Decodes are deferred to lookup time;
    only OS pages actually touched stay resident.

    Memory model at idle:
      - mmap of the blob:       ~few KB of bookkeeping until first access
      - offsets array:          ~85 KB
      - word_indices array:     ~160 KB
      - verse_start dict:       ~290 KB (already needed for key parsing)
      - surah_info parsed dict: ~290 KB (cached at module level)

    No 77k canonical-tuples list is built. keys_for_reference() walks
    surah_info on demand for the requested range only.
    """
    fh = path.open("rb")
    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
    n, m, offsets, tstart, word_indices = _read_dedup_blob_header(mm)
    verse_start, n_total = _build_verse_start()
    if n_total != n:
        raise ValueError(
            f"dedup blob has {n} word slots but surah_info implies "
            f"{n_total}; rebuild quran_db_dedup.bin"
        )
    return _DedupMmapDB(mm, fh, offsets, tstart, word_indices, verse_start)


def _build_verse_start():
    """Build (s, v) -> base_idx and total word count from surah_info.json.

    Returns ``(verse_start, n_words)``. The 77k canonical (s, v, w) tuples
    are NOT materialised here — keys_for_reference() walks the surah_info
    structure directly for the requested range, paying only for what's
    actually needed (a verse-call materialises ~50 keys; a full-Quran call
    materialises 77k strings, but only at call time, not at idle).
    """
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


def _load_mmap_lazy(path: Path) -> Tuple[_MmapLazyDB, List[Tuple[int, int, int]]]:
    """Pay-as-you-go: mmap the binary file. Eager structures are kept
    minimal — just the offsets array and a (s, v) -> base_idx dict.
    Texts and keys are not materialised at load.

    Returns ``(db, sorted_tuples)`` so the caller can populate the bisect
    index without recomputing.
    """
    fh = path.open("rb")
    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
    n = struct.unpack_from("<I", mm, 0)[0]
    offsets_size = (n + 1) * 4
    offsets = array.array("I")
    offsets.frombytes(bytes(mm[4:4 + offsets_size]))
    pos = 4 + offsets_size
    text_blob_len = struct.unpack_from("<I", mm, pos)[0]; pos += 4
    text_blob_start = pos
    # Skip the keys section entirely; reconstruct from surah_info instead.

    verse_start, sorted_tuples = _build_verse_index_and_tuples()
    base = len(sorted_tuples)
    if base != n:
        # surah_info disagrees with the binary file — refuse to load
        # rather than silently mis-mapping indices.
        raise ValueError(
            f"binary blob has {n} entries but surah_info implies {base}; "
            f"rebuild quran_db_blob.bin"
        )

    return _MmapLazyDB(mm, fh, offsets, text_blob_start, verse_start, sorted_tuples), sorted_tuples


_LOADERS = {
    "json": _load_json_full,
    "flat": _load_json_flat,
    "blob": _load_binary_blob,
    "texts": _load_texts_only,
    "mmap": _load_mmap_lazy,
    "dedup": _load_dedup_eager,
    "dedup_mmap": _load_dedup_mmap,
}

# Formats that ship their keys in canonical sort order. Their loaders
# guarantee db.keys() is already sorted, so _build_index can skip the
# explicit sort step.
_PRE_SORTED_FORMATS = {"flat", "blob", "texts", "mmap", "dedup", "dedup_mmap"}


_SIBLING_FILENAMES = {
    "texts":      "quran_db_texts.json",
    "flat":       "quran_db_flat.json",
    "blob":       "quran_db_blob.bin",
    "mmap":       "quran_db_blob.bin",   # same file, different load strategy
    "dedup":      "quran_db_dedup.bin",
    "dedup_mmap": "quran_db_dedup.bin",  # same file, mmap'd
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

    if p.name.endswith("_dedup.bin"):
        return "dedup", p
    if p.suffix == ".bin":
        return "blob", p
    if p.name.endswith("_texts.json"):
        return "texts", p
    if p.name.endswith("_flat.json"):
        return "flat", p

    if p.name == "Quran.json":
        # Prefer the format that is both smallest *and* fastest at lookup
        # time. dedup-eager wins on memory + speed; texts wins on full-Quran
        # cold starts but uses more RAM.
        for f in ("dedup", "texts", "flat", "blob"):
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
    elif fmt == "dedup_mmap":
        # Pure pay-as-you-go: no sorted_tuples either. keys_for_reference()
        # walks surah_info for the requested range.
        db = _LOADERS[fmt](p)
        _index_cache[path_str] = (None, None)
    elif fmt in ("mmap", "dedup"):
        # Defer key materialisation but keep sorted_tuples for bisect.
        db, sorted_tuples = _LOADERS[fmt](p)
        _index_cache[path_str] = (sorted_tuples, None)
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
        if sorted_tuples is None and sorted_keys is None:
            # Pure lazy mode: walk surah_info to emit keys for the
            # requested range only. Idle RSS doesn't carry a 5 MB
            # tuples list; per-call cost scales with the range.
            return _generate_keys_for_range(lo, hi)
        start_idx = bisect.bisect_left(sorted_tuples, lo)
        end_idx = bisect.bisect_right(sorted_tuples, hi)
        if sorted_keys is None:
            # Tuples kept, keys lazy: generate only the range slice.
            return [f"{s}:{v}:{w}" for s, v, w in sorted_tuples[start_idx:end_idx]]
        return sorted_keys[start_idx:end_idx]
    else:
        selected = [k for k in db.keys() if lo <= _key_to_tuple(k) <= hi]
        return sorted(selected, key=_key_to_tuple)


def _generate_keys_for_range(lo, hi) -> List[str]:
    """Walk surah_info to yield canonical-order keys in [lo, hi] inclusive."""
    info = _load_surah_info()
    s_lo, v_lo, w_lo = lo
    s_hi, v_hi, w_hi = hi
    keys: List[str] = []
    a = keys.append
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
            v_info = verses[v_idx - 1]
            nw = v_info["num_words"]
            prefix = s_str + ":" + str(v_idx) + ":"
            w_start = max(w_lo if (s == s_lo and v_idx == v_lo) else 1, 1)
            w_end = min(w_hi if (s == s_hi and v_idx == v_hi) else nw, nw)
            for w in range(w_start, w_end + 1):
                a(prefix + str(w))
    return keys

