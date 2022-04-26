from sameproject.ops.files import find_same_config, find_notebook
from tempfile import mkdtemp
from pathlib import Path
import pytest


@pytest.fixture
def tempdir():
    return Path(mkdtemp())


def test_files_find_same_config(tempdir):
    (tempdir / "empty").mkdir()
    (tempdir / "nonempty").mkdir()
    (tempdir / "nonempty" / "a").mkdir()
    (tempdir / "nonempty" / "a" / "same.yaml").touch()
    (tempdir / "nonempty" / "b").mkdir()
    (tempdir / "nonempty" / "b" / "same.yaml").touch()

    # Should return None when there is no SAME config to be found.
    assert find_same_config(tempdir / "empty", recurse=True) is None
    assert find_same_config(tempdir / "nonempty", recurse=False) is None

    # Should find the first SAME config lexicographically:
    path = str(find_same_config(tempdir / "nonempty", recurse=True))
    assert path.endswith("a/same.yaml")


def test_files_find_notebook(tempdir):
    (tempdir / "empty").mkdir()
    (tempdir / "nonempty").mkdir()
    (tempdir / "nonempty" / "a").mkdir()
    (tempdir / "nonempty" / "a" / "1.ipynb").touch()
    (tempdir / "nonempty" / "a" / "2.ipynb").touch()
    (tempdir / "nonempty" / "b").mkdir()
    (tempdir / "nonempty" / "b" / "3.ipynb").touch()

    # Should return None when there is no notebook to be found.
    assert find_notebook(tempdir / "empty", recurse=True) is None
    assert find_notebook(tempdir / "nonempty", recurse=False) is None

    # Should find the first notebook lexicographically:
    path = str(find_notebook(tempdir / "nonempty", recurse=True))
    assert path.endswith("a/1.ipynb")
