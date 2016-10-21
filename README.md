## Kubernetes in OpenStack
Simple commands to install and control a kuberneter cluster in Openstack


### Requirements

It only works in python 2 given that ansible is not fully python 3 compatible. All packages below are pip installables.

- [PyYAML](http://pyyaml.org/wiki/PyYAML)
- [python-novaclient](https://github.com/openstack/python-novaclient)
- [python-neutronclient](https://github.com/openstack/python-neutronclient)
- [python-keystoneclient](https://github.com/openstack/python-keystoneclient)
- [ansible](http://docs.ansible.com/ansible/)

### Create network

    python admin_cluster.py <my_net> --create-network

### Create master
    
    python admin_cluster.py <my_net> --master

### Add nodes

    python admin_cluster.py <my_net> --add-node --multiple <number>

### All at once
    
    python admin_cluster.py <my_net> --create-network --master --add-node --multiple <number>

### Delete cluster in network
    
    python admin_cluster.py <my_net> --delete-cluster --force

### Delete network 
    
    python admin_cluster.py <my_net> --delete-network --force


