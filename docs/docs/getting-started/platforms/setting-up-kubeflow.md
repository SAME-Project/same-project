---
type: docs
title: "Setting up Kubeflow"
description: "How to set up Kubeflow for SAME."
---

First, you will need a Kubernetes setup. You can test this by executing a simple command:

```bash
kubectl get nodes
```

Next, you will need to setup the default Kubeflow installation. We are following the [manifests](https://github.com/kubeflow/manifests/tree/master/apps/pipeline/upstream) effort in Kubeflow (as of June 2022).

```bash
KFP_ENV=platform-agnostic
kubectl apply -k cluster-scoped-resources/
kubectl wait crd/applications.app.k8s.io --for condition=established --timeout=60s
kubectl apply -k "env/${KFP_ENV}/"
kubectl wait pods -l application-crd-id=kubeflow-pipelines -n kubeflow --for condition=Ready --timeout=1800s
```

You can test your installation is working properly by executing the following:

```bash
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```

From this point, the SAME project should be up and ready to go!
