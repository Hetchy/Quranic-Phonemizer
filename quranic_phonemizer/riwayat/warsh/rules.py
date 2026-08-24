"""The shared-rule baseline bound by Warsh through al-Azraq."""

from __future__ import annotations

from ...engine.classifier import RuleSet
from ...engine.plan import Phase
from ...model.address import Riwayah
from ...rules.annotation import CanonicalColour, Tarqeeq
from ...rules.boundary import (
    DroppedGlide,
    IwadLength,
    TaaMarbutaAtWaqf,
    TanweenDrop,
    TanweenIwad,
    WaqfHarakaDrop,
    WaqfSilahDrop,
)
from ...rules.idgham import Idgham
from ...rules.lam_shamsiyyah import ArticleLam, ArticleShape
from ...rules.madd import (
    IltiqaShortening,
    MaddClass,
    MaddLeen,
    MaddSilah,
)
from ...rules.pausal_glide import PausalGlide
from ...rules.meem_sakinah import GhunnahMushaddadah, MeemSakinah
from ...rules.noon_sakinah import IkhfaaWeight, NoonSakinah
from ...rules.qalqala import Qalqala
from ...rules.tafkheem import Emphasis, Weight
from ...rules.wasl import SpelledBeforeWasl, TanweenBeforeWasl, WaslHamza
from .resources import khilaf, lexicon, rule_tables


def _article(tables) -> ArticleShape:
    return ArticleShape(
        prefixes=tables.proclitics,
        is_form_eight_lam=lexicon().is_form_eight_lam,
    )


def _build() -> RuleSet:
    tables = rule_tables()
    weight = Weight(always_heavy=tables.always_heavy)
    article = _article(tables)
    return RuleSet(
        {
            Phase.BOUNDARY: (
                WaslHamza(),
                SpelledBeforeWasl(),
                TanweenBeforeWasl(),
                TanweenDrop(),
                TanweenIwad(),
                WaqfHarakaDrop(yaa=khilaf().yaa),
                WaqfSilahDrop(),
                DroppedGlide(yaa=khilaf().yaa),
                TaaMarbutaAtWaqf(),
            ),
            Phase.MERGE: (
                NoonSakinah(followers=tables.followers_of_noon),
                MeemSakinah(followers=tables.followers_of_meem),
                ArticleLam(sun=tables.sun_letters, article=article),
                GhunnahMushaddadah(sun=tables.sun_letters, article=article),
                Idgham(
                    pairs=tables.pairs,
                    never_follows=tables.never_follows,
                    article=article,
                ),
            ),
            Phase.LENGTH: (
                PausalGlide(),
                IltiqaShortening(),
                MaddClass(),
                MaddClass(additive_arid=True),
                MaddLeen(),
                MaddSilah(),
                IwadLength(),
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


WARSH = _build()


def rules_for(riwayah: Riwayah) -> RuleSet:
    if riwayah is not Riwayah.WARSH:
        raise ValueError(f"{__name__} assembles warsh, not {riwayah.value}")
    return WARSH


__all__ = ["WARSH", "rules_for"]
