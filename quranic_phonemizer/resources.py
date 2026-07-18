from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import Riwayah


@dataclass(frozen=True, slots=True)
class RiwayahResources:
    riwayah: Riwayah
    corpus: Path
    addresses: Path
    script: Path
    tajweed: Path
    render: Path
    muqattaat: Path
    exceptions: Path


def resources_for(riwayah: Riwayah) -> RiwayahResources:
    root = Path(__file__).resolve().parent / "data"
    if riwayah is not Riwayah.HAFS:
        raise NotImplementedError("Warsh phonology has not been implemented")
    return RiwayahResources(
        riwayah=riwayah,
        corpus=root / "riwayat" / "hafs" / "corpus" / "quran_db.bin",
        addresses=root / "riwayat" / "hafs" / "corpus" / "surah_info.json",
        script=root / "riwayat" / "hafs" / "script.yaml",
        tajweed=root / "shared" / "tajweed.yaml",
        render=root / "shared" / "render.yaml",
        muqattaat=root / "shared" / "muqattaat.yaml",
        exceptions=root / "riwayat" / "hafs" / "exceptions.yaml",
    )
