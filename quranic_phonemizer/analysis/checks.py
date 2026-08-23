"""Shared law scaffolding: each surface binds its own error class once."""
from __future__ import annotations

from collections.abc import Callable


def requirer(error: type[Exception]) -> Callable[[bool, str], None]:
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise error(message)
    return require


__all__ = ["requirer"]
