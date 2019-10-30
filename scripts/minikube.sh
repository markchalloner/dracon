#!/bin/sh -e

# ES and Kibana
minikube addons enable efk

kubectl create ns dracon

# Enricher DB
kubectl --context minikube -n dracon apply -f templates/resources/enricher-db/k8s.yaml

# Minio
kubectl --context minikube -n dracon apply -f templates/resources/minio-storage/k8s.yaml

# Example source codes from Git
kubectl --context minikube -n dracon apply -f templates/resources/git-ssh-example.yaml
kubectl --context minikube -n dracon apply -f templates/resources/git-https-example.yaml

# Dracon Tasks
cat templates/tasks/*.yaml | kubectl --context minikube -n dracon apply -f-

# Dracon Pipeline
kubectl --context minikube -n dracon apply -f templates/pipeline.yaml

echo "To run Dracon pipeline:"
echo "kubectl --context minikube -n dracon apply -f templates/pipeline-run.yaml"
