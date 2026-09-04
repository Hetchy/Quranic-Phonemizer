"""Rule occurrences and mergers placed on exact visible units.

A unit carries the occurrences on the sounds it owns and its silencer; a rule
placement is their inverse, a merger placement its contributors and host.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .dtos import Merger, RuleOccurrence, Sound
from .source_ownership import Ownership


@dataclass(frozen=True, slots=True)
class Placements:
    unit_occurrences: dict[int, tuple[int, ...]]
    rule_placements: tuple[tuple[int, tuple[int, ...]], ...]
    merger_placements: tuple[tuple[int, tuple[int, ...], tuple[int, ...]], ...]


def _unit_occurrences(own: Ownership, sounds: tuple[Sound, ...]) -> dict[int, set[int]]:
    out: dict[int, set[int]] = defaultdict(set)
    for sound, unit in own.owner.items():
        out[unit].update(
            o.value for o in sounds[sound].rule_occurrence_ids
            if o.value not in own.carrier_only
        )
    for unit, silence in own.silence.items():
        if isinstance(silence, int):
            out[unit].add(silence)
    return out


def _rule_placements(unit_occ, occurrences):
    by_occ: dict[int, list[int]] = defaultdict(list)
    for unit, occs in unit_occ.items():
        for occ in occs:
            by_occ[occ].append(unit)
    return tuple(
        (i, tuple(sorted(by_occ.get(i, ())))) for i in range(len(occurrences))
    )


def placements(
    own: Ownership,
    sounds: tuple[Sound, ...],
    occurrences: tuple[RuleOccurrence, ...],
    mergers: tuple[Merger, ...],
) -> Placements:
    unit_occ = _unit_occurrences(own, sounds)
    merger = tuple(
        (
            i,
            tuple(sorted(own.presenters.get(m.sound_id.value, frozenset()))),
            () if own.owner.get(m.sound_id.value) is None
            else (own.owner[m.sound_id.value],),
        )
        for i, m in enumerate(mergers)
    )
    return Placements(
        unit_occurrences={u: tuple(sorted(o)) for u, o in unit_occ.items()},
        rule_placements=_rule_placements(unit_occ, occurrences),
        merger_placements=merger,
    )


__all__ = ["Placements", "placements"]
