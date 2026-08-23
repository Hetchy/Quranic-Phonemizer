"""Validate a serialized document against its schema and close its references.

The reference pass reads the schema's `x-record` and `x-ref` marks to prove
every id points at a record present in the same set of documents.
"""
from __future__ import annotations

from .serialize import Json

_TYPE = {
    "integer": int, "string": str, "number": (int, float),
    "object": dict, "array": list, "boolean": bool, "null": type(None),
}


def _resolve(schema: dict, root: dict) -> dict:
    while "$ref" in schema:
        schema = root["$defs"][schema["$ref"].split("/")[-1]]
    return schema


def _type_ok(name: str, value: Json) -> bool:
    if name == "integer" and isinstance(value, bool):
        return False
    return isinstance(value, _TYPE[name])


def validation_errors(schema: dict, value: Json) -> list[str]:
    return _validate(schema, value, schema, "$")


def _validate(schema: dict, value: Json, root: dict, path: str) -> list[str]:
    schema = _resolve(schema, root)
    if "anyOf" in schema:
        if any(not _validate(s, value, root, path) for s in schema["anyOf"]):
            return []
        return [f"{path}: matches no branch"]
    out: list[str] = []
    if "const" in schema and value != schema["const"]:
        out.append(f"{path}: {value!r} is not const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        out.append(f"{path}: {value!r} not in enum")
    kind = schema.get("type")
    if kind and not _type_ok(kind, value):
        return out + [f"{path}: {value!r} is not {kind}"]
    if kind == "object":
        out += _object(schema, value, root, path)
    elif kind == "array":
        out += _array(schema, value, root, path)
    return out


def _object(schema: dict, value: dict, root: dict, path: str) -> list[str]:
    out: list[str] = []
    properties = schema.get("properties", {})
    for name in schema.get("required", ()):
        if name not in value:
            out.append(f"{path}.{name}: required but missing")
    if schema.get("additionalProperties") is False:
        out += [f"{path}.{k}: not permitted" for k in value if k not in properties]
    for name, sub in properties.items():
        if name in value:
            out += _validate(sub, value[name], root, f"{path}.{name}")
    return out


def _array(schema: dict, value: list, root: dict, path: str) -> list[str]:
    out: list[str] = []
    for index, sub in enumerate(schema.get("prefixItems", ())):
        if index < len(value):
            out += _validate(sub, value[index], root, f"{path}[{index}]")
    if "items" in schema:
        for index, item in enumerate(value):
            out += _validate(schema["items"], item, root, f"{path}[{index}]")
    return out


def _match(value: Json, options: list[dict], root: dict) -> dict | None:
    for option in options:
        resolved = _resolve(option, root)
        kind = resolved.get("type")
        if value is None and kind == "null":
            return resolved
        if isinstance(value, int) and not isinstance(value, bool) and (
            kind == "integer" or "x-ref" in resolved
        ):
            return resolved
        if isinstance(value, str) and kind in ("string", None):
            return resolved
    return None


def _collect(
    value: Json, schema: dict, root: dict,
    index: dict[str, set], refs: list[tuple[str, Json]],
) -> None:
    schema = _resolve(schema, root)
    if "anyOf" in schema:
        branch = _match(value, schema["anyOf"], root)
        if branch is not None:
            _collect(value, branch, root, index, refs)
        return
    ref = schema.get("x-ref")
    if ref is not None and value is not None:
        refs.append((ref, value))
        return
    if isinstance(value, dict):
        record = schema.get("x-record")
        if record is not None and "id" in value:
            index.setdefault(record, set()).add(value["id"])
        for name, sub in schema.get("properties", {}).items():
            if name in value:
                _collect(value[name], sub, root, index, refs)
    elif isinstance(value, list) and "items" in schema:
        for item in value:
            _collect(item, schema["items"], root, index, refs)


def closed_reference_errors(schema: dict, value: Json) -> list[str]:
    """Every id whose target record appears in this document resolves to it."""
    index: dict[str, set] = {}
    refs: list[tuple[str, Json]] = []
    _collect(value, schema, schema, index, refs)
    return [
        f"{target} {ref!r} does not resolve"
        for target, ref in refs
        if target in index and ref not in index[target]
    ]


def combined_reference_errors(documents: list[tuple[dict, Json]]) -> list[str]:
    """Over one request's documents together, every reference resolves and no
    target record is absent."""
    index: dict[str, set] = {}
    refs: list[tuple[str, Json]] = []
    for schema, value in documents:
        _collect(value, schema, schema, index, refs)
    out: list[str] = []
    for target, ref in refs:
        if target not in index:
            out.append(f"{target} is referenced but absent")
        elif ref not in index[target]:
            out.append(f"{target} {ref!r} does not resolve")
    return out


__all__ = [
    "closed_reference_errors",
    "combined_reference_errors",
    "validation_errors",
]
