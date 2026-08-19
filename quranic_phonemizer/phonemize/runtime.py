"""Process-runtime controls for explicitly bounded batch requests."""
from __future__ import annotations

import gc
import threading
from contextlib import contextmanager
from collections.abc import Iterator

_LOCK = threading.Lock()
_USERS = 0
_RESTORE = False


@contextmanager
def suspend_collection() -> Iterator[None]:
    """Defer cyclic collection until the last concurrent request exits."""
    global _RESTORE, _USERS
    with _LOCK:
        if not _USERS:
            _RESTORE = gc.isenabled()
            if _RESTORE:
                gc.disable()
        _USERS += 1
    try:
        yield
    finally:
        with _LOCK:
            _USERS -= 1
            if not _USERS:
                if _RESTORE:
                    gc.enable()
                _RESTORE = False


__all__ = ["suspend_collection"]
