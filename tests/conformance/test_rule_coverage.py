"""Every declared rule must actually fire, and no two rules may collide.

Runs over the real `HAFS` ruleset rather than a single-rule set, since both
checks depend on the full rule interaction.
"""
from __future__ import annotations

import pytest

from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.plan import ConflictError
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction, Riwayah
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.definitions import (
    RULE_DEFINITIONS,
    SILENCE_DEFINITIONS,
)
from quranic_phonemizer.phonemize.names import tajweed_rules
from quranic_phonemizer.riwayat import ruleset_for
from quranic_phonemizer.riwayat.hafs import HAFS

from conftest import score_for

#: Chosen to reach every implemented rule; the named ones are the only known
#: site for some rule families.
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
    (46, 4),    # ٱئْتُونِى — ibdāl, a quiescent hamza after a prosthetic one
]

#: Plus a broad sweep for the common families: noon and meem in all their
#: outcomes, the article lam, qalqala, emphasis, waqf.
SAMPLE = (
    [(1, n) for n in range(1, 8)]
    + [(2, n) for n in range(1, 26)]
    + [(112, n) for n in range(1, 5)]
    + [(114, n) for n in range(1, 7)]
    + SITES
)

#: Rules declared absent, each with a reason. Every member of `Rule` must be
#: produced by some classifier in the corpus; a member here needs a reason,
#: and `test_the_deferred_list_does_not_rot` fails once the reason no longer
#: holds.
#:
#: `naql` is Warsh-only: no Hafs classifier emits it, and
#: `test_naql_is_warsh_bound_and_fires` asserts the Warsh side.
DEFERRED: set[Rule] = {Rule.NAQL, Rule.MADD_LEEN_MAHMUZ}


def _fired(packed, hafs, surah, ayah):
    score = score_for(packed, hafs, surah, ayah)
    out = set()
    for junction in (Junction.JOIN, Junction.STOP):
        plan = BoundaryPlan(
            (junction,) * (len(score.words) - 1) + (Junction.EDGE,)
        )
        out |= {o.rule for o in perform(score, HAFS, plan).occurrences}
    return out


def test_every_rule_not_declared_deferred_actually_fires(packed, hafs):
    """Falsifier: a `Rule` member with no classifier. Add one without an
    implementation and this fails."""
    fired: set[Rule] = set()
    for surah, ayah in SAMPLE:
        fired |= _fired(packed, hafs, surah, ayah)
    expected = set(Rule) - DEFERRED
    missing = sorted(rule.value for rule in expected - fired)
    assert not missing, (
        f"declared but never produced: {missing}. Either implement the rule, "
        f"or add it to DEFERRED with the reason."
    )


def test_the_deferred_list_does_not_rot(packed, hafs):
    """The other direction: a rule that starts firing must leave the list, or
    `DEFERRED` slowly becomes a place where finished work hides."""
    fired: set[Rule] = set()
    for surah, ayah in SAMPLE:
        fired |= _fired(packed, hafs, surah, ayah)
    stale = sorted(rule.value for rule in DEFERRED & fired)
    assert not stale, f"listed as deferred but firing: {stale}"


def test_naql_is_warsh_bound_and_fires():
    """The one Warsh-only rule: absent from the Hafs catalogue, present in
    the Warsh one, and actually produced by the Warsh ruleset."""
    from quranic_phonemizer.api import recitation
    from quranic_phonemizer.model.address import Script, VerseRef
    from quranic_phonemizer.riwayat.warsh.rules import WARSH

    assert Rule.NAQL in WARSH.emitted()
    assert Rule.NAQL not in ruleset_for(Riwayah.HAFS).emitted()

    package = recitation(Riwayah.WARSH)
    verse = VerseRef(23, 1)
    words = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, words))
    plan = all_join(len(words))
    fired = {o.rule for o in perform(built.score, WARSH, plan).occurrences}
    assert Rule.NAQL in fired
    assert fired <= WARSH.emitted()


def test_leen_mahmuz_is_warsh_bound_and_fires():
    from quranic_phonemizer.api import recitation
    from quranic_phonemizer.model.address import Script, VerseRef
    from quranic_phonemizer.riwayat.warsh.rules import WARSH

    assert Rule.MADD_LEEN_MAHMUZ in WARSH.emitted()
    assert Rule.MADD_LEEN_MAHMUZ not in ruleset_for(Riwayah.HAFS).emitted()

    package = recitation(Riwayah.WARSH)
    verse = VerseRef(3, 49)
    words = package.words(verse)
    built = package.build(package.read(Script.UTHMANI, verse, words))
    fired = {
        occurrence.rule
        for occurrence in perform(
            built.score, WARSH, all_join(len(built.score.words))
        ).occurrences
    }
    assert Rule.MADD_LEEN_MAHMUZ in fired


@pytest.mark.parametrize("riwayah", list(Riwayah))
def test_nominal_rule_is_declared_emitted(riwayah):
    """A classifier whose nominal `rule` is a `Rule` must list it in `emits`;
    the nominal identifier is what dispatch and displays lean on."""
    for classifiers in ruleset_for(riwayah).phases.values():
        for classifier in classifiers:
            if isinstance(classifier.rule, Rule):
                assert classifier.rule in classifier.emits, type(classifier)


@pytest.mark.parametrize("riwayah", list(Riwayah))
def test_tajweed_rules_is_the_emitted_union_plus_silences(riwayah):
    """The public catalogue is derived from the bound classifiers' declared
    sets: a rule no classifier declares is absent, silences always show."""
    published = {row[0] for row in tajweed_rules(riwayah.value)}
    emitted = {rule.value for rule in ruleset_for(riwayah).emitted()}
    silences = {identifier.value for identifier in SILENCE_DEFINITIONS}
    assert published == emitted | silences
    assert emitted <= {identifier.value for identifier in RULE_DEFINITIONS}


def test_fired_rules_stay_inside_the_declared_sets(packed, hafs):
    """Falsifier: a classifier producing a rule it does not declare."""
    fired: set[Rule] = set()
    for surah, ayah in SAMPLE:
        fired |= _fired(packed, hafs, surah, ayah)
    undeclared = sorted(rule.value for rule in fired - HAFS.emitted())
    assert not undeclared, f"produced but not declared: {undeclared}"


@pytest.mark.parametrize(("surah", "ayah"), SAMPLE)
def test_no_two_rules_claim_the_same_slot_and_aspect(packed, hafs, surah, ayah):
    """No two rules may claim the same slot and aspect; overlaps must be
    resolved by mutually exclusive conditions, not by ranking.
    """
    score = score_for(packed, hafs, surah, ayah)
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
