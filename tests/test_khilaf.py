"""Both readings of the two bilabial hidings, and the hafs/riwayah overlay."""
from __future__ import annotations

import pytest

from conftest import score_for
from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import (
    KhilafId,
    Option,
    VariantSelection,
)
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.performance import Nasal, NasalPlace
from quranic_phonemizer.riwayat.hafs import HAFS, rule_tables
from quranic_phonemizer.rules.khilaf import KhilafError, nasal_place

#: 2:19 `مِّنَ ٱلصَّوَٰعِقِ` carries an iqlab site; 2:8 has the meem's.
SITES = {KhilafId.IQLAB_NASAL: (2, 19), KhilafId.IKHFAA_SHAFAWI_NASAL: (2, 8)}
RULE_OF = {
    KhilafId.IQLAB_NASAL: Rule.IQLAB,
    KhilafId.IKHFAA_SHAFAWI_NASAL: Rule.IKHFAA_SHAFAWI,
}


def _places(packed, hafs, khilaf, option: str | None) -> set[NasalPlace]:
    surah, ayah = SITES[khilaf]
    score = score_for(packed, hafs, surah, ayah)
    selection = (
        VariantSelection() if option is None
        else VariantSelection((Option(khilaf, option),))
    )
    score = type(score)(
        riwayah=score.riwayah, words=score.words,
        selection=selection, digest=score.digest,
    )
    performance = perform(score, HAFS, all_join(len(score.words)),
                          selection=selection)
    owned = {
        o.id for o in performance.occurrences if o.rule is RULE_OF[khilaf]
    }
    return {
        sound.place
        for _, sound in performance.sounds
        if isinstance(sound, Nasal)
    } if owned else set()


@pytest.mark.parametrize("khilaf", list(SITES))
def test_both_options_are_reachable(packed, hafs, khilaf) -> None:
    """A khilaf nothing reads is a khilaf that does not exist."""
    assert NasalPlace.BILABIAL in _places(packed, hafs, khilaf, "bilabial")
    assert NasalPlace.ASSIMILATED in _places(
        packed, hafs, khilaf, "assimilated"
    )


@pytest.mark.parametrize("khilaf", list(SITES))
def test_the_default_is_taken_when_nothing_is_chosen(packed, hafs, khilaf) -> None:
    assert NasalPlace.ASSIMILATED in _places(packed, hafs, khilaf, None)


def test_an_unknown_option_raises_rather_than_falling_back() -> None:
    selection = VariantSelection((Option(KhilafId.IQLAB_NASAL, "nasal-ish"),))
    with pytest.raises(KhilafError, match="not an option"):
        nasal_place(selection, KhilafId.IQLAB_NASAL)


def test_the_shared_tables_load_for_every_letter() -> None:
    """The tables are keyed by Arabic letter, so a missing glyph is a load
    error rather than a rule that quietly never fires."""
    tables = rule_tables()
    assert len(tables.qalqala) == 5
    assert len(tables.always_heavy) == 7
    assert tables.never_follows
    assert tables.pairs.of(*next(iter(tables.pairs.by_pair)))


def test_the_riwayah_inherits_what_it_does_not_override() -> None:
    """Hafs overrides nothing today, so it must read the shared file whole."""
    from pathlib import Path

    from quranic_phonemizer.riwayat.tables import load_rule_tables

    shared = (
        Path(__file__).resolve().parent.parent
        / "quranic_phonemizer" / "data" / "shared"
    )
    bare = load_rule_tables(shared / "rules.yaml")
    assert bare.qalqala == rule_tables().qalqala
    assert bare.pairs.by_pair == rule_tables().pairs.by_pair
