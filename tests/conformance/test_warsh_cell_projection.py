"""Corpus-wide closure of the selected Warsh script over public views."""
from __future__ import annotations

import pytest

from tools.warsh_projection_audit import audit


@pytest.mark.slow
def test_every_warsh_scalar_reaches_a_cell_or_boundary():
    result = audit()
    assert result.verses == 6214
    assert not result.failures
    assert len([char for char in result.scalars if char != " "]) == 62
    assert all(reach.routes for reach in result.scalars.values())

    for character in "ءأؤإئٕٔ":
        reach = result.scalars[character]
        assert reach.count
        assert reach.routes <= {"word_cell", "spelled_run"}
        assert "word_cell" in reach.routes
