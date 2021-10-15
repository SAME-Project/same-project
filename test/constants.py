# Environment variable that can be optionally set to specify a host where Durable Functions backend is running.
# If none is specified, the one deployed on Azure Functions is used.
DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR = "DURABLE_FUNCTIONS_BACKEND_TEST_HOST"

# Name of the app deployed on Azure Functions running the test backend.
DURABLE_FUNCTIONS_APP_NAME_AZURE = "same-df-backend"

# Azure Functions host URL where the test backend is running.
DURABLE_FUNCTIONS_BACKEND_URL_AZURE = f"https://{DURABLE_FUNCTIONS_APP_NAME_AZURE}.azurewebsites.net"
