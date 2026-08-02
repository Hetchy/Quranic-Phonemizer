"""Declaring a case: where it sits, how it is read, and what it produced."""
from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import (
    KhilafId,
    Option,
    Script,
    VariantSelection,
)

from .boundary import UnreachableWasl, plan_for
from .reading import Reading, reading
from .site import Site

__all__ = [
    "KhilafId",
    "Option",
    "Reading",
    "Script",
    "Site",
    "UnreachableWasl",
    "VariantSelection",
    "for_each_riwayah",
    "plan_for",
    "reading",
]


def for_each_riwayah(site: Site, *, scripts=(Script.UTHMANI,), **boundary):
    """Run one case under every riwayah the site declares and this build has."""
    def decorate(body):
        cases = [
            (name, script) for name in site.shipped() for script in scripts
        ]
        if not cases:
            return pytest.mark.skip(
                reason="no declared riwayah is packaged in this build"
            )(body)

        def test(riwayah, script):
            body(reading(site, riwayah, script, **boundary))

        test.__name__ = body.__name__
        test.__doc__ = body.__doc__
        return pytest.mark.parametrize(
            ("riwayah", "script"),
            cases,
            ids=[f"{name}-{script.value}" for name, script in cases],
        )(test)

    return decorate
