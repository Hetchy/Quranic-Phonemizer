"""Emit a self-describing JSON Schema from the dataclass field types.

An id field carries `x-ref` naming the record it points at and a record with an
id carries `x-record`, so a checker can close every reference.
"""
from __future__ import annotations

import dataclasses
import types
import typing
from enum import Enum

DRAFT = "https://json-schema.org/draft/2020-12/schema"

_SCALAR = {int: "integer", str: "string", bool: "boolean", type(None): "null"}


def _is_id_type(tp: object) -> bool:
    if not (isinstance(tp, type) and dataclasses.is_dataclass(tp)):
        return False
    hints = typing.get_type_hints(tp)
    return list(hints) == ["value"] and hints["value"] in (int, str)


def _has_id(tp: type) -> bool:
    return "id" in typing.get_type_hints(tp) and _is_id_type(
        typing.get_type_hints(tp)["id"]
    )


def id_record_map(roots: tuple[type, ...]) -> dict[type, str]:
    """Map each id type to the record that owns it as its `id`, over every
    record reachable from the given roots."""
    found: dict[type, str] = {}
    seen: set[type] = set()

    def visit(tp: object) -> None:
        for arg in typing.get_args(tp):
            visit(arg)
        if not (isinstance(tp, type) and dataclasses.is_dataclass(tp)):
            return
        if _is_id_type(tp) or tp in seen:
            return
        seen.add(tp)
        hints = typing.get_type_hints(tp)
        if _has_id(tp):
            found[hints["id"]] = tp.__name__
        for hint in hints.values():
            visit(hint)

    for root in roots:
        visit(root)
    return found


def _wire(name: str) -> str:
    return name.lstrip("_")


def json_schema(root: type, id_map: dict[type, str]) -> dict:
    defs: dict[str, dict] = {}
    body = _schema(root, id_map, defs)
    return {"$schema": DRAFT, **body, "$defs": defs}


def _schema(tp: object, id_map: dict[type, str], defs: dict[str, dict]) -> dict:
    if _is_id_type(tp):
        node = {"type": _SCALAR[typing.get_type_hints(tp)["value"]]}
        if tp in id_map:
            node["x-ref"] = id_map[tp]
        return node
    if isinstance(tp, type) and issubclass(tp, Enum):
        return {"type": "string", "enum": [member.value for member in tp]}
    if isinstance(tp, type) and dataclasses.is_dataclass(tp):
        return _record(tp, id_map, defs)
    if tp in _SCALAR:
        return {"type": _SCALAR[tp]}
    if tp is dict:
        return {"type": "object"}
    return _generic(tp, id_map, defs)


def _generic(tp: object, id_map: dict[type, str], defs: dict[str, dict]) -> dict:
    origin, args = typing.get_origin(tp), typing.get_args(tp)
    if origin in (typing.Union, types.UnionType):
        return {"anyOf": [_schema(arg, id_map, defs) for arg in args]}
    if origin in (frozenset, set):
        return {"type": "array", "items": _schema(args[0], id_map, defs),
                "uniqueItems": True}
    if origin in (tuple, list):
        if origin is tuple and not (len(args) == 2 and args[1] is Ellipsis):
            items = [_schema(arg, id_map, defs) for arg in args]
            return {"type": "array", "prefixItems": items,
                    "minItems": len(items), "maxItems": len(items)}
        return {"type": "array", "items": _schema(args[0], id_map, defs)}
    raise TypeError(f"cannot reflect {tp!r}")


def _record(tp: type, id_map: dict[type, str], defs: dict[str, dict]) -> dict:
    name = tp.__name__
    if name not in defs:
        defs[name] = {}
        hints = typing.get_type_hints(tp)
        properties = {
            _wire(field.name): _schema(hints[field.name], id_map, defs)
            for field in dataclasses.fields(tp)
        }
        node = {
            "type": "object",
            "properties": properties,
            "required": sorted(properties),
            "additionalProperties": False,
        }
        if _has_id(tp):
            node["x-record"] = name
        defs[name] = node
    return {"$ref": f"#/$defs/{name}"}


__all__ = ["DRAFT", "id_record_map", "json_schema"]
