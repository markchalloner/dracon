# Dracon Tutorial

This tutorial will walk you through creating a Dracon run to to scan an
external project ( in this case we will use [djangoat][djangoat] ). In the end
we will see our results by exploring the data in Kibana.

If you haven't already got Dracon set up, see the [install](./install.md) guide
before proceeding.

```bash
namespace="dracon-djangoat-demo"
uuid="$(cat /proc/sys/kernel/random/uuid)"
timestamp="$(date --iso-8601=s --utc)"

kubectl create ns "${namespace}" || true
kubectl -n "${namespace}" create sa dracon || true
# Set up a database instance for enrichment service to use
plz run //third_party/docker:postgres-alpine_load
plz run //infrastructure/security/dracon/enrichment_service/k8s/local:local_postgres_k8s_push -- --namespace "${namespace}"
sleep 5

# Set tables up
kubectl -n ${namespace} exec \
  "$(kubectl --namespace "${namespace}" get po -l app=dracon-enrichment-db --no-headers | head -n 1 | awk '{print $1}')" \
        -i -- psql -U dracon < "${DIR}/infrastructure/security/dracon/utils/initdb.sql"

# Ensure we have pre-requisits built and in minikube's docker
plz build //infrastructure/security/dracon/...

# Hault setup:
# plz run //infrastructure/local-hault:local_hault_setup
# plz run //experimental/hjenkins/dracon:setup_register -- --namespaces "${namespace}" --vault_addr "${hault_address}"

docker pull ubuntu:latest
code_image="ubuntu:latest"
code_command="/bin/sh"
code_args="-c 'apt update && apt install -y git && mkdir -p /workspace/scan-source /workspace/raw /workspace/enriched && chown 1000:1000 /workspace/scan-source /workspace/raw /workspace/enriched && git clone https://github.com/Contrast-Security-OSS/DjanGoat.git /workspace/scan-source/ --depth 1'"

plz run //infrastructure/security/dracon/producers/bandit/k8s:dracon_bandit_producer_load
producer_image=$(docker images | grep bandit | head -n 1 | awk '{print $1 ":" $2}')
producer_command="/usr/bin/dracon_bandit_producer.pex"
producer_config="--target /workspace/scan-source/ --output /workspace/raw/bandit.pb --scan_uuid ${uuid} --ts ${timestamp}"

plz run //infrastructure/security/dracon/enrichment_service/k8s:dracon_enrichment_service_load
enrichment_image=$(docker images | grep enrichment | head -n 1 | awk '{print $1 ":" $2}')
enrichment_command="/home/app/enrichment-service.pex"
db_uri="postgresql://dracon:dracon@dracon-enrichment-db.${namespace}.svc.cluster.local"
enrichment_config="--read_pvc_location /workspace/raw/ --write_pvc_location /workspace/enriched --db_uri ${db_uri}"

plz run //infrastructure/security/dracon/consumers/elasticsearch/k8s:dracon_elasticsearch_consumer_load
consumer_image=$(docker images | grep elasticsearch | head -n 1 | awk '{print $1 ":" $2}')
consumer_command="/home/app/elasticsearch-consumer.pex"
ES_URL=${ES_URL:=http://elasticsearch-logging.kube-system.svc.cluster.local:9200}
consumer_config="--es_url=${ES_URL} --es_index=dracon-dev --pvc_location=/workspace/enriched"

plz run //infrastructure/security/dracon:dracon -- \
 --namespace "${namespace}" \
 --pipeline \
 --scan_name "${uuid}" \
 --code_image "${code_image}" \
 --code_command "${code_command}" \
 --code_args "${code_args}" \
 --producer_image "${producer_image}" \
 --producer_command "${producer_command}" \
 --producer_config "${producer_config}" \
 --enrichment_image "${enrichment_image}" \
 --enrichment_command "${enrichment_command}" \
 --enrichment_config "${enrichment_config}" \
 --consumer_image "${consumer_image}" \
 --consumer_command "${consumer_command}" \
 --consumer_config "${consumer_config}" \
 --config_file "$HOME/.kube/config"

```

## See the results

Open Kibana to see some results:

```bash
minikube service kibana-logging --namespace kube-system
```

## Clean up

Remove the cluster:
```bash
minikube delete
```

[djangoat]: https://github.com/Contrast-Security-OSS/DjanGoat

