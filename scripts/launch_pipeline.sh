eval $(minikube docker-env)
# make images
scan_uuid=$(cat /proc/sys/kernel/random/uuid)
sed  "s/<scan_uuid>/$scan_uuid/g" templates/dracon-TaskRun.yaml > /tmp/$scan_uuid
kubectl -n dracon-demo apply -f  /tmp/$scan_uuid