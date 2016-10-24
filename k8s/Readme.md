### Some Kubernetes services

These services are installed by default, and the source were originally extracted from their websites. Modify this file to expose the desire external port, leave blank to get a random port between 30000-32767 

### Heapster, required to display graphics in dashboard (graphana and influxDB) and monitor cluster

- [Website](https://github.com/kubernetes/heapster)
- [Files](https://github.com/kubernetes/heapster/tree/master/deploy/kube-config/influxdb)
- Command: `kubectl apply -f influxdb`

### Dashboard, default port 30080

- [Website](https://github.com/kubernetes/dashboard)
- [File](https://github.com/kubernetes/dashboard/blob/master/src/deploy/kubernetes-dashboard.yaml)
- Command: `kubectl create -f kubernetes-dashboard.yaml`

Deployed at `https://<kubernetes-master>:30080`

### Weavescope, default port 30090

- [Website](https://www.weave.works/)
- [Installation](https://www.weave.works/documentation/scope-latest-installing/#k8s)
- [Manifest file](https://cloud.weave.works/launch/k8s/weavescope.yaml)
- [Weave-Net](https://github.com/weaveworks/weave-kube)
- Command: `kubectl apply -f weavescope.yaml`

Deployed at `https://<kubernetes-master>:30090`

