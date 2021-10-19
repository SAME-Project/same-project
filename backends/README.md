# Backends for SAME Python CLI

## Overview

Standardized implementations for extending the workflow execution backends that SAME CLI can run Jupyter notebooks against. Each has to:

- Render the SAME configuration into code that can be executed against the specific backend.
- Deploy the resulting code for execution to a specified instance of the backend.
  
## Project structure
- **aml:** Backend implementation for [Azure Machine Learning (AML)](https://docs.microsoft.com/EN-US/azure/machine-learning/overview-what-is-azure-machine-learning).
- **common:** Helper functions used by all backend implementations, such as dill serialization.
- **durable-functions:** Backend implementation for [Azure Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview).
- **kubeflow:** Backend implementation for [Kubeflow](https://www.kubeflow.org/docs/about/kubeflow/) on Kubernetes clusters.
