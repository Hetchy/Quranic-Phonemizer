"""The shipped riwayah packages, registered once. Adding a riwayah is one
row here plus its package directory."""
from __future__ import annotations

from ..engine.classifier import RuleSet
from ..model.address import Riwayah
from . import hafs, warsh

#: Every riwayah this build ships.
PACKAGES = {Riwayah.HAFS: hafs, Riwayah.WARSH: warsh}

#: `Riwayah` is the closed vocabulary the gates check against; a member with
#: no package here would pass them and fail late, so refuse to load instead.
if set(PACKAGES) != set(Riwayah):
    raise RuntimeError("every Riwayah member needs a package in PACKAGES")


def ruleset_for(riwayah: Riwayah) -> RuleSet:
    """The classifiers a riwayah binds, without loading its corpus."""
    return PACKAGES[riwayah].rules_for(riwayah)


def quality_fallbacks_for(riwayah: str | Riwayah) -> dict:
    """Return the notation fallbacks owned by one shipped riwayah."""
    return PACKAGES[Riwayah(riwayah)].QUALITY_FALLBACKS


__all__ = [
    "PACKAGES", "hafs", "quality_fallbacks_for", "ruleset_for", "warsh",
]
