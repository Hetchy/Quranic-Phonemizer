"""Total value-directed serializer from a record to plain JSON.

Id newtypes collapse to their scalar, enums to their value, tuples to lists,
frozensets to sorted lists; a leading underscore is dropped from a field name.
"""
from __future__ import annotations

import dataclasses
from enum import Enum

Json = None | bool | int | str | list | dict


def _is_id(value: object) -> bool:
    """A single-field record named `value` carrying a scalar is an identity."""
    if not dataclasses.is_dataclass(value) or isinstance(value, type):
        return False
    fields = dataclasses.fields(value)
    return (
        len(fields) == 1
        and fields[0].name == "value"
        and isinstance(getattr(value, "value"), (int, str))
    )


def to_json(value: object) -> Json:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, Enum):
        return value.value
    if _is_id(value):
        return value.value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name.lstrip("_"): to_json(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, (tuple, list)):
        return [to_json(item) for item in value]
    if isinstance(value, (frozenset, set)):
        return sorted(to_json(item) for item in value)
    if isinstance(value, dict):
        return {str(key): to_json(item) for key, item in value.items()}
    raise TypeError(f"cannot serialize {type(value).__name__}")


__all__ = ["Json", "to_json"]
