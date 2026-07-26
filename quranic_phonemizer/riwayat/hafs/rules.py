"""Hafs binds its rules here.

`rules_for` and `adapters_for` are siblings, because a riwayah owns its scripts
as well as its rules (ADR-004 §6). Supporting a second riwayah swaps typed
classifiers in this list; it does not subclass a profile and it does not put an
`if riwayah == …` inside any rule.
"""
from __future__ import annotations

from ...engine.classifier import RuleSet
from ...model.address import Riwayah
from ...model.canon import Phase
from ...rules.boundary import (
    TaaMarbutaAtWaqf,
    TanweenAtWaqf,
    WaqfEnding,
    WaslHamza,
)
from ...rules.lam_shamsiyyah import ArticleLam
from ...rules.madd import PausalGlide
from ...rules.meem_sakinah import GhunnahMushaddadah
from ...rules.noon_sakinah import NoonSakinah
from ...rules.qalqala import Qalqala
from ...rules.tafkheem import Emphasis

HAFS = RuleSet(
    {
        Phase.BOUNDARY: (WaslHamza(), TanweenAtWaqf(), WaqfEnding(), TaaMarbutaAtWaqf()),
        Phase.MERGE: (NoonSakinah(), ArticleLam(), GhunnahMushaddadah()),
        Phase.LENGTH: (PausalGlide(),),
        Phase.COLOUR: (Emphasis(),),
        Phase.RELEASE: (Qalqala(),),
    }
)


def rules_for(riwayah: Riwayah) -> RuleSet:
    if riwayah is not Riwayah.HAFS:
        raise ValueError(f"{__name__} assembles hafs, not {riwayah.value}")
    return HAFS
