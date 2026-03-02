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
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple


# ----------------------------------------------------------------------
# JSON loading (with caching)
# ----------------------------------------------------------------------

import bisect

# Module-level cache for database to avoid re-parsing JSON on every call
_db_cache: Dict[str, Dict[str, dict]] = {}

# Pre-sorted index cache: maps db_path -> (sorted_tuples, sorted_keys)
_index_cache: Dict[str, Tuple[List[Tuple[int, int, int]], List[str]]] = {}


def load_db(db_path: str | Path) -> Dict[str, dict]:
    """Read the Qurʾān word-by-word database into a dict (cached)."""
    path_str = str(Path(db_path).resolve())
    if path_str not in _db_cache:
        with Path(db_path).expanduser().open(encoding="utf-8") as fh:
            _db_cache[path_str] = json.load(fh)
        # Build sorted index for fast lookups
        _build_index(path_str, _db_cache[path_str])
    return _db_cache[path_str]


def _build_index(path_str: str, db: Dict[str, dict]) -> None:
    """Build a sorted index of keys for binary search lookups."""
    keys = list(db.keys())
    tuples = [_key_to_tuple(k) for k in keys]
    # Sort by tuple and keep keys aligned
    sorted_pairs = sorted(zip(tuples, keys), key=lambda x: x[0])
    sorted_tuples = [p[0] for p in sorted_pairs]
    sorted_keys = [p[1] for p in sorted_pairs]
    _index_cache[path_str] = (sorted_tuples, sorted_keys)


def _get_index(db_path: str | Path) -> Tuple[List[Tuple[int, int, int]], List[str]]:
    """Get the sorted index for a database path."""
    path_str = str(Path(db_path).resolve())
    if path_str not in _index_cache:
        # Ensure db is loaded (which builds the index)
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


def keys_for_reference(ref: str, db: Dict[str, dict], db_path: str | Path = None) -> List[str]:
    """
    Return an **ordered** list of location keys matching *ref*.
    Uses binary search on pre-sorted index for O(log n) performance.
    """
    if "-" not in ref:                               # single spec
        start = end = _parse_endpoint(ref)
    else:                                            # range
        left, right = ref.split("-", 1)  # Split only on first "-"
        start, end = _parse_endpoint(left.strip()), _parse_endpoint(right.strip())

    # Canonicalise: fill missing verse/word with 0 / big number
    def canon(tpl, is_end=False) -> Tuple[int, int, int]:
        s, v, w = tpl
        if v is None:
            return (s, 0 if not is_end else 10_000, 0 if not is_end else 10_000)
        if w is None:
            return (s, v, 0 if not is_end else 10_000)
        return (s, v, w)

    lo = canon(start)
    hi = canon(end, is_end=True)

    # Try to use indexed lookup if we have the index
    # Find the db_path from cache keys (use first cached path that matches this db)
    index_path = None
    for cached_path, cached_db in _db_cache.items():
        if cached_db is db:
            index_path = cached_path
            break
    
    if index_path and index_path in _index_cache:
        # Use binary search for O(log n) lookup
        sorted_tuples, sorted_keys = _index_cache[index_path]
        
        # Find start index using bisect_left
        start_idx = bisect.bisect_left(sorted_tuples, lo)
        # Find end index using bisect_right with hi+epsilon (to include hi)
        end_idx = bisect.bisect_right(sorted_tuples, hi)
        
        # Return the slice of keys
        return sorted_keys[start_idx:end_idx]
    else:
        # Fallback to O(n) scan if no index available
        selected = [
            k for k in db.keys()
            if lo <= _key_to_tuple(k) <= hi
        ]
        return sorted(selected, key=_key_to_tuple)
