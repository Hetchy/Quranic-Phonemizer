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
from .boundary_case import explicit, isolated, joining, through
from .case import Case, Expect, StateCase, VariantCase, R, case_runs, pick
from .assertions import assert_case, parse_phonemes
from .reading import Reading, loaded, reading
from .selectors import SelectorError, registered_selectors
from .site import Site
from .variant import selected, selection, spaced

__all__ = [
    "KhilafId",
    "Case",
    "Expect",
    "Option",
    "R",
    "Reading",
    "Script",
    "Site",
    "StateCase",
    "VariantCase",
    "UnreachableWasl",
    "VariantSelection",
    "assert_case",
    "case_runs",
    "explicit",
    "for_each_riwayah",
    "isolated",
    "joining",
    "parse_phonemes",
    "pick",
    "loaded",
    "plan_for",
    "reading",
    "registered_selectors",
    "selected",
    "selection",
    "spaced",
    "SelectorError",
    "through",
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
