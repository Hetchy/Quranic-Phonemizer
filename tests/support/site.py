"""Where a case sits, keyed by riwayah.

Word indices are riwayah data, so the same words take a different address
under a different transmission and a site cannot share one.
"""
from __future__ import annotations

from dataclasses import dataclass

from quranic_phonemizer.api import PACKAGES
from quranic_phonemizer.model.address import Riwayah, VerseRef


@dataclass(frozen=True, slots=True)
class Address:
    verse: VerseRef
    words: tuple[int, ...]


def _address(value) -> Address:
    """`"2:5"` for a whole verse, or `("2:5", (3, 4))` for named words."""
    ref, words = value if isinstance(value, tuple) else (value, ())
    surah, ayah = (int(part) for part in ref.split(":"))
    return Address(VerseRef(surah, ayah), tuple(words))


class Site:
    """One case's address under each riwayah that has one."""

    def __init__(self, **per_riwayah) -> None:
        self.addresses = {
            name: _address(value) for name, value in per_riwayah.items()
        }

    def shipped(self) -> tuple[str, ...]:
        """Declared riwayat this build can actually read, in declared order."""
        return tuple(
            name for name in self.addresses
            if Riwayah(name) in PACKAGES
        )

    def address(self, riwayah: str) -> Address:
        return self.addresses[riwayah]
