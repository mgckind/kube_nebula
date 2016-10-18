#sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 localhost $HOSTNAME/g" /etc/hosts
sudo curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y docker.io kubelet kubeadm kubectl kubernetes-cni
