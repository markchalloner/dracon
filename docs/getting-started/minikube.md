## Getting Started with Dracon on Minikube

## Installation

A helper script that automates the below exists in `./scripts/minikube.sh`.

1. First install the latest release of Tekton Pipelines:
```
kubectl --context minikube apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
```
2. Create a namespace for Dracon
```
kubectl --context minikube create namespace dracon
```
3. Create a DB for the Enricher
```
kubectl apply --context minikube --namespace dracon -f resources/persistence/enricher-db/k8s.yaml
```
**Note**: Running postgres like this is not recommended in production. However it's great as a demo run of Dracon. Running Dracon in production, you should use a properly set up and maintained Postgres instance with secret username and password.

4. Start Minio for ephemeral build storage
```
kubectl apply --context minikube --namespace dracon -f resources/persistence/minio-storage/k8s.yaml
```
5. Dracon is now ready to use


## Usage

### Configure Kubectl

Configure Kubectl to use the `minikube` context and `dracon` namespace by default:
```
kubectl config use-context minikube
kubectl config set-context minikube --namespace=dracon
```

### Setting up a Pipeline
To setup an pipeline, you can execute:
```
dracon setup --pipeline examples/pipelines/golang-project
```

### Running a Pipeline
To run that example pipeline you can execute:
```
dracon run --pipeline examples/pipelines/golang-project
```
