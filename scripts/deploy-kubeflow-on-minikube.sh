#!/bin/bash
# usage: ./deploy-kubeflow-on-minikube [READY_TIMEOUT]

if [[ -n $1 ]]; then
    READY_TIMEOUT="$1"
    echo "Using READY_TIMEOUT=$READY_TIMEOUT..."
else
    echo "No READY_TIMEOUT specified, script will end without waiting for kubeflow pods to be ready..."
    echo "Use './deploy-kubeflow-on-minikube [READY_TIMEOUT]' e.g. '10m' if you would like the script to wait."
fi

echo "Checking if minikube is installed..."
minikube_version=$(minikube version --short 2>/dev/null)
if [[ -z ${minikube_version} ]]; then
    echo "ERROR: minikube is not installed, please install before proceeding."
    return 1
else
    echo "Found minikube version: ${minikube_version} ..."
fi

echo "Checking if kubectl is installed..."
kubectl_version=$(kubectl version --short 2>/dev/null)
if [[ -z ${kubectl_version} ]]; then
    echo "ERROR: kubectl is not installed, please install before proceeding."
    return 1
else
    echo "Found ${kubectl_version} ..."
fi

# Kubernetes version must be < v1.22 as the kubeflow CRDs are defined under apiextensions.k8s.io/v1beta deprecated in v1.22.
# Starting minikube will also change the kubectl default context to minikube.
minikube start --kubernetes-version=v1.21.5

export PIPELINE_VERSION=1.7.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established crd/applications.app.k8s.io --timeout=60s
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"

if [[ -n ${READY_TIMEOUT} ]]; then
    echo "Waiting for kubeflow pods to be ready ..."
    kubectl wait --for condition=ready pods --all --namespace kubeflow --timeout=${READY_TIMEOUT}
    echo "Done waiting for kubeflow pods."
else
    echo "Kubeflow manifest applied to minikube. Pods will typically take about 10m to all be ready."
fi

echo "To remove the minikube deployment, use 'minikube delete'."
