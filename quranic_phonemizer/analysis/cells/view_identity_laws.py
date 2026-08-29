"""Validate carrier identity and letter-weight placement in a cell view."""

from __future__ import annotations

from ...render.alphabet import is_long_a_token, is_short_a_token
from ..checks import requirer
from ..dtos import AnalysisBundle
from .dtos import CellRole, CellView
from .laws import CellValidationError
from .projection_semantics import is_carrier_identity_rule

_require = requirer(CellValidationError)
_WEIGHT = frozenset({"tafkheem", "tarqeeq"})


def check_carrier_identity_placement(view: CellView, bundle: AnalysisBundle) -> None:
    rules = {
        occurrence.id: occurrence.rule_id.value
        for occurrence in bundle.rule_occurrences
    }
    for word in view.words:
        for column in word.columns:
            pausal_alif = any(
                rules[occurrence] == "pausal_alif"
                for occurrence in column.rule_occurrence_ids
            )
            _require(
                not pausal_alif or (
                    column.role is CellRole.MADD and column.text.startswith("ا")
                ),
                "pausal-alif identity is not on its alif carrier",
            )
            if column.role is CellRole.HARAKA:
                _require(
                    not any(
                        is_carrier_identity_rule(rules[occurrence])
                        for occurrence in column.rule_occurrence_ids
                    ),
                    "a carrier identity labels its accompanying haraka",
                )


def _column_weight_shape(word, column, rules, sounds):
    occurrences = tuple(dict.fromkeys(
        occurrence for occurrence in column.rule_occurrence_ids
        if rules[occurrence] in _WEIGHT
    ))
    named = {rules[occurrence] for occurrence in occurrences}
    held = tuple(dict.fromkeys(
        (*column.owned_sound_ids, *column.presented_sound_ids)
    ))
    letter = (
        column.role is CellRole.LETTER
        and any(
            ("ر" in column.text and sounds[sound].token.startswith("r"))
            or ("ل" in column.text and sounds[sound].token.startswith("l"))
            for sound in column.owned_sound_ids
        )
        and column.silence is None
    )
    carrier_shape = (
        column.role in {CellRole.LETTER, CellRole.MADD}
        and (column.role is CellRole.MADD or any(c in column.text for c in "اىٰ"))
        and column.silence is None
    )
    owned_carrier = carrier_shape and any(
        is_long_a_token(sounds[sound].token) for sound in column.owned_sound_ids
    )
    presented_carrier = carrier_shape and any(
        is_long_a_token(sounds[sound].token) for sound in held
    )
    spelled_run = any(column.id in run.column_ids for run in word.runs)
    compact = (
        column.role is CellRole.LETTER
        and column.text == "ا"
        and len(column.owned_sound_ids) > 1
    )
    return named, held, letter, owned_carrier, presented_carrier, spelled_run, compact


def _check_weight_column(word, column, rules, sounds):
    named, held, letter, carrier, presented, spelled, compact = _column_weight_shape(
        word, column, rules, sounds
    )
    if column.role in {CellRole.HARAKA, CellRole.TANWEEN}:
        _require(not named, "a short-vowel cell has a weight label")
        return
    if letter or carrier:
        _require(
            len(named) == 1,
            "a pronounced raa, lam, or A carrier lacks one weight identity: "
            f"word={word.word_id.value} column={column.id.value} "
            f"text={column.text!r} role={column.role.value} "
            f"weights={sorted(named)} sounds={[item.value for item in held]}",
        )
    _require(
        "tarqeeq" not in named or letter or presented or spelled or compact,
        "tarqeeq labels something other than a pronounced raa, lam, "
        f"or long-A carrier: word={word.word_id.value} "
        f"column={column.id.value} text={column.text!r} role={column.role.value} "
        f"sounds={[(item.value, sounds[item].token) for item in held]}",
    )


def _check_boundary_weights(view, rules):
    for boundary in view.boundaries:
        for column in boundary.columns:
            named = {
                rules[occurrence] for occurrence in column.rule_occurrence_ids
                if rules[occurrence] in _WEIGHT
            }
            _require(
                not named,
                "a boundary haraka or sign has a weight label: "
                f"boundary={boundary.boundary_id.value} "
                f"column={column.id.value} text={column.text!r} "
                f"weights={sorted(named)}",
            )


def _all_cells(view):
    cells = [cell for word in view.words for cell in word.sounds]
    cells.extend(bridge.sound for word in view.words for bridge in word.bridges)
    for boundary in view.boundaries:
        cells.extend(boundary.sounds)
        cells.extend(bridge.sound for bridge in boundary.bridges)
    return cells


def check_weight_identity_placement(view: CellView, bundle: AnalysisBundle) -> None:
    """Require weight only on pronounced letters and long-A carriers."""
    rules = {item.id: item.rule_id.value for item in bundle.rule_occurrences}
    sounds = {sound.id: sound for sound in bundle.sounds}
    for word in view.words:
        for column in word.columns:
            _check_weight_column(word, column, rules, sounds)
    _check_boundary_weights(view, rules)
    for cell in _all_cells(view):
        named = {
            rules[occurrence] for occurrence in cell.rule_occurrence_ids
            if rules[occurrence] in _WEIGHT
        }
        token = sounds[cell.sound_id].token
        _require(
            not named or not is_short_a_token(token),
            "a short /a/ sound has a visible weight label: "
            f"sound={cell.sound_id.value} token={token!r} weights={sorted(named)}",
        )


__all__ = ["check_carrier_identity_placement", "check_weight_identity_placement"]
