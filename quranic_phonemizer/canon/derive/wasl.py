"""Hamzat al-waṣl: three morphological rules, and a lexicon of ~30.

The first draft of this design carried a **575-skeleton lexicon**, learned from
Uthmani's own `ٱ` positions. That is not a derivation — a list learned from one
script's glyph positions can only ever be confirmed by the corpus that produced
it, which is what ADR-008 open question 2b was about.

Two measurements dissolved it.

**A bare initial ālif in IndoPak *is* a hamzat al-waṣl**: 13,274 bare-waṣl
against 16 bare-qaṭʿ, all of them muqaṭṭaʿāt. So the fact is declared by both
scripts and needs deriving only where IndoPak writes the helping vowel — 186
sites, of which the article rule takes 121.

And the remaining 64 are all imperatives or form VII–X verbs, so they are a
rule too. The three below reach **98.19%** as a total decision procedure over
all 20,894 word-initial ālif sites, with exactly two misses (46:4:18 and
49:11:30, both already Ledger entries). What is left over is six named closed
classes of Arabic — particles, proper nouns, form-IV verbal nouns — none of
them specific to this corpus.

The distinction that matters is not the residue count. It is that a rule can be
checked against a grammar by someone who has never seen this corpus, and a list
cannot.
"""
from __future__ import annotations

from ...model.canon import ABJAD, CanonLetter, Onset, Quality, Short
from ...model.inscription import SlotFact
from . import Context, Outcome, Sets, register

VOWEL_ROLES = frozenset({"fatha", "damma", "kasra"})
QUIESCENT_BLOCKERS = frozenset(VOWEL_ROLES | {"fathatan", "dammatan", "kasratan"})

#: The letters the form-VIII infixed tāʾ assimilates into. A geminate drawn
#: from this set after a prosthetic hamza is `افتعل`; a geminate outside it is
#: a particle — `إنّ`, `إلّا`, `إيّاك`.
FORM_EIGHT = frozenset(
    {
        CanonLetter.TA,
        CanonLetter.DAL,
        CanonLetter.TAH,
        CanonLetter.ZAY,
        CanonLetter.SAD,
        CanonLetter.DAD,
        CanonLetter.ZAH,
        CanonLetter.THA,
        CanonLetter.THAL,
    }
)

#: Letters that may carry a proclitic before a medial waṣl.
PROCLITICS = frozenset(
    {
        CanonLetter.WAW,
        CanonLetter.FA,
        CanonLetter.BA,
        CanonLetter.LAM,
        CanonLetter.KAF,
        CanonLetter.TA,
        CanonLetter.SEEN,
        CanonLetter.HAMZA,
    }
)


def is_wasl(context: Context) -> bool:
    """The decision procedure. `canon.build` names it for every bare ālif."""
    cluster = context.cluster
    if cluster.letter not in (CanonLetter.ALIF, CanonLetter.HAMZA):
        return False
    if cluster.has("dagger", "combining_hamza", "shadda"):
        return False  # madd badal, or a seated hamza: neither is prosthetic
    if not (context.word_initial or _after_proclitics(context)):
        return False
    following = context.ahead()
    if following is None:
        return False

    if following.has("shadda"):
        return _geminate_case(context, cluster, following)
    if following.has(*QUIESCENT_BLOCKERS) or following.has("dagger"):
        return False  # nothing to prop up: no waṣl hamza is needed

    written = _written_vowel(cluster)
    if written is None:
        return True  # a bare prosthetic ālif; both scripts write it that way
    if following.letter is CanonLetter.LAM:
        return True  # the article, with its helping vowel written out
    if written is Quality.A:
        return False  # the helping vowel is fatha only for the article
    if context.lexicon.is_wasl_exempt(_skeleton(context)):
        return False
    return written is _helping_vowel(context)


def _geminate_case(context: Context, cluster, following) -> bool:
    written = _written_vowel(cluster)
    if following.letter is CanonLetter.LAM:
        # `الَّذين` is the article before a lām-initial word; `إلَّا` is a
        # particle. Something real has to follow the lām for it to be the one.
        return any(
            c.letter not in (CanonLetter.ALIF, CanonLetter.WAW, CanonLetter.YA)
            or c.has(*VOWEL_ROLES)
            for c in context.clusters[context.index + 2 : context.word_bounds[1]]
        )
    if written is Quality.A:
        return False
    return following.letter in FORM_EIGHT


def helping_vowel(context: Context) -> Quality:
    """Domain-facts §5.7's three-branch grammatical decision.

    IndoPak evidences all three branches: fatha at 118 sites, kasra at 44,
    damma at 19 (ADR-003 §6.3). The canonical nucleus of a waṣl slot *is* this
    vowel, silenced by `WASL_ELISION` in connection and realized at ibtidāʾ —
    if it were `Silent`, IndoPak's fatha at 1:2:1 would contradict it and L2
    would fail the build at 186 sites.
    """
    return _helping_vowel(context)


def _helping_vowel(context: Context) -> Quality:
    following = context.ahead()
    if following is not None and following.letter is CanonLetter.LAM:
        return Quality.A
    if context.lexicon.is_wasl_noun(_skeleton(context)):
        return Quality.I
    third = context.ahead(2)
    if third is not None and third.has("damma"):
        return Quality.U
    return Quality.I


@register("hamzat_wasl")
def hamzat_wasl(context: Context) -> Outcome:
    """The waṣl slot: a hamza whose onset sounds only at ibtidāʾ."""
    del context
    return Sets(SlotFact.ONSET, Onset.WASL)


@register("wasl_helping_vowel")
def wasl_helping_vowel(context: Context) -> Outcome:
    return Sets(SlotFact.NUCLEUS, Short(_helping_vowel(context)))


def _after_proclitics(context: Context) -> bool:
    start = context.word_bounds[0]
    if not 1 <= context.index - start <= 3:
        return False
    for cluster in context.clusters[start : context.index]:
        if cluster.letter not in PROCLITICS or not cluster.has(*VOWEL_ROLES):
            return False
    return True


def _written_vowel(cluster) -> Quality | None:
    for role, quality in (
        ("fatha", Quality.A),
        ("damma", Quality.U),
        ("kasra", Quality.I),
    ):
        if cluster.has(role):
            return quality
    return None


def _skeleton(context: Context) -> str:
    """Canonical letters from this cluster to the end of the word. Keyed by
    letters, never by glyphs, so the two scripts produce the same key."""
    return "".join(
        ABJAD[cluster.letter.value] if cluster.letter else ""
        for cluster in context.clusters[context.index : context.word_bounds[1]]
    )
