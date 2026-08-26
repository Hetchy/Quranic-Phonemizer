"""The shared-rule baseline bound by Warsh through al-Azraq."""

from __future__ import annotations

from ...engine.classifier import RuleSet
from ...engine.plan import Phase
from ...model.address import Riwayah
from ...rules.annotation import CanonicalColour, Inclination
from ...rules.boundary import (
    DroppedGlide,
    IwadLength,
    PausalAlif,
    TaaMarbutaAtWaqf,
    TanweenDrop,
    TanweenIwad,
    WaqfHarakaDrop,
    WaqfSilahDrop,
)
from ...rules.idgham import Idgham
from ...rules.lam_shamsiyyah import ArticleLam, ArticleShape
from ...rules.lam import LamWeight
from ...rules.madd import (
    IltiqaShortening,
    MaddClass,
    MaddBadal,
    MaddLeen,
    MaddSilah,
)
from ...rules.warsh_madd import (
    MaddLeenMahmuz,
    MaddMimAlJam,
    MaddYaaZawaid,
    StartedBadal,
)
from ...rules.pausal_glide import PausalGlide
from ...rules.meem_sakinah import GhunnahMushaddadah, MeemSakinah
from ...rules.naql import CarriedNaql, Naql
from ...rules.noon_sakinah import IkhfaaWeight, NoonSakinah
from ...rules.qalqala import Qalqala
from ...rules.single_hamza import JoinedIbdal, SuppliedIbdal
from ...rules.hamza_meetings import HamzaMeetingMadd, HamzaMeetings
from ...rules.raa import RaaWeight
from ...rules.tafkheem import Emphasis, Weight
from ...model.address import Location
from ...model.canon import Quality
from ...rules.wasl import (
    SoftenedHamza,
    SpelledBeforeWasl,
    TanweenBeforeWasl,
    WaslHamza,
)
from .resources import khilaf, lexicon, rule_tables
from .hamza_meetings import meeting_rows, rows_by_target
from .lam import PROFILE as LAM_PROFILE
from .raa import PROFILE as RAA_PROFILE

#: Warsh repairs a collision with damm when the elided word starts on an
#: original damm; the shared kasra and fatha defaults stand elsewhere.
_DAMM_START_REPAIR = {Quality.U: Quality.U}

#: The `كتابيه إني` boundary reads tahqiq by default: haa stays sakin and
#: the qata is fully realized, so the general transfer must not claim it.
_NAQL_TAHQIQ = frozenset({Location(69, 20, 1)})
_HAMZA_MEETING_STARTS = frozenset(
    row.canonical for row in meeting_rows() if row.scope != "one_word"
)

# Canonical locations of مَوْئِلا and الْمَوْءُودَة.  Only the first waw of
# the latter can satisfy the leen predicate; its following long remains badal.
_LEEN_MAHMUZ_EXCLUDED = frozenset({
    Location(18, 58, 19),
    Location(81, 8, 2),
})


def _article(tables) -> ArticleShape:
    return ArticleShape(
        prefixes=tables.proclitics,
        is_form_eight_lam=lexicon().is_form_eight_lam,
    )


def _boundary() -> tuple:
    return (
        Naql(excluded=_NAQL_TAHQIQ | _HAMZA_MEETING_STARTS),
        CarriedNaql(),
        HamzaMeetings(rows=rows_by_target()),
        SuppliedIbdal(),
        JoinedIbdal(),
        WaslHamza(),
        SoftenedHamza(),
        PausalAlif(),
        SpelledBeforeWasl(repairs=_DAMM_START_REPAIR),
        TanweenBeforeWasl(repairs=_DAMM_START_REPAIR),
        TanweenDrop(),
        TanweenIwad(),
        WaqfHarakaDrop(yaa=khilaf().yaa),
        WaqfSilahDrop(),
        DroppedGlide(yaa=khilaf().yaa),
        TaaMarbutaAtWaqf(),
    )


def _build() -> RuleSet:
    tables = rule_tables()
    article = _article(tables)
    return RuleSet(
        {
            Phase.BOUNDARY: _boundary(),
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
                HamzaMeetingMadd(),
                MaddClass(badal_is_effective=True),
                MaddClass(additive_arid=True),
                MaddLeen(mahmuz_is_distinct=True),
                MaddLeenMahmuz(excluded=_LEEN_MAHMUZ_EXCLUDED),
                MaddBadal(),
                StartedBadal(),
                MaddSilah(),
                MaddMimAlJam(),
                MaddYaaZawaid(),
                IwadLength(),
            ),
            Phase.COLOUR: (
                LamWeight(profile=LAM_PROFILE),
                Emphasis(weight=Weight(
                    always_heavy=tables.always_heavy,
                    raa_enabled=False,
                )),
                RaaWeight(profile=RAA_PROFILE),
                Inclination(),
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
