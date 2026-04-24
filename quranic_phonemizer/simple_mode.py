"""Simple-mode phoneme collapse.

Collapses geminated and allophonic variants of phonemes produced by the full
phonemizer into a reduced vocabulary. See ``resources/simple_phonemes.yaml``
for the configured rules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import yaml


_CONFIG_PATH = Path(__file__).resolve().parent / "resources" / "simple_phonemes.yaml"

# Marks that attach to a preceding base character when splitting a phoneme
# token into units for the gemination-collapse pass.
#   ˤ  (U+02E4)          tafkheem / emphatic
#   ̃   (U+0303)          combining tilde (idgham nasalisation)
#   :                    length marker (madd)
_COMBINING_MARKS = frozenset(["ˤ", "̃", ":"])

_config: Optional[dict] = None


def _load_config() -> dict:
    global _config
    if _config is None:
        with _CONFIG_PATH.open("r", encoding="utf-8") as fh:
            _config = yaml.safe_load(fh) or {}
    return _config


def _split_units(token: str) -> List[str]:
    """Split a phoneme token into units of (base char + attached marks).

    e.g. ``"sˤsˤ"`` -> ``["sˤ", "sˤ"]``, ``"aˤ:"`` -> ``["aˤ:"]``.
    """
    units: List[str] = []
    for ch in token:
        if ch in _COMBINING_MARKS and units:
            units[-1] += ch
        else:
            units.append(ch)
    return units


def collapse_token(token: str) -> Optional[str]:
    """Collapse a single phoneme token. Returns ``None`` if the token is dropped."""
    cfg = _load_config()
    if token in (cfg.get("drop_tokens") or []):
        return None

    out = token
    for src, dst in (cfg.get("replace") or {}).items():
        out = out.replace(src, dst)

    if cfg.get("collapse_geminates"):
        units = _split_units(out)
        deduped: List[str] = []
        for u in units:
            if not deduped or deduped[-1] != u:
                deduped.append(u)
        out = "".join(deduped)

    return out


def collapse_phonemes(phonemes: Iterable[str]) -> List[str]:
    """Collapse a sequence of phoneme tokens, dropping any that map to ``None``."""
    result: List[str] = []
    for ph in phonemes:
        collapsed = collapse_token(str(ph))
        if collapsed is not None:
            result.append(collapsed)
    return result
