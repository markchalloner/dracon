#!/bin/sh -e

# Tekton Pipelines
kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# ES and Kibana
minikube addons enable efk

kubectl config use-context minikube
kubectl create ns dracon || true
kubectl config set-context minikube --namespace=dracon

# Enricher DB
kubectl apply -f resources/persistence/enricher-db/k8s.yaml

# Minio
kubectl apply -f resources/persistence/minio-storage/k8s.yaml
