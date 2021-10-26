import sys
sys.path.insert(0, "../..")
sys.path.insert(0, "..")


from test.constants import DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR, DURABLE_FUNCTIONS_BACKEND_URL_AZURE
from clients.durable_functions_client import DurableFunctionsClient
