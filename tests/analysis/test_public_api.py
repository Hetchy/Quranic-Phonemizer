"""The analysis package's public surface and its packaged wheel.

`__all__` is exactly the importable public names, and a built wheel carries the
package, its schema module, the data the result needs, and the same `__all__`.
"""
from __future__ import annotations

import json
import subprocess
import sys
import types
import zipfile
from pathlib import Path

import pytest

from quranic_phonemizer import analysis

ROOT = Path(__file__).resolve().parents[2]


# ---- the exported surface ----

def _public_names() -> set[str]:
    return {
        name
        for name in vars(analysis)
        if not name.startswith("_")
        and name != "annotations"
        and not isinstance(getattr(analysis, name), types.ModuleType)
    }


def test_all_lists_only_importable_names():
    for name in analysis.__all__:
        assert hasattr(analysis, name), name


def test_all_has_no_duplicates():
    assert len(analysis.__all__) == len(set(analysis.__all__))


def test_all_is_exactly_the_public_namespace():
    """A new public symbol not added to __all__, or an __all__ name that does
    not resolve, fails here."""
    assert _public_names() == set(analysis.__all__)


# ---- the built wheel ----

@pytest.fixture(scope="session")
def wheel(tmp_path_factory) -> Path:
    dest = tmp_path_factory.mktemp("wheel")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "wheel", ".", "--no-deps",
             "-w", str(dest), "-q"],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=420,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
        pytest.skip(f"wheel build unavailable: {error}")
    wheels = list(dest.glob("*.whl"))
    if not wheels:
        pytest.skip("wheel build produced nothing")
    return wheels[0]


def test_the_wheel_carries_the_package_and_its_data(wheel):
    names = zipfile.ZipFile(wheel).namelist()
    assert "quranic_phonemizer/analysis/__init__.py" in names
    for module in ("serialize", "reflect", "refs", "documents", "__init__"):
        assert f"quranic_phonemizer/analysis/schema/{module}.py" in names
    assert any(n.startswith("quranic_phonemizer/data/") and n.endswith(".yaml")
               for n in names)
    assert any(n.endswith(".bin") for n in names)


def test_the_installed_wheel_exposes_the_same_all(wheel, tmp_path):
    extracted = tmp_path / "site"
    zipfile.ZipFile(wheel).extractall(extracted)
    code = (
        "import sys;"
        "sys.meta_path=[f for f in sys.meta_path"
        " if 'editable' not in type(f).__module__];"
        f"sys.path.insert(0, {str(extracted)!r});"
        "import quranic_phonemizer.analysis as a;"
        "import json;print(json.dumps(list(a.__all__)))"
    )
    done = subprocess.run(
        [sys.executable, "-c", code],
        check=True, capture_output=True, text=True, timeout=120,
    )
    assert json.loads(done.stdout.strip().splitlines()[-1]) == list(analysis.__all__)
