"""Phase 0's gate: the vocabulary is closed and every referenced name defined.

Falsified by any type needing a field no ADR names, or any referenced name
still undefined (ADR-008 §5).
"""
from __future__ import annotations

import dataclasses
import inspect

import pytest

from quranic_phonemizer.model import address, canon, inscription, performance

MODULES = (address, canon, inscription, performance)


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_every_model_dataclass_is_frozen_and_slotted(module) -> None:
    """ADR-007 §4.6. The `Plan` is the only append-only structure and it is
    not in `model/`."""
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
    """The 28 letters, plus HAMZA, plus TAA_MARBUTA — and no ALEF_WASLA
    (an onset) and no ALIF_MAQSURA (a glyph)."""
    assert len(canon.CanonLetter) == 30
    names = {m.name for m in canon.CanonLetter}
    assert "ALEF_WASLA" not in names and "ALIF_MAQSURA" not in names
    assert {"HAMZA", "TAA_MARBUTA"} <= names


def test_closed_sets_have_the_sizes_their_arguments_depend_on() -> None:
    assert len(canon.Onset) == 5
    assert len(canon.Phase) == 5
    assert len(performance.Aspect) == 2, (
        "Aspect is the slot's own field partition; a third member would mean "
        "the slot gained a third field (ADR-002 §2)"
    )
    assert len(canon.RuleFamily) == 6


def test_every_rule_declares_a_family() -> None:
    missing = sorted(r.value for r in canon.Rule if r not in canon.FAMILY_OF)
    assert not missing, f"Rule members with no RuleFamily: {missing}"
    extra = sorted(r for r in canon.FAMILY_OF if r not in set(canon.Rule))
    assert not extra, f"FAMILY_OF names non-rules: {extra}"


def test_classification_only_rules_are_rules() -> None:
    assert canon.CLASSIFICATION_ONLY <= set(canon.Rule)


def test_deleted_names_stay_deleted() -> None:
    """Each of these was removed for a recorded reason; re-adding one silently
    would undo the argument that removed it."""
    for module, name in (
        (canon, "Nunated"),
        (canon, "Colouring"),
        (canon, "Condition"),
        (canon, "SPELLING_EXPANSION"),
        (performance, "Attach"),
        (performance, "SilenceReason"),
        (inscription, "Inert"),
        (inscription, "SpellKind"),
        (inscription, "RuleTag"),
    ):
        assert not hasattr(module, name), (
            f"{module.__name__}.{name} is back; it was deleted with an argument"
        )
    assert not hasattr(canon.Rule, "SPELLING_EXPANSION")
    assert not hasattr(canon.Onset, "COLOUR")


def test_slot_origin_meets_the_conditions_that_let_it_return() -> None:
    """ADR-001 §3.2 deleted an earlier `SlotOrigin` and set two conditions for
    reinstating one: a **script-independent definition** and a **real
    consumer**. Both now hold, so the guard tests the conditions rather than
    the absence.

    The definition names the producing module, which is shared code, so no
    member can encode which script was read — that was the fatal property of
    the version that was deleted. And there are two consumers: the muqaṭṭaʿāt
    toggle, and waqf, which must tell `هُدًى` from `مِن` and has nothing else
    to tell them apart with.
    """
    members = {member.value for member in canon.SlotOrigin}
    assert members == {"written", "spelled", "nunation"}
    assert not hasattr(canon.SlotOrigin, "LEXICAL"), (
        "LEXICAL was the script-relative member: it meant 'some script writes "
        "a base letter for it', a quantifier canon.build cannot evaluate"
    )
    slot = canon.Slot(
        id=None, letter=canon.CanonLetter.NOON, onset=canon.Onset.PLAIN,
        nucleus=canon.SILENT, origin=canon.SlotOrigin.SPELLED,
    )
    assert slot.spelled, "the old flag stays readable through the enum"


def test_nucleus_union_covers_the_conditionality_table() -> None:
    """ADR-001 §3.6: conditionality lives in the canonical vocabulary, in
    exactly one place."""
    kinds = {member.value for member in canon.NucleusKind}
    assert kinds == {"silent", "short", "long", "silah", "pausal_long"}
    assert canon.Onset.WASL and canon.Onset.SILAH, "the two mirrors"


def test_spelling_union_has_the_four_members() -> None:
    from typing import get_args

    members = {cls.__name__ for cls in get_args(inscription.Spelling)}
    assert members == {"Evidences", "Attests", "Decorates", "Structural"}


def test_attribution_union_has_the_four_variants() -> None:
    from typing import get_args

    members = {cls.__name__ for cls in get_args(performance.Attribution)}
    assert members == {"Hosts", "Inserted", "MergedInto", "Silent"}


def test_decorates_requires_a_slot() -> None:
    """The whole point of the rename: `Inert` let a grapheme name nothing,
    and the maddah is a grapheme that supplies nothing yet shows something."""
    fields = {f.name for f in dataclasses.fields(inscription.Decorates)}
    assert fields == {"grapheme", "slot"}
    with pytest.raises(TypeError):
        inscription.Decorates(grapheme=None)  # type: ignore[call-arg]
