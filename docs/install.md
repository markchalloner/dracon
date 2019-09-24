# Installing Dracon

This guide sets up a new Kubernetes cluster on minikube with all that is
required to run Dracon.

## Requirements

It's assumed you have already set up and have the follow available:

- [minikube](https://minikube.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## Step #1: Create a Kubernetes cluster

Here we are setting up a new Kubernetes cluster in minikube. If you are using
your own cluster ensure you have Elasticsearch and Kibana available.

1. Create the cluster. We need more memory for ES to run happily.

   ```bash
   minikube start --disk-size 50GB --cpus 6 --memory 6144
   minikube addons enable efk
   ```

1. Ensure we are using minikube's docker daemon:

   ```bash
   eval $(minikube docker-env)
   ```

Note: It takes some time for Elasticsearch and Kibana to come up. Be patient :)

## Step #2: Installing Tekton

Based of the [tekton install docs](https://github.com/tektoncd/pipeline/blob/master/docs/install.md),
lets get tekton installed.


1. Run the
   [`kubectl apply`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#apply)
   command to install [Tekton Pipelines](https://github.com/tektoncd/pipeline)
   and its dependencies:

   ```bash
   kubectl apply --filename https://storage.googleapis.com/tekton-releases/previous/v0.6.0/release.yaml
   ```

1. Run the
   [`kubectl get`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#get)
   command to monitor the Tekton Pipelines components until all of the
   components show a `STATUS` of `Running`:

   ```bash
   kubectl get pods --namespace tekton-pipelines
   ```

   Tip: Instead of running the `kubectl get` command multiple times, you can
   append the `--watch` flag to view the component's status updates in real
   time. Use CTRL + C to exit watch mode.

## Step #3: Setup Postgres

Postgres is used by Dracon's Enricher, here we will set up postgres to running
inside our Kubernetes cluster.

1. Run the
   [`kubectl apply`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#apply)
   command to run Postgres:

   ```bash
   kubectl apply --filename https://raw.githubusercontent.com/thought-machine/dracon/master/docs/postgres-local.yaml
   ```
2. Run the
   [`kubectl get`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#get)
   command to verify postgres is now running:

   ```bash
   kubectl get all --namespace dracon
   ```

This gets us up and running with postgres that has a username `dracon` and
password `dracon`.

Note: Running postgres like this is not a recommended way in production.
However it's great as a demo run of Dracon. Running Dracon in production, you
should use a properly set up and maintained Postgres instance with valid
username and password.

## Next

Dracon is now read to be run:

- See the [tutorial](./tutorial.md) to get started.
- Look at the [examples](/examples)


#TODO add documentation about creating a SA