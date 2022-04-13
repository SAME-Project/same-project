import sys
sys.path.insert(0, "../..")
sys.path.insert(0, "..")


from sameproject.backends.durable_functions.constants import EXECUTE_WORKFLOW_ACTIVITY_NAME
from test.constants import DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR, DURABLE_FUNCTIONS_BACKEND_URL_AZURE
from sameproject.ops import notebooks
from sameproject.data.step import Step
