"""Corpus-wide closure of the selected Warsh script over public views."""
from __future__ import annotations

import pytest

from tools.warsh_projection_audit import audit

KNOWN_PROJECTION_GAPS = {
    "2:1", "3:1", "3:93", "7:1", "11:87", "12:90", "13:1", "26:1",
    "27:29", "27:32", "27:39", "27:62", "27:64", "27:65", "27:66",
    "28:1", "29:1", "30:1", "31:1", "32:1", "35:28", "37:52", "37:53",
}


@pytest.mark.slow
def test_every_warsh_scalar_reaches_a_cell_or_boundary():
    result = audit()
    assert result.verses == 6214
    assert {
        failure.split(": ", 1)[0] for failure in result.failures
    } == KNOWN_PROJECTION_GAPS
    assert len([char for char in result.scalars if char != " "]) == 62
    assert all(reach.routes for reach in result.scalars.values())

    for character in "ءأؤإئٕٔ":
        reach = result.scalars[character]
        assert reach.count
        assert reach.routes <= {"word_cell", "spelled_run"}
        assert "word_cell" in reach.routes
