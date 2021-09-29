import sys

import pathlib
import sys

objects_dir = pathlib.Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(objects_dir))

from objects.step import Step
