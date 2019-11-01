#!/bin/sh -e

# ES and Kibana
minikube addons enable efk

kubectl config use-context minikube
kubectl create ns dracon
kubectl config set-context --namespace=dracon

# Enricher DB
kubectl apply -f templates/resources/enricher-db/k8s.yaml

# Minio
kubectl apply -f templates/resources/minio-storage/k8s.yaml

# Dracon Pipeline
go run cmd/dracon/main.go setup --path templates/pipeline

# Dracon Run Pipeline
go run cmd/dracon/main.go run --path templates/run/git-ssh.pipeline-run.yaml
go run cmd/dracon/main.go run --path templates/run/pipeline-run.yaml

kubectl get pod
