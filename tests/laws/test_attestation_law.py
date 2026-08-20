"""A shadda the script writes must be produced by some occurrence.

The full-corpus residue is a ratchet in CI; these are the sites that were
silently unmet because a rule was never reached.
"""
from __future__ import annotations

import dataclasses

import pytest

from conftest import built_for
from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.laws import check_attestations
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.inscription import Attests
from quranic_phonemizer.model.performance import Hosts, MergedInto
from quranic_phonemizer.riwayat.hafs import HAFS

#: Cross-word idgham mutamathilayn on letters outside the pair table.
MERGERS = [(17, 33), (18, 78), (18, 82), (2, 137)]


def _performed(packed, hafs, surah: int, ayah: int):
    built = built_for(packed, hafs, surah, ayah)
    score = built.score
    plan = all_join(len(score.words))
    attested = [
        s.anchor for s in built.inscription.spellings if isinstance(s, Attests)
    ]
    return attested, perform(score, HAFS, plan), plan


@pytest.mark.parametrize("surah,ayah", MERGERS)
def test_a_written_shadda_is_accounted_for(packed, hafs, surah, ayah) -> None:
    attested, performance, _ = _performed(packed, hafs, surah, ayah)
    assert not check_attestations(attested, performance)


@pytest.mark.parametrize("surah,ayah", MERGERS)
def test_like_into_like_fires_at_these_sites(packed, hafs, surah, ayah) -> None:
    """Every letter can repeat, so the rule cannot key on a pair table."""
    _, performance, _ = _performed(packed, hafs, surah, ayah)
    fired = {o.rule for o in performance.occurrences}
    assert Rule.IDGHAM_MUTAMATHILAYN in fired


def test_a_merger_that_stops_naming_its_host_leaves_the_shadda_unmet(
    packed, hafs
) -> None:
    """The law is falsifiable. A merger names the unit it produced through
    the edge that hosts the shared sound; take that occurrence off the edge
    and the shadda witnessing the pair is accounted for by nothing."""
    attested, performance, _ = _performed(packed, hafs, 17, 33)
    assert not check_attestations(attested, performance)

    merges = [a for a in performance.attributions if isinstance(a, MergedInto)]
    host = next(
        h for h in performance.attributions
        if isinstance(h, Hosts) and h.slots[0] in attested
        and any(h.sound == m.sound and h.by == m.by for m in merges)
    )
    stripped = dataclasses.replace(
        performance,
        attributions=tuple(
            dataclasses.replace(a, by=None) if a is host else a
            for a in performance.attributions
        ),
    )

    problems = check_attestations(attested, stripped)
    assert len(problems) == 1 and str(host.slots[0]) in problems[0]
