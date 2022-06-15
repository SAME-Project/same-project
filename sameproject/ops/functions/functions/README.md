# Azure Functions Backend

This directory contains the code for the `functions` backend of SAME. Usage
instructions can be found on the [documentation site](https://sameproject.ml/getting-started/platforms/setting-up-functions/).

## Testing Locally

To run the functions locally, first create a virtualenv with the dependencies
in `requirements.txt`:

```bash
virtualenv -p python3.8 .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Next, you will need to configure a `local.settings.json` file with an Azure
storage account connection string. This storage account needs permissions for
Blob storage, as we are running a Durable Functions app instead of a vanilla
Functions app:

```bash
cat <<SETTINGS > local.settings.json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<storage connection string>"
  }
}
SETTINGS
```

Note that the [functions terraform](../terraform) has a storage string as an output field.
Finally, you can host the functions locally with the following command:

```bash
func host start
```
