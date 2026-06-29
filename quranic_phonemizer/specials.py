"""
Special word handling for location-specific phonemization rules.

Some words require special handling when phonemizing, especially for
stopping (waqf) scenarios.
"""

from pathlib import Path
from typing import Dict, Optional


_DISPLAY_TEXT_MAP: Optional[Dict[str, str]] = None
_TAJWEED_MAPPING_MAP: Optional[Dict[str, list]] = None


def get_display_text(location_key: str) -> Optional[str]:
    """Return spelled-out display_text for huroof muqattaat, or None."""
    global _DISPLAY_TEXT_MAP
    if _DISPLAY_TEXT_MAP is None:
        import yaml
        yaml_path = Path(__file__).resolve().parent / "resources" / "muqattaat.yaml"
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _DISPLAY_TEXT_MAP = {}
        for entry in data.get("muqattaat", []):
            display = entry.get("display_text")
            if display:
                for loc in entry.get("locations", []):
                    _DISPLAY_TEXT_MAP[loc] = display
    return _DISPLAY_TEXT_MAP.get(location_key)


def get_tajweed_mapping(location_key: str) -> Optional[list]:
    """Return tajweed_mapping list for muqattaat, or None."""
    global _TAJWEED_MAPPING_MAP
    if _TAJWEED_MAPPING_MAP is None:
        import yaml
        yaml_path = Path(__file__).resolve().parent / "resources" / "muqattaat.yaml"
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _TAJWEED_MAPPING_MAP = {}
        for entry in data.get("muqattaat", []):
            tm = entry.get("tajweed_mapping")
            if tm:
                for loc in entry.get("locations", []):
                    _TAJWEED_MAPPING_MAP[loc] = tm
    return _TAJWEED_MAPPING_MAP.get(location_key)


