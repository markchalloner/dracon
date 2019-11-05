#!/bin/sh -e

# Tekton Pipelines
kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# ES and Kibana
minikube addons enable efk

kubectl config use-context minikube
kubectl create ns dracon || true
kubectl config set-context minikube --namespace=dracon

# Enricher DB
kubectl apply -f templates/persistence/enricher-db/k8s.yaml

# Minio
kubectl apply -f templates/persistence/minio-storage/k8s.yaml

# Dracon Pipeline
go run cmd/dracon/main.go setup --path templates/pipeline

# Dracon Run Pipeline
go run cmd/dracon/main.go run --path templates/run/git-ssh.pipeline-run.yaml
go run cmd/dracon/main.go run --path templates/run/pipeline-run.yaml

kubectl get pod
