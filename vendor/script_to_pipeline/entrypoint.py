#!/usr/bin/env python3
import io
import site
import sys

from base64 import b64decode
from importlib import import_module, reload
from pathlib import Path
from subprocess import run
import tarfile
from tempfile import TemporaryDirectory

from script_to_pipeline.utils import get_entrypoint, pip_list

if __name__ == "__main__":
    if len(sys.argv) > 2:

        if len(sys.argv) > 3:
            dependencies = sys.argv[2:]
            packages = pip_list()
            if not all(dependency.split("==")[0] in packages for dependency in dependencies):
                run(["pip", "--disable-pip-version-check", "install", *dependencies])
                reload(site)

        tar_bytes = sys.argv[1]
        # base64 decode tar_bytes into a buffer
        buffer = io.BytesIO(b64decode(tar_bytes))

        root_module = sys.argv[2]

        # import pdb; pdb.set_trace()
        with TemporaryDirectory() as tempdir:

            # untar tar_bytes into tempdir using tarfile module
            with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
                tar.extractall(tempdir)

            p = Path(tempdir) / "context" / "requirements.txt"
            if p.exists():
                run(["pip", "--disable-pip-version-check", "install", "-r", p.as_posix()])

            # Path(tempdir, "script.py").write_bytes(source)
            import pdb; pdb.set_trace()
            sys.path.append((Path(tempdir) / "context").as_posix())
            # import pdb; pdb.set_trace()

            script = import_module(root_module)
            # SAME convention is that it outputs a root module with a root()
            # method, so call it:
            script.root()
            # entrypoint = get_entrypoint(script)
            # entrypoint()
