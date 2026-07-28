"""Hafs binds its rules here.

Adding a riwayah swaps typed classifiers in this list and edits its own
rules.yaml, rather than subclassing a profile or branching inside a rule.
"""
from __future__ import annotations

from ...engine.classifier import RuleSet
from ...model.address import Riwayah
from ...model.canon import Phase
from ...rules.annotation import CanonicalColour, Sakt, Silah, Tarqeeq
from ...rules.boundary import (
    SoftenedHamza,
    TaaMarbutaAtWaqf,
    TanweenAtWaqf,
    WaqfEnding,
    WaslHamza,
)
from ...rules.idgham import Idgham
from ...rules.lam_shamsiyyah import ArticleLam, ArticleShape
from ...rules.madd import IltiqaRepair, MaddClass, MaddLeen, PausalGlide
from ...rules.meem_sakinah import GhunnahMushaddadah, MeemSakinah
from ...rules.noon_sakinah import NoonSakinah
from ...rules.qalqala import Qalqala
from ...rules.tafkheem import Emphasis, Weight
from .resources import khilaf, lexicon, rule_tables


def _build() -> RuleSet:
    tables = rule_tables()
    weight = Weight(always_heavy=tables.always_heavy, raa=khilaf().raa)
    article = ArticleShape(
        prefixes=tables.proclitics,
        is_form_eight_lam=lexicon().is_form_eight_lam,
    )
    return RuleSet(
        {
            Phase.BOUNDARY: (
                WaslHamza(), SoftenedHamza(), TanweenAtWaqf(),
                WaqfEnding(yaa=khilaf().yaa),
                TaaMarbutaAtWaqf(), Sakt(),
            ),
            Phase.MERGE: (
                NoonSakinah(followers=tables.followers_of_noon),
                MeemSakinah(followers=tables.followers_of_meem),
                ArticleLam(sun=tables.sun_letters, article=article),
                GhunnahMushaddadah(),
                Idgham(pairs=tables.pairs,
                       never_follows=tables.never_follows,
                       article=article),
            ),
            Phase.LENGTH: (
                PausalGlide(), IltiqaRepair(), MaddClass(), MaddLeen(), Silah(),
            ),
            Phase.COLOUR: (
                Emphasis(weight=weight),
                Tarqeeq(weight=weight),
                CanonicalColour(),
            ),
            Phase.RELEASE: (Qalqala(letters=tables.qalqala),),
        }
    )


HAFS = _build()


def rules_for(riwayah: Riwayah) -> RuleSet:
    if riwayah is not Riwayah.HAFS:
        raise ValueError(f"{__name__} assembles hafs, not {riwayah.value}")
    return HAFS
