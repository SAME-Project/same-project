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
