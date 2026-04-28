"""
Location class for the Quranic phonemizer.
"""

from __future__ import annotations


class Location:
    """Location metadata for a word."""

    __slots__ = ("surah_num", "ayah_num", "word_num", "location_key")

    def __init__(self, surah_num: int, ayah_num: int, word_num: int, location_key: str):
        self.surah_num = surah_num
        self.ayah_num = ayah_num
        self.word_num = word_num
        self.location_key = location_key

    @classmethod
    def from_key(cls, key: str) -> Location:
        """Create a Location from a location key like '1:1:1'."""
        s, a, w = key.split(':', 2)
        loc = cls.__new__(cls)
        loc.surah_num = int(s)
        loc.ayah_num = int(a)
        loc.word_num = int(w)
        loc.location_key = key
        return loc

    def __repr__(self) -> str:
        return (
            f"Location(surah_num={self.surah_num}, ayah_num={self.ayah_num}, "
            f"word_num={self.word_num}, location_key={self.location_key!r})"
        )
