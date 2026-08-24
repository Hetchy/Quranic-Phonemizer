"""Lexical facts recovered independently of a script's written detail."""
from __future__ import annotations

from ...model.canon import ABJAD, CanonLetter, Nucleus, Onset, Quality
from .vocabulary import Context

#: The name is a lam before a haa, and the lam before it or the wasl hamza.
ALLAH_TAIL = (CanonLetter.LAM, CanonLetter.HEH)
ALLAH_HEAD = (CanonLetter.LAM, CanonLetter.HAMZA)
CONTRACTED_ALLAH_PREFIXES = ((), (CanonLetter.FA,), (CanonLetter.WAW,))


def contracted_divine_name(
    letters: list[CanonLetter], nuclei: list, onsets: list, lexicon
) -> list[int]:
    """The second lam in `لله`, whose shadda and fatha are not always drawn."""
    del onsets
    out: list[int] = []
    for index in range(1, len(letters) - 1):
        if (
            letters[index - 1:index + 2]
            == [CanonLetter.LAM, CanonLetter.LAM, CanonLetter.HEH]
            and tuple(letters[:index - 1]) in CONTRACTED_ALLAH_PREFIXES
            and nuclei[index - 1].quality is Quality.I
            and nuclei[index].is_silent
            and lexicon.is_divine_name(_tail(letters, index))
        ):
            out.append(index)
    return out


def divine_name(
    letters: list[CanonLetter], nuclei: list, onsets: list, lexicon
) -> list[int]:
    """Indices of the lam of the divine name, from the letters alone.

    Script-independent by construction: one script writes the alif and the
    other does not, so keying on the nucleus would tag only one of them.
    """
    out: list[int] = []
    for i, letter in enumerate(letters):
        if letter is not ALLAH_TAIL[0] or i == 0 or i + 1 >= len(letters):
            continue
        if letters[i + 1] is not ALLAH_TAIL[1]:
            continue
        if letters[i - 1] not in ALLAH_HEAD:
            continue
        if nuclei[i].quality is not Quality.A:
            continue
        doubled = onsets[i] is Onset.GEMINATE or (
            letters[i - 1] is CanonLetter.LAM
            and nuclei[i - 1].is_silent
        )
        if not doubled:
            continue
        if not lexicon.is_divine_name(_tail(letters, i)):
            continue
        out.append(i)
    return out


def _tail(letters: list[CanonLetter], start: int) -> str:
    return "".join(ABJAD[letter.value] for letter in letters[start:])


def allah_long_a(
    letters: list[CanonLetter], nuclei: list, onsets: list, lexicon
) -> list[int]:
    """Of those, the ones whose nucleus must still become a long `a`.

    Uthmani writes `ٱللَّهِ` with no alif at all; IndoPak writes the dagger.
    """
    return [
        i
        for i in divine_name(letters, nuclei, onsets, lexicon)
        if nuclei[i].is_short
        and nuclei[i].quality is Quality.A
    ]


#: What the divine name's short `a` becomes. A value, not a transform: the
#: only relengthening there is has one answer, and `Nucleus` is frozen.
RELENGTHENED_A = Nucleus.long(Quality.A)


def unmarked_layl(
    letters: list[CanonLetter], nuclei: list, onsets: list
) -> list[int]:
    """The lexical lam of `al-layl` when its shadda and fatha are implicit."""
    shape = (
        CanonLetter.HAMZA,
        CanonLetter.LAM,
        CanonLetter.YA,
        CanonLetter.LAM,
    )
    if (
        tuple(letters) == shape
        and onsets[0] is Onset.WASL
        and nuclei[1].is_silent
        and nuclei[2].is_silent
    ):
        return [1]
    return []


#: The two particles the rasm joins to the word behind them: the vocative
#: `يا` and `ها` التنبيه. Both end in the long `a` that carries the join.
JOINING_PARTICLES = (CanonLetter.YA, CanonLetter.HEH)


def joined_particle(
    letters: list[CanonLetter], nuclei: list, onsets: list, lexicon
) -> list[int]:
    """Index of a particle the rasm joined to a word that follows it.

    `يَـٰٓأَيُّهَا`, `هَـٰٓؤُلَآءِ` -- one word written and two spoken, so the
    hamza behind the long `a` opens a word rather than standing inside one.
    """
    del onsets
    for i in (0, 1):
        if i >= len(letters) or letters[i] not in JOINING_PARTICLES:
            continue
        if i and not _heads_the_word(letters[0], lexicon):
            continue
        if i + 1 >= len(letters) or letters[i + 1] is not CanonLetter.HAMZA:
            continue
        if not nuclei[i].is_long or nuclei[i].quality is not Quality.A:
            continue
        if not lexicon.joins_a_particle(_tail(letters, i)):
            continue
        return [i]
    return []


def _heads_the_word(letter: CanonLetter, lexicon) -> bool:
    """One proclitic (`وَهَـٰٓؤُلَآءِ`) or the interrogative hamza
    (`أَهَـٰٓؤُلَآءِ`) leaves the particle word-initial. Anything else and the
    shape is a root: the yaa of `ضِيَآءً` has the same `a` before a hamza."""
    return (
        letter is CanonLetter.HAMZA
        or ABJAD[letter.value] in lexicon.affixes.proclitics
    )


def otiose_waw(context: Context) -> bool:
    """`أُو۟لَـٰٓئِكَ`, `أُو۟لِى` - a waw in the rasm that never sounds.

    A script that marks its silent letters never reaches here; one that marks
    what it sounds leaves this waw bare, and `ٱلْأُولَىٰ` is the same shape.
    """
    cluster = context.cluster
    if cluster.marks or not cluster.marked_script:
        return False
    if context.index == context.word_bounds[0]:
        return False
    head = context.clusters[context.index - 1]
    following = context.ahead()
    return (
        head.letter in (CanonLetter.ALIF, CanonLetter.HAMZA)
        and head.has("damma")
        and cluster.letter is CanonLetter.WAW
        and following is not None
        and following.letter in (CanonLetter.LAM, CanonLetter.RA)
    )


#: The two letters that carry a leen with a preceding fatha.
LEEN_CARRIERS = (CanonLetter.YA, CanonLetter.WAW)

#: The letters a hamza may be seated on.
SEATS = (CanonLetter.ALIF, CanonLetter.WAW, CanonLetter.YA)


def hamza_seat(context: Context) -> bool:
    """`ٱللُّؤْلُؤِ`, `ٱلسَّيِّئِ` - the letter a hamza sits on, which spells
    no sound of its own. A script that precomposes the seat never gets here;
    one that writes it out leaves it bare, since it marks what it sounds."""
    cluster = context.cluster
    following = context.ahead()
    return (
        cluster.marked_script
        and cluster.letter in SEATS
        and not cluster.marks
        and following is not None
        and following.letter is CanonLetter.HAMZA
    )


def alif_in_leen(context: Context) -> bool:
    """`تَا۟يْـَٔسُوا۟` - a bare alif inside a leen, which needs neither a
    carrier nor a prosthetic hamza. Uthmani marks it, IndoPak does not."""
    cluster = context.cluster
    following = context.ahead()
    return (
        cluster.letter is CanonLetter.ALIF
        and not cluster.has("fatha", "damma", "kasra", "shadda")
        and not context.word_initial
        and context.clusters[context.index - 1].has("fatha")
        and following is not None
        and following.letter in LEEN_CARRIERS
        and following.has("sukun")
    )


def _alif_al_fasila(context: Context, previous) -> bool:
    """The alif written after a verb's waw and never said: `قَالُوا۟`,
    `يَعْفُوَا۟`. The dual's alif is written the same and is read, and what
    tells them apart is the vowel before the waw."""
    if context.previous_letter is not CanonLetter.WAW:
        return False
    if not previous.is_short:
        return True   # the quiescent plural waw
    # `يَعْفُوَا۟` carries the stem's damma; `ذَوَا` and `دَعَوَا` a fatha.
    before = context.index - 2
    return before >= context.word_bounds[0] and context.clusters[before].has("damma")


def otiose_alif(context: Context) -> bool:
    """The alif of the plural waw (`قَالُوا۟`), and the alif no vowel can carry.

    Word-finally after a waw or a short u, or anywhere after a short vowel
    that is not a, a bare alif is rasm.
    """
    cluster = context.cluster
    if cluster.letter is not CanonLetter.ALIF or cluster.marks:
        return False
    if context.word_initial:
        return False   # the previous nucleus belongs to another word
    if alif_in_leen(context):
        return True
    previous = context.previous_nucleus
    if previous is None:
        return False
    if context.word_final and (
        _alif_al_fasila(context, previous)
        or (previous.is_short and previous.quality is Quality.U)
    ):
        return True
    return previous.is_short and previous.quality is not Quality.A
