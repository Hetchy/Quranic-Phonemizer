"""Hafs binds its rules here.

Adding a riwayah swaps typed classifiers in this list and edits its own
rules.yaml, rather than subclassing a profile or branching inside a rule.
"""
from __future__ import annotations

from ...engine.classifier import RuleSet
from ...engine.plan import Phase
from ...model.address import KhilafId, Riwayah
from ...rules.annotation import CanonicalColour, Tarqeeq
from ...rules.boundary import (
    PausalAlif,
    SoftenedHamza,
    TaaMarbutaAtWaqf,
    TanweenAtWaqf,
    TanweenBeforeWasl,
    WaqfEnding,
    WaslHamza,
)
from ...rules.ibtidaa import FakkIdgham
from ...rules.idgham import Idgham
from ...rules.lam_shamsiyyah import ArticleLam, ArticleShape
from ...rules.madd import IltiqaShortening, MaddClass, MaddLeen, PausalGlide
from ...rules.meem_sakinah import GhunnahMushaddadah, MeemSakinah
from ...rules.noon_sakinah import IkhfaaWeight, NoonSakinah
from ...rules.qalqala import Qalqala
from ...rules.tafkheem import Emphasis, Weight
from .resources import khilaf, lexicon, rule_tables


def _build() -> RuleSet:
    tables = rule_tables()
    choices = khilaf()
    weight = Weight(always_heavy=tables.always_heavy, raa=choices.raa)
    article = ArticleShape(
        prefixes=tables.proclitics,
        is_form_eight_lam=lexicon().is_form_eight_lam,
    )
    return RuleSet(
        {
            Phase.BOUNDARY: (
                WaslHamza(), SoftenedHamza(), TanweenAtWaqf(), PausalAlif(),
                TanweenBeforeWasl(),
                WaqfEnding(yaa=choices.yaa),
                TaaMarbutaAtWaqf(),
            ),
            Phase.MERGE: (
                NoonSakinah(
                    followers=tables.followers_of_noon,
                    opening_wasl=choices.definition(KhilafId.NOON_YASEEN_WASL),
                ),
                MeemSakinah(followers=tables.followers_of_meem),
                ArticleLam(sun=tables.sun_letters, article=article),
                GhunnahMushaddadah(sun=tables.sun_letters, article=article),
                Idgham(pairs=tables.pairs,
                       never_follows=tables.never_follows,
                       article=article),
                FakkIdgham(
                    pairs=tables.pairs,
                    followers_of_noon=tables.followers_of_noon,
                    followers_of_meem=tables.followers_of_meem,
                    never_follows=tables.never_follows,
                ),
            ),
            Phase.LENGTH: (
                PausalGlide(), IltiqaShortening(), MaddClass(), MaddLeen(),
            ),
            Phase.COLOUR: (
                Emphasis(weight=weight),
                Tarqeeq(weight=weight),
                CanonicalColour(),
                IkhfaaWeight(
                    followers=tables.followers_of_noon,
                    always_heavy=tables.always_heavy,
                ),
            ),
            Phase.RELEASE: (Qalqala(letters=tables.qalqala, pairs=tables.pairs),),
        }
    )


HAFS = _build()


def rules_for(riwayah: Riwayah) -> RuleSet:
    if riwayah is not Riwayah.HAFS:
        raise ValueError(f"{__name__} assembles hafs, not {riwayah.value}")
    return HAFS
