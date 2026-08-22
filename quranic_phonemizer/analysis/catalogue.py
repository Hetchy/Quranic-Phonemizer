"""The rule catalogue: one `RuleDefinition` per identifier a bundle can name.

The inventory is the whole vocabulary -- every rule, then the silence
reasons; colour, order, and grouping belong to a consumer.
"""
from __future__ import annotations

from ..model.address import UnknownRiwayah, check_riwayah
from ..model.definitions import RULE_DEFINITIONS, SILENCE_DEFINITIONS
from .dtos import RuleDefinition
from .ids import RuleId


def rule_definitions() -> tuple[RuleDefinition, ...]:
    """The whole inventory, one row per identifier, in the model's order."""
    return tuple(
        RuleDefinition(RuleId(identifier.value), name, arabic_name, summary)
        for identifier, (name, arabic_name, summary) in (
            *RULE_DEFINITIONS.items(), *SILENCE_DEFINITIONS.items()
        )
    )


def tajweed_rules(riwayah: str) -> tuple[RuleDefinition, ...]:
    """The rule inventory for a reading, validated against what ships."""
    check_riwayah(riwayah)
    return rule_definitions()


__all__ = [
    "UnknownRiwayah",
    "check_riwayah",
    "rule_definitions",
    "tajweed_rules",
]
