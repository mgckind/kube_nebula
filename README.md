## Kubernetes in OpenStack
Simple commands to install and control a kuberneter cluster in Openstack


### Requirements

It only works in python 2 given that ansible is not fully python 3 compatible. All packages below are pip installables.

- [PyYAML](http://pyyaml.org/wiki/PyYAML)
- [python-novaclient](https://github.com/openstack/python-novaclient)
- [python-neutronclient](https://github.com/openstack/python-neutronclient)
- [python-keystoneclient](https://github.com/openstack/python-keystoneclient)
- [ansible](http://docs.ansible.com/ansible/)

### Configuration

The file [config_nodes.yml](config_nodes.yml) has the initial configuration given OpenStack resources. This also includes the name of the key, if not in current working directory a ssh keipair will be created and upload to the server. 

### Command Examples

#### Create network

    python admin_cluster.py <my_net> --create-network

#### Create master
    
    python admin_cluster.py <my_net> --master

#### Add nodes

    python admin_cluster.py <my_net> --add-nodes <number_of_nodes>

Use `--add-nodes` or `-an` to specify number of nodes, if flag is absent, no nodes will be added.If no number, the default is 1.

#### All at once
    
    python admin_cluster.py <my_net> --create-network --master --add-nodes <number>

#### To run ansible using same script add --run-ansible or -run at the end, this will run the playbook on master

     python admin_cluster.py <my_net> -run

#### To set up a cluster of 5 nodes in one command

    python admin_cluster.py <my_net> --create-network --master --add-nodes 4 -run

#### Custon names for the nodes
By default the master will have the name <my_net>-master and the nodes will have <my_net>-<random>, you can specify the names for the node with the flag --node-name <custom-name>

#### Delete cluster in network
    
    python admin_cluster.py <my_net> --delete-cluster --force

#### Delete network 
    
    python admin_cluster.py <my_net> --delete-network --force


