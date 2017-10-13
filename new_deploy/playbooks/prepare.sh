#!/bin/bash
# install kubernetes repo
cat << EOF >/etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
        https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
# Add the Docker public key
rpm --import "https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e"
# Install the Docker repo (1.12 is the last stable version compatible with k8s 1.7)
yum-config-manager --add-repo https://packages.docker.com/1.12/yum/repo/main/centos/7
yum install -y docker-engine
# Add centos as a user of docker
usermod -aG docker centos
# Turn off SELinux
setenforce 0
#kube 1.7
yum install -y kubelet-1.7.3 kubeadm-1.7.3  kubectl-1.7.3
#yum install -y kubelet-1.8.0 kubeadm-1.8.0  kubectl-1.8.0
# change systemd to cgroupfs (to make Kubelet  compatible with Docker)
cp /etc/systemd/system/kubelet.service.d/10-kubeadm.conf /etc/systemd/system/kubelet.service.d/10-kubeadm.conf.bak
sed 's/KUBELET_CGROUP_ARGS=--cgroup-driver=systemd/KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs/' < /etc/systemd/system/kubelet.service.d/10-kubeadm.conf.bak > /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
# enable and start services
systemctl start docker
systemctl enable kubelet
systemctl start kubelet
# set iptables
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
