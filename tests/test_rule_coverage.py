"""Two things no law could see, asserted over the assembled ruleset.

E4 inspects occurrences that *fired*, so a rule that never fires is invisible
to every law in `engine/laws.py`. 15 of 38 `Rule` members were dead and the
suite was green — including the whole mīm sākinah family, in a module whose
docstring named it. And E1 only ran when somebody ran a harness by hand.

Both run here, over the real `HAFS` ruleset. Every other engine test binds a
one-rule `RuleSet`, which is why neither was visible.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.plan import ConflictError
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.riwayat.hafs import HAFS

from conftest import score_for

#: Verses chosen to reach every implemented rule, not verses that happened to
#: be convenient. The named ones below are the *only* sites some families
#: have, and a sample without them was green while four rules were unreached.
SITES = [
    (2, 256),   # قَد تَّبَيَّنَ — mutajanisayn kamil, dāl into tāʾ
    (11, 42),   # ٱرْكَب مَّعَنَا — kamil, bāʾ into mīm
    (7, 176),   # يَلْهَث ذَّٰلِكَ — kamil, thāʾ into dhāl
    (5, 28),    # بَسَطتَ — naqis, ṭāʾ into tāʾ, the first keeping its trace
    (27, 22),   # أَحَطتُ — naqis again
    (23, 118),  # قُل رَّبِّ — mutaqaribayn, lām into rāʾ
    (77, 20),   # نَخْلُقكُّم — mutaqaribayn, the qāf
    (13, 4),    # صِنْوَانٌ — iẓhār muṭlaq
    (6, 99),    # قِنْوَانٌ
    (9, 109),   # بُنْيَٰن
    (2, 85),    # دُنْيَا
    (11, 41),   # مَجْر۪ىٰهَا — imāla, the only site
    (12, 11),   # تَأْمَ۫نَّا — ishmām, the only site
    (41, 44),   # ءَا۬عْجَمِىٌّ — tashīl, the only site
    (75, 27),   # مَنْ ۜ — sakt; 18:1's entry waits on an L1 row
    (7, 1),     # الٓمٓصٓ — muqaṭṭaʿāt, and madd lāzim with them
    (1, 7),     # ٱلضَّآلِّينَ — madd lāzim in an ordinary word
]

#: Plus a broad sweep for the common families: nūn and mīm in all their
#: outcomes, the article lām, qalqala, emphasis, waqf.
SAMPLE = (
    [(1, n) for n in range(1, 8)]
    + [(2, n) for n in range(1, 26)]
    + [(112, n) for n in range(1, 5)]
    + [(114, n) for n in range(1, 7)]
    + SITES
)

#: Declared absent, with the reason. A member here is a promise, not an
#: excuse: it must move out of this list or out of `Rule`.
#: Empty, and that is the point. Every member of `Rule` is produced by some
#: classifier somewhere in the corpus. It held 12 entries when this file was
#: written and 15 members were dead; anything added back needs a reason next
#: to it, and `test_the_deferred_list_does_not_rot` fails if the reason
#: stops being true.
DEFERRED: set[Rule] = set()


def _fired(packed, shared, surah, ayah):
    score = score_for(packed, shared, surah, ayah)
    out = set()
    for junction in (Junction.JOIN, Junction.STOP):
        plan = BoundaryPlan(
            (junction,) * (len(score.words) - 1) + (Junction.EDGE,)
        )
        out |= {o.rule for o in perform(score, HAFS, plan).occurrences}
    return out


def test_every_rule_not_declared_deferred_actually_fires(packed, shared):
    """Falsifier: a `Rule` member with no classifier, like the whole mīm
    sākinah family was. Add a member without a rule and this fails."""
    fired: set[Rule] = set()
    for surah, ayah in SAMPLE:
        fired |= _fired(packed, shared, surah, ayah)
    expected = set(Rule) - DEFERRED
    missing = sorted(rule.value for rule in expected - fired)
    assert not missing, (
        f"declared but never produced: {missing}. Either implement the rule, "
        f"or add it to DEFERRED with the reason."
    )


def test_the_deferred_list_does_not_rot(packed, shared):
    """The other direction: a rule that starts firing must leave the list, or
    `DEFERRED` slowly becomes a place where finished work hides."""
    fired: set[Rule] = set()
    for surah, ayah in SAMPLE:
        fired |= _fired(packed, shared, surah, ayah)
    stale = sorted(rule.value for rule in DEFERRED & fired)
    assert not stale, f"listed as deferred but firing: {stale}"


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_no_two_rules_claim_the_same_slot_and_aspect(packed, shared, surah, ayah):
    """E1, in the suite rather than only in a harness somebody remembers to run.

    It has caught three genuine overlaps so far, and each was fixed by making
    the conditions mutually exclusive rather than by ranking them. The next
    family to overlap should fail here, on the first test run, not on verse
    3,000 of a manual parity pass.
    """
    score = score_for(packed, shared, surah, ayah)
    try:
        perform(score, HAFS, all_join(len(score.words)))
        perform(
            score,
            HAFS,
            BoundaryPlan(
                (Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,)
            ),
        )
    except ConflictError as conflict:  # pragma: no cover - the failure path
        pytest.fail(f"{surah}:{ayah}: {conflict}")
