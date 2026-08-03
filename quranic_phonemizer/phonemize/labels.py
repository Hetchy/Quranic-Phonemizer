"""Item 40: the four teaching labels of `07-rules.md` section 4.

Each is a predicate over an already-assembled `RuleInstance` and the unit it
names; none mints an instance of its own.
"""
from __future__ import annotations

import dataclasses

from ..model.canon import CanonLetter, Rule
from . import nodes as nd

#: The rules that lengthen a vowel by the canon's own account. `madd_leen`
#: names a vowel that stays short and `iltiqa_shortening` sets a length
#: rather than reading one, so neither is a candidate here.
MADD_RULES = frozenset({
    Rule.MADD_TABII, Rule.MADD_WAJIB_MUTTASIL, Rule.MADD_JAIZ_MUNFASIL,
    Rule.MADD_LAZIM, Rule.MADD_ARID_LIL_SUKUN,
})


def with_labels(
    instances: tuple[nd.RuleInstance, ...], units: tuple[nd.Unit, ...]
) -> tuple[nd.RuleInstance, ...]:
    """Every instance, `labels` filled in where a predicate holds."""
    iwad_noons = {i.source for i in instances if i.rule is Rule.IWAD}
    return tuple(_labelled(instance, units, iwad_noons) for instance in instances)


def _labelled(instance, units, iwad_noons) -> nd.RuleInstance:
    if instance.source is None or instance.rule not in MADD_RULES:
        return instance
    unit = units[instance.source]
    labels = list(_labels_of(instance, unit, iwad_noons))
    return instance if not labels else dataclasses.replace(
        instance, labels=tuple(labels)
    )


def _labels_of(instance, unit: nd.Unit, iwad_noons: set[int]):
    # A tanween's noon sits immediately after the unit its fathatan
    # lengthens: `canon.build` inserts it contiguous with its host.
    if instance.source + 1 in iwad_noons:
        yield "madd_iwad"
    if unit.letter is CanonLetter.HAMZA and unit.vowel.sounds_long:
        yield "madd_badal"
    if unit.vowel.is_silah:
        yield "silah"
        if instance.rule is Rule.MADD_JAIZ_MUNFASIL:
            yield "silah_kubra"


__all__ = ["MADD_RULES", "with_labels"]
