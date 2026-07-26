"""The IndoPak adapter.

Deliberately almost empty. Everything this script knows is declared in
`data/riwayat/hafs/scripts/indopak.yaml`; the reading machinery is shared
(`orthography/cluster.py`) and the facts it under-specifies are derived
(`canon/derive/`). ADR-001 §2 asserted the adapters would stay thin and then
withdrew the claim as a premise. This file is where it becomes a measurement.
"""
from __future__ import annotations

from ....model.address import Script
from ..resources import script_adapter

adapter = script_adapter(Script.INDOPAK)
