"""02-gate section 5: canonical JSON, and the shape it must reject.

Every tagged union carries `kind`, the producing type's name lowercased.
Holds no phoneme string: a token is an opaque string here, never composed.
"""
from __future__ import annotations

import json

from .document import PhonemizeResult
from .pairing import Pairing


class SchemaError(ValueError):
    """A canonical document, or a fragment of one, that the schema rejects."""


# --------------------------------------------------------------- serializing

def to_canonical(result: PhonemizeResult) -> dict:
    """The whole document, ready for `json.dumps`. Field order does not
    matter for correctness; `canonical_bytes` sorts keys for stability."""
    return {
        "schema_version": result.schema_version,
        "ref": result.ref,
        "riwayah": result.riwayah,
        "script": result.script,
        "variant": result.variant,
        "extra_phonemes": sorted(result.extra_phonemes),
        "canon_digest": result.canon_digest,
        "words": [_word(w) for w in result.words],
        "glyphs": [_glyph(g) for g in result.glyphs],
        "rendered": [_render_glyph(g) for g in result.rendered],
        "units": [_unit(u) for u in result.units],
        "sounds": [_sound(s) for s in result.sounds],
        "rules": [_rule_instance(r) for r in result.rules],
        "spellings": [_spelling(e) for e in result.spellings],
        "attributions": [_attribution(e) for e in result.attributions],
        "modifiers": [_modifier(e) for e in result.modifiers],
    }


def canonical_bytes(result: PhonemizeResult) -> bytes:
    return json.dumps(
        to_canonical(result), sort_keys=True, ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _word(w) -> dict:
    return {
        "location": str(w.location), "text": w.text,
        "is_started_on": w.is_started_on, "is_stopped_on": w.is_stopped_on,
        "sakt_after": w.sakt_after,
        "stop_sign": w.stop_sign.value if w.stop_sign else None,
    }


def _vowel_state(form, quality) -> dict:
    out = {"kind": form.value}
    if form.value != "absent":
        out["quality"] = quality.value if quality else None
    return out


def _unit(u) -> dict:
    vowel = u.vowel
    return {
        "word": u.word, "letter": u.letter.value,
        "consonant": {"geminate": u.consonant.geminate, "sounds": u.consonant.sounds.value},
        "vowel": {
            "joined": _vowel_state(vowel.joined.form, vowel.joined.quality),
            "stopped": _vowel_state(vowel.stopped.form, vowel.stopped.quality),
        },
        "origin": u.origin.value,
    }


def _glyph(g) -> dict:
    return {
        "word": g.word, "char": g.char, "kind": g.kind.value,
        "word_index": g.word_index, "source_index": g.source_index,
    }


def _render_glyph(g) -> dict:
    return {**_glyph(g), "from_glyphs": list(g.from_glyphs)}


def _sound(s) -> dict:
    out = {"token": s.token, "kind": s.kind.value}
    if s.kind.value == "consonant":
        out.update(letter=s.letter.value, geminate=s.geminate,
                    emphatic=s.emphatic, ghunnah=s.ghunnah, eased=s.eased)
    elif s.kind.value == "vowel":
        out.update(quality=s.quality.value, long=s.long, emphatic=s.emphatic)
    else:
        out.update(degree=s.degree.value)
    return out


def _rule_instance(r) -> dict:
    return {
        "rule": r.rule.value, "source": r.source, "host": r.host,
        "labels": list(r.labels),
    }


def _spelling(e) -> dict:
    kind = type(e).__name__.lower()
    out = {"kind": kind, "glyph": e.glyph}
    if kind != "structural":
        out["unit"] = e.unit
    if kind == "supplies":
        out["fact"] = e.fact.value
    return out


def _attribution(e) -> dict:
    kind = type(e).__name__.lower()
    out = {"kind": kind, "unit": e.unit, "part": e.part.value, "by": e.by}
    if kind != "silent":
        out["sound"] = e.sound
    return out


def _modifier(e) -> dict:
    kind = type(e).__name__.lower()
    out = {"kind": kind, "sound": e.sound, "by": e.by}
    if kind == "setslength":
        out["length"] = e.length.value
    return out


def to_pairing(p: Pairing) -> dict:
    return {
        "glyphs": list(p.glyphs), "sounds": list(p.sounds),
        "shares": list(p.shares), "silent": list(p.silent),
        "rules": list(p.rules), "after": p.after,
    }


__all__ = [
    "SchemaError",
    "canonical_bytes",
    "to_canonical",
    "to_pairing",
]
