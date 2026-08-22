"""The three module functions, and the vocabulary `Phonemizer` reads a
`variants` argument against and reports one back with.
"""
from __future__ import annotations

from ..api import PACKAGES, recitation
from ..model.address import (
    KhilafId,
    Option,
    Riwayah,
    Script,
    VariantSelection,
    check_riwayah,
)
from ..model.definitions import RULE_DEFINITIONS, SILENCE_DEFINITIONS

#: Hafs is Uthmani by default; a second riwayah adds its own row.
DEFAULT_SCRIPT: dict[Riwayah, Script] = {Riwayah.HAFS: Script.UTHMANI}


def supported_riwayat() -> tuple[str, ...]:
    return tuple(sorted(r.value for r in PACKAGES))


def tajweed_rules(riwayah: str) -> tuple[tuple[str, str, str, str], ...]:
    """One row per identifier a result can publish -- every rule, then the
    silence reasons: identifier, English name, Arabic name, summary."""
    check_riwayah(riwayah)
    return tuple(
        (identifier.value, *definition)
        for identifier, definition in (
            *RULE_DEFINITIONS.items(), *SILENCE_DEFINITIONS.items()
        )
    )


def available_variants(riwayah: str) -> dict[str, dict]:
    khilaf = recitation(check_riwayah(riwayah)).khilaf
    return khilaf.points()


def resolved_variant(khilaf, selection: VariantSelection) -> dict[str, str]:
    """Return the scalar choice resolved for every published variant."""
    return {
        point.value: spec.choose(selection)
        for point, spec in khilaf.variants.items()
    }


def to_selection(variants: dict | None) -> VariantSelection:
    """Convert the public scalar mapping into a typed selection."""
    if not variants:
        return VariantSelection()
    options = []
    for key, value in variants.items():
        khilaf = KhilafId(key)
        if not isinstance(value, str):
            raise TypeError(
                f"{key}: variant choices are scalar strings, got "
                f"{type(value).__name__}"
            )
        options.append(Option(khilaf, value))
    return VariantSelection(tuple(options))


__all__ = [
    "DEFAULT_SCRIPT",
    "available_variants",
    "check_riwayah",
    "resolved_variant",
    "supported_riwayat",
    "tajweed_rules",
    "to_selection",
]
