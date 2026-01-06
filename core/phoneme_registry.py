"""phoneme_registry.py
Central registry that loads base and rule phoneme YAML files once and allows
fast lookup of phonemes by Arabic character or rule key.

Supports runtime overrides via set_phoneme_override() for configurable
Tajweed rules like iqlab and ikhfaa shafawi.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# We keep the resources beside core package
DATA_DIR = Path(__file__).resolve().parent / "resources"

_BASE_CACHE: Dict[str, str] = {}
_RULE_CACHE: Dict[str, Any] = {}
_INITIALISED = False

# Runtime overrides: (rule, key) -> phoneme
_OVERRIDES: Dict[tuple, str] = {}


def _init() -> None:
    global _INITIALISED, _BASE_CACHE, _RULE_CACHE
    if _INITIALISED:
        return

    base_path = DATA_DIR / "base_phonemes.yaml"
    rule_path = DATA_DIR / "rule_phonemes.yaml"

    if base_path.exists():
        with base_path.open("r", encoding="utf-8") as fh:
            base_data = yaml.safe_load(fh)
        for letter_type, info in base_data.get("letters", {}).items():
            char = info.get("char")
            phoneme = info.get("phoneme", "")
            if char:
                _BASE_CACHE[char] = phoneme
    else:
        raise FileNotFoundError(base_path)

    if rule_path.exists():
        with rule_path.open("r", encoding="utf-8") as fh:
            _RULE_CACHE = yaml.safe_load(fh) or {}
    else:
        raise FileNotFoundError(rule_path)

    _INITIALISED = True


def get_base_phoneme(char: str) -> str:
    """Return the default phoneme for an Arabic letter character."""
    if not _INITIALISED:
        _init()
    return _BASE_CACHE.get(char, "")


def get_rule_phoneme(rule: str, key: str = "phoneme", default: str = "") -> str:
    """Return a phoneme defined in rule_phonemes.yaml.

    Checks runtime overrides first, then falls back to YAML values.

    Example::
        get_rule_phoneme("ikhfaa", "light_phoneme")
    """
    if not _INITIALISED:
        _init()
    # Check for runtime override first
    override_key = (rule, key)
    if override_key in _OVERRIDES:
        return _OVERRIDES[override_key]
    section = _RULE_CACHE.get(rule, {})
    return section.get(key, default)


def set_phoneme_override(rule: str, key: str, phoneme: str) -> None:
    """Set a runtime override for a rule phoneme.

    Args:
        rule: Rule name (e.g., "iqlab", "ikhfaa")
        key: Key within the rule (e.g., "phoneme", "shafawi_phoneme")
        phoneme: The phoneme to use instead of the YAML default
    """
    _OVERRIDES[(rule, key)] = phoneme


def clear_phoneme_overrides() -> None:
    """Clear all runtime phoneme overrides."""
    _OVERRIDES.clear()


def get_phoneme_overrides() -> Dict[tuple, str]:
    """Get a copy of current phoneme overrides."""
    return dict(_OVERRIDES)
