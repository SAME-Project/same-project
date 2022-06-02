from sameproject.data.config import SameConfig
from .fuzzer import genstr, example_params
from sameproject.cli.init import init
from click.testing import CliRunner
from pathlib import Path
import test.testdata
import pytest


def test_init():
    for i in range(100):
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Copy over a notebook for the test:
            path = Path(test.testdata.__file__).parent / "features/singlestep/singlestep.ipynb"
            data = path.read_text()
            Path("a" + genstr(example_params) + ".ipynb").write_text(data)

            # Run `same init` with randomly generated input data:
            res = runner.invoke(init, input=_geninput())

            # If an invariant is failed we print the test output for debugging:
            output = f"Run output: \n{res.output}"

            # `same init` should never exit with an unhandled exception.
            assert res.exception is None or type(res.exception) is SystemExit, output

            # If `same init` exits with code 1, then no config should be written.
            if res.exit_code == 1:
                assert not Path("same.yaml").exists(), output
                continue

            # If `same init` exits with code 0, then it should have written a config
            # that is valid, and which can be run with `same run -f same.yaml`.
            # TODO: actually call `same run` with a mock backend
            path = Path("same.yaml")
            assert path.exists(), output
            try:
                SameConfig.from_yaml(path.read_text())  # will validate the config
            except Exception as err:
                assert False, f"Invalid config:\n{err}\n\n{output}"


def _geninput():
    return "\n".join([
        genstr(example_params) for _ in range(50)
    ])
