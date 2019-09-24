eval $(minikube docker-env)
make image_enricher
set -e
tmpfile=$(mktemp)
kubectl -n dracon-tekton-demo delete po db-setup || true
cat > $tmpfile<< EndOfMessage

apiVersion: v1
kind: Pod
metadata:
  name: db-setup
  namespace: dracon-demo
  labels:
    app: enricher-db-setup
spec:
    restartPolicy: Never
    containers:
    - name: enricher-db-setup
      image: dracon/enrichment
      imagePullPolicy: Never
      command:
      - "python3"
      args:
      - "/home/app/dracon/enrichment_service/enrich_service.py"
      - "--setup"
      - "--read_pvc_location"
      - "/"
      - "--write_pvc_location"
      - "/"
      - "--db_uri"
      - postgresql://dracon:dracon@dracon-db.dracon.svc.cluster.local
EndOfMessage
kubectl apply -f $tmpfile
kubectl -n dracon-demo get po db-setup