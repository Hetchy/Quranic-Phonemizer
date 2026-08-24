"""The model vocabulary is closed: every referenced name is defined.

Falsified by any type needing a field not already in the vocabulary, or
any referenced name left undefined.
"""
from __future__ import annotations

import dataclasses
import importlib
import inspect

import pytest

from conftest import performance_for
from quranic_phonemizer.model import address, canon, inscription, performance
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.performance import Classifies, Recolours, SetsLength

MODULES = (address, canon, inscription, performance)


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_every_model_dataclass_is_frozen_and_slotted(module) -> None:
    """The `Plan` is the only append-only structure, and it lives outside
    `model/`."""
    for name, obj in vars(module).items():
        if not inspect.isclass(obj) or not dataclasses.is_dataclass(obj):
            continue
        if obj.__module__ != module.__name__:
            continue
        params = obj.__dataclass_params__
        assert params.frozen, f"{module.__name__}.{name} is not frozen"
        assert getattr(obj, "__slots__", None) is not None, (
            f"{module.__name__}.{name} has no __slots__"
        )


def test_canon_letter_has_thirty_members() -> None:
    """The 28 letters, plus HAMZA and TAA_MARBUTA; not ALEF_WASLA (an onset)
    or ALIF_MAQSURA (a glyph)."""
    assert len(canon.CanonLetter) == 30
    names = {m.name for m in canon.CanonLetter}
    assert "ALEF_WASLA" not in names and "ALIF_MAQSURA" not in names
    assert {"HAMZA", "TAA_MARBUTA"} <= names


def test_closed_sets_have_the_sizes_their_arguments_depend_on() -> None:
    assert len(canon.Onset) == 5
    assert len(performance.Aspect) == 2, (
        "Aspect is the slot's own field partition; a third member would mean "
        "the slot gained a third field"
    )


def test_classification_only_rules_are_rules() -> None:
    assert canon.CLASSIFICATION_ONLY <= set(canon.Rule)


def test_classification_only_excludes_rules_with_a_real_effect() -> None:
    """A rule that emits its own `Recolour`/`Relength`/`Realize` earns a
    `Recolours`/`SetsLength`/`Hosts` edge from that effect, not a
    `Classifies` one, so it does not need the exemption."""
    assert not canon.CLASSIFICATION_ONLY & {
        Rule.TAFKHEEM, Rule.MADD_TABII, Rule.ILTIQA_SHORTENING, Rule.PAUSAL_ALIF,
    }


def test_sound_union_has_the_three_variants() -> None:
    """The standalone `Nasal` sound is gone: a hum is a `Consonant` with
    `ghunnah`, riding the letter the rule mints rather than a place field."""
    from typing import get_args

    members = {cls.__name__ for cls in get_args(performance.Sound)}
    assert members == {"Consonant", "Vowel", "Release"}
    assert {f.name for f in dataclasses.fields(performance.Consonant)} == {
        "letter", "geminate", "emphatic", "ghunnah", "eased",
    }
    assert {f.name for f in dataclasses.fields(performance.Release)} == {
        "degree",
    }


def test_modifier_union_has_the_three_variants() -> None:
    from typing import get_args

    members = {cls.__name__ for cls in get_args(performance.Modifier)}
    assert members == {"Recolours", "SetsLength", "Classifies"}


def test_a_recolour_and_a_relength_each_retain_one_edge(packed, hafs) -> None:
    """`تَفْخِيم` reverting to a discarded feature, or a relength reverting to
    a discarded length, both leave the modifier they earned unfindable."""
    _, tafkheem_performance = performance_for(packed, hafs, 1, 1)
    tafkheem = [
        o for o in tafkheem_performance.occurrences if o.rule is Rule.TAFKHEEM
    ]
    assert tafkheem
    recoloured = {
        m.by for m in tafkheem_performance.modifiers if isinstance(m, Recolours)
    }
    assert all(o.id in recoloured for o in tafkheem)

    _, alif_performance = performance_for(packed, hafs, 2, 258)
    pausal = [
        o for o in alif_performance.occurrences if o.rule is Rule.PAUSAL_ALIF
    ]
    assert pausal
    lengthened = {
        m.by for m in alif_performance.modifiers if isinstance(m, SetsLength)
    }
    assert all(o.id in lengthened for o in pausal)


def test_madd_leen_classifies_the_consonant_it_names(packed, hafs) -> None:
    """The waw or yaa `madd_leen` names has no vowel; the edge must land on
    its consonant or the classification-only rule owns nothing at all."""
    _, leen_performance = performance_for(packed, hafs, 106, 1)
    leen = [
        o for o in leen_performance.occurrences if o.rule is Rule.MADD_LEEN
    ]
    assert leen
    classified = {
        m.by for m in leen_performance.modifiers if isinstance(m, Classifies)
    }
    assert all(o.id in classified for o in leen)


def test_deleted_names_stay_deleted() -> None:
    """Each name here must stay undefined on its module."""
    for module, name in (
        (canon, "Nunated"),
        (canon, "Colouring"),
        (canon, "Condition"),
        (canon, "SPELLING_EXPANSION"),
        (canon, "NucleusKind"),
        (canon, "Silent"),
        (canon, "Short"),
        (canon, "Long"),
        (canon, "Silah"),
        (canon, "PausalLong"),
        (canon, "SILENT"),
        (performance, "Attach"),
        (performance, "Participants"),
        (performance, "SilenceReason"),
        (performance, "Nasal"),
        (performance, "NasalPlace"),
        (performance, "ReleaseKind"),
        (inscription, "Inert"),
        (inscription, "SpellKind"),
        (inscription, "RuleTag"),
    ):
        assert not hasattr(module, name), (
            f"{module.__name__}.{name} is back; it was deleted with an argument"
        )
    assert not hasattr(canon.Rule, "SPELLING_EXPANSION")
    assert not hasattr(canon.Onset, "COLOUR")
    for renamed in (
        "FAKK_IDGHAM",
        "IKHFAA_HAQIQI",
        "ILTIQA_FATHA",
        "ILTIQA_KASRA",
        "IWAD",
        "MADD_ARID_LIL_SUKUN",
        "MADD_JAIZ_MUNFASIL",
        "MADD_WAJIB_MUTTASIL",
        "PAUSAL_SUKUN",
        "TAA_MARBUTA_PAUSAL",
        "WASL_ELISION",
        "WASL_START",
    ):
        assert not hasattr(canon.Rule, renamed), (
            f"Rule.{renamed} is back; the identifier it was renamed to is the "
            f"only one"
        )


def test_the_teaching_labels_module_stays_deleted() -> None:
    """Badal and silah are occurrences a rule minted, so nothing derives
    them from an assembled madd afterwards."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("quranic_phonemizer.phonemize.labels")


def test_slot_origin_meets_the_conditions_that_let_it_return() -> None:
    """`SlotOrigin` must be script-independent: no member may encode which
    script produced it. Its two real consumers are the muqattaat toggle and
    waqf, which tells `هُدًى` from `مِن` by nothing else.
    """
    members = {member.value for member in canon.SlotOrigin}
    assert members == {"written", "spelled", "nunation"}
    assert not hasattr(canon.SlotOrigin, "LEXICAL"), (
        "LEXICAL was the script-relative member: it meant 'some script writes "
        "a base letter for it', a quantifier canon.build cannot evaluate"
    )
    slot = canon.Slot(
        id=None, letter=canon.CanonLetter.NOON, onset=canon.Onset.PLAIN,
        nucleus=canon.Nucleus.silent(), origin=canon.SlotOrigin.SPELLED,
    )
    assert slot.spelled, "the old flag stays readable through the enum"


def test_nucleus_union_covers_the_conditionality_table() -> None:
    """Conditionality lives in the canonical vocabulary, in exactly one
    place: the joined and stopped readings of one `Nucleus`."""
    forms = {member.value for member in canon.VowelForm}
    assert forms == {"absent", "short", "long"}
    silent = canon.Nucleus.silent()
    short = canon.Nucleus.short(canon.Quality.A)
    long = canon.Nucleus.long(canon.Quality.A)
    silah = canon.Nucleus.joined_only_long(canon.Quality.A)
    pausal_long = canon.Nucleus.pausal_long(canon.Quality.A)
    assert (silent.is_silent, short.is_short, long.is_long) == (True, True, True)
    assert (silah.is_joined_only_long, pausal_long.is_pausal_long) == (True, True)
    assert canon.Onset.WASL and canon.Onset.GLIDE, "the two mirrors"


def test_spelling_union_has_the_four_members() -> None:
    from typing import get_args

    members = {cls.__name__ for cls in get_args(inscription.Spelling)}
    assert members == {"Evidences", "Attests", "Decorates", "Structural"}


def test_attribution_union_has_the_four_variants() -> None:
    from typing import get_args

    members = {cls.__name__ for cls in get_args(performance.Attribution)}
    assert members == {"Hosts", "Inserted", "MergedInto", "Silent"}


def test_decorates_requires_a_slot() -> None:
    """A maddah grapheme supplies nothing yet must still point at a slot."""
    fields = {f.name for f in dataclasses.fields(inscription.Decorates)}
    assert fields == {"grapheme", "slot"}
    with pytest.raises(TypeError):
        inscription.Decorates(grapheme=None)  # type: ignore[call-arg]


def test_a_merger_names_the_rule_that_made_it() -> None:
    """A merger is the pair sharing a sound and a rule, so its `by` is not
    optional. A hosted or silenced part may have had no rule at all."""
    from typing import get_type_hints

    from quranic_phonemizer.phonemize import edges as ed

    assert get_type_hints(performance.MergedInto)["by"] is address.OccurrenceId
    assert get_type_hints(performance.Hosts)["by"] == address.OccurrenceId | None
    assert get_type_hints(ed.MergedInto)["by"] is int
    assert get_type_hints(ed.Hosts)["by"] == int | None
