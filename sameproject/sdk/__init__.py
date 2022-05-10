# Hack to support importing vendored conda package with `import conda`:
from pathlib import Path
import sys

conda_path = Path(__file__).parent.parent / "vendor/conda"
sys.path.insert(0, str(conda_path))

del sys
del Path
del conda_path

# Actual `sdk` package exports.
from .conda_env import CondaEnv, CondaEnvValidator
from .importer import import_packages
from .dataset import dataset
