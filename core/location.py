"""
Location class for the Quranic phonemizer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """Location metadata for a word."""
    sura_num: int
    aya_num: int
    word_num: int
    location_key: str

    @classmethod
    def from_key(cls, key: str) -> Location:
        """Create a Location from a location key like '1:1:1'."""
        parts = key.split(':')
        return cls(
            sura_num=int(parts[0]),
            aya_num=int(parts[1]),
            word_num=int(parts[2]),
            location_key=key
        )
