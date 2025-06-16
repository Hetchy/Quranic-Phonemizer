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
# JSON loading
# ----------------------------------------------------------------------

def load_db(db_path: str | Path) -> Dict[str, dict]:
    """Read the Qurʾān word-by-word database into a dict."""
    with Path(db_path).expanduser().open(encoding="utf-8") as fh:
        return json.load(fh)


# ----------------------------------------------------------------------
# Reference parsing helpers
# ----------------------------------------------------------------------

def _key_to_tuple(key: str) -> Tuple[int, int, int]:
    """'s:v:w' → (s, v, w) with *w* defaulting to 0 for comparisons."""
    s, v, *rest = key.split(":")
    w = rest[0] if rest else 0
    return int(s), int(v), int(w)


def _parse_endpoint(spec: str) -> Tuple[int, int, int | None]:
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


def keys_for_reference(ref: str, db: Dict[str, dict]) -> List[str]:
    """
    Return an **ordered** list of location keys matching *ref*.
    """
    if "-" not in ref:                               # single spec
        start = end = _parse_endpoint(ref)
    else:                                            # range
        left, right = ref.split("-")
        start, end = _parse_endpoint(left), _parse_endpoint(right)

    # Canonicalise: fill missing verse/word with 0 / big number
    def canon(tpl, is_end=False):
        s, v, w = tpl
        if v is None:
            return (s,   0 if not is_end else 10_000, 0 if not is_end else 10_000)
        if w is None:
            return (s, v, 0 if not is_end else 10_000)
        return (s, v, w)

    lo = canon(start)
    hi = canon(end, is_end=True)

    # Collect keys inside range
    selected = [
        k for k in db.keys()
        if lo <= _key_to_tuple(k) <= hi
    ]
    return sorted(selected, key=_key_to_tuple)
