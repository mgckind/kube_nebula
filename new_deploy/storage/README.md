https://github.com/kubernetes/examples/tree/master/staging/volumes/nfs
- mount cinder volume to master
- format volume : sudo mkfs.ext4 /dev/vdb
- create mounting point: sudo mkdir /external
- mount: sudo mount /dev/vdb /external
- sudo chown -R centos:centos /external
- create PV; nfs-pv.yaml
- create PVC; nff-pvc.yaml
- test with busy box

--Nebula
make sure the volume path are correct, /external vs /external01
--LSST
sudo mount /dev/vdb /external01
sudo mount /dev/vdc /external02
sudo mount /dev/vdd /external03
kubectl apply -f nfs-server-deploy.yaml
kubectl apply -f nfs-server-service.yaml
--DES
sudo mount /dev/vdb /external

--Test

