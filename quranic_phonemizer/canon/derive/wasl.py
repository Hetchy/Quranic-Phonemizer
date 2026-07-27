"""Hamzat al-wasl: three morphological rules, plus a small lexicon for what
no orthographic test can separate from them. A rule can be checked against
grammar; a list cannot.
"""
from __future__ import annotations

from ...model.canon import ABJAD, CanonLetter, Onset, Quality, Short
from ...model.inscription import SlotFact
from . import Context, Outcome, Sets, lexeme, register

VOWEL_ROLES = frozenset({"fatha", "damma", "kasra"})
QUIESCENT_BLOCKERS = frozenset(VOWEL_ROLES | {"fathatan", "dammatan", "kasratan"})

#: The letters the form-VIII infixed taa assimilates into. A geminate drawn
#: from this set after a prosthetic hamza is `افتعل`; a geminate outside it is
#: a particle - `إنّ`, `إلّا`, `إيّاك`.
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

#: Letters that may carry a proclitic before a medial wasl.
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
        CanonLetter.ALIF,
    }
)


def is_wasl(context: Context) -> bool:
    """The decision procedure. `canon.build` names it for every bare alif.

    Check order is load-bearing: written evidence of the article outranks the
    lexeme list, and the list outranks the shape alone.
    """
    cluster = context.cluster
    if cluster.letter not in (CanonLetter.ALIF, CanonLetter.HAMZA):
        return False
    if cluster.has("dagger", "combining_hamza", "shadda", "madd"):
        # Madd badal, a seated hamza, or the ibdal alif that replaces the
        # article's hamza after an interrogative one in `ءَآلذَّكَرَيْنِ`.
        return False
    if not (context.word_initial or _after_proclitics(context)):
        return False
    if lexeme.alif_in_leen(context):
        return False  # rasm inside a diphthong, not a prop for a quiescent letter
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
    if following.letter is CanonLetter.LAM and _assimilated_sun_letter(context):
        return True  # only the article puts a geminate after a vowelless lam
    if context.lexicon.is_wasl_exempt(_skeleton(context)):
        # `ألقى`, `ألف`, `ألسنة` and `ألوان` all begin hamza + lam and none of
        # them is the article; nothing orthographic separates them from it, so
        # the list is consulted before the lam branch below.
        return False
    if following.letter is CanonLetter.LAM:
        return True  # the article, with its helping vowel written out
    if _is_form_four_masdar(context):
        # `إفعال` - إكراه، إصلاح، إسراف، إعراض، إلحاف. A long aa in the second
        # syllable is the shape's signature and no imperative has one:
        # `اذهب`, `انظر`, `اجتنبوا` are short throughout. Form X's masdar
        # (`استكبارًا`) keeps its wasl because its long vowel comes later.
        # Checked after the article, which also often carries a long aa.
        return False
    if _is_nunated(context):
        # A word carrying tanween is a fully inflected noun, and no prosthetic
        # hamza begins one - the ten nouns are definite or annexed wherever
        # they occur. This is what separates `إفك`, `إنس`, `إخوة`, `إملاق`
        # and every form-IV verbal noun from the imperatives they otherwise
        # look exactly like: quiescent second radical, voweled third.
        return False
    if written is Quality.A:
        return False  # the helping vowel is fatha only for the article
    return written is _helping_vowel(context)


def _geminate_case(context: Context, cluster, following) -> bool:
    written = _written_vowel(cluster)
    if following.letter is CanonLetter.LAM:
        if context.lexicon.is_wasl_exempt_doubled(_skeleton(context)):
            return False
        # `الَّذين` is the article before a lam-initial word; `إلَّا` is a
        # particle. Something real has to follow the lam for it to be the one.
        return any(
            c.letter not in (CanonLetter.ALIF, CanonLetter.WAW, CanonLetter.YA)
            or c.has(*VOWEL_ROLES)
            for c in context.clusters[context.index + 2 : context.word_bounds[1]]
        )
    if written is Quality.A:
        return False
    return following.letter in FORM_EIGHT


def helping_vowel(context: Context) -> Quality:
    """The three-branch grammatical decision for the wasl helping vowel.

    The canonical nucleus of a wasl slot is this vowel, silenced by
    `WASL_ELISION` in connection and realized at ibtida.
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


@register("hamzat_wasl", requires=(
    "fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan",
        "shadda", "silah_waw", "silah_ya",
    "sukun", "dagger", "combining_hamza", "madd",
))
def hamzat_wasl(context: Context) -> Outcome:
    """The wasl slot: a hamza whose onset sounds only at ibtida."""
    del context
    return Sets(SlotFact.ONSET, Onset.WASL)


@register("wasl_helping_vowel", requires=(
    "fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan",
        "shadda", "silah_waw", "silah_ya",
    "sukun", "dagger", "combining_hamza", "madd",
))
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


def _assimilated_sun_letter(context: Context) -> bool:
    third = context.ahead(2)
    return third is not None and third.has("shadda")


def _is_nunated(context: Context) -> bool:
    return any(
        cluster.has("fathatan", "dammatan", "kasratan")
        for cluster in context.clusters[
            context.word_bounds[0] : context.word_bounds[1]
        ]
    )


def _is_form_four_masdar(context: Context) -> bool:
    second, third = context.ahead(1), context.ahead(3)
    if second is None or third is None:
        return False
    if second.marks and not second.has("sukun"):
        return False
    return third.letter is CanonLetter.ALIF and _is_bare_carrier(third)


def _is_bare_carrier(cluster) -> bool:
    """A length carrier spells no letter of the skeleton - which is what lets
    one lexicon entry cover `إسرائيل` and `اِسْرَاءِيْلَ` alike."""
    return cluster.letter in (
        CanonLetter.ALIF,
        CanonLetter.WAW,
        CanonLetter.YA,
    ) and not cluster.has("fatha", "damma", "kasra", "shadda")


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
    span = context.clusters[context.index : context.word_bounds[1]]
    letters = [
        cluster.letter
        for offset, cluster in enumerate(span)
        if cluster.letter is not None
        and not (offset and _is_bare_carrier(cluster))
    ]
    if not letters:
        return ""
    # The candidate position is the hamza under question, whichever seat the
    # script drew it on. Normalising it is what lets one lexicon entry serve
    # `إن` and `اِنْ` alike.
    letters[0] = CanonLetter.HAMZA
    return "".join(ABJAD[letter.value] for letter in letters)
