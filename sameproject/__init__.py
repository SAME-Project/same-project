# Hacks to support importing vendored dependencies as if they were installed
# locally via `poetry add`:
from pathlib import Path
import sys

conda_path = Path(__file__).parent / "vendor/conda"
sys.path.insert(0, str(conda_path))

pipreqs_path = Path(__file__).parent / "vendor/pipreqs"
sys.path.insert(0, str(pipreqs_path))

# Clean up locals:
del Path
del sys
del conda_path
del pipreqs_path

# Imports and registers all backend runtime options:
import sameproject.ops.runtime_options
import sameproject.ops.aml.options
import sameproject.ops.functions.options
import sameproject.ops.kubeflow.options
