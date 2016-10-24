#!/usr/bin/env python
from __future__ import print_function
from novaclient import client
from keystoneclient.auth.identity import v2
from keystoneclient import session 
from neutronclient.v2_0 import client as nclient
import os,sys
import argparse
import uuid
import time
from ostack import *
import inventory
import yaml
import pbook

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create Kubernetes cluster in Openstack')
    parser.add_argument('network', type=str, help="NETWORK name")
    parser.add_argument('--add-nodes', '-an', dest='add_node', nargs='?', const=1, type=int, help="Add extra nodes to the network, default: 1 for no number, 0 for no flag ")
    parser.add_argument('--master', action='store_true', help="Creates a  node master with public ip")
    parser.add_argument('--node-name', '-nn', dest='node_name', type=str, default=None, help="Node name (default: random)")
    parser.add_argument('--create-network', dest='new_net', action='store_true', help="Create a new NETWORK")
    parser.add_argument('--delete-network', dest='del_net', action='store_true', help="Delete a NETWORK")
    parser.add_argument('--delete-cluster', dest='del_cl', action='store_true', help="Delete a cluster inside NETWORK")
    parser.add_argument('--run-ansible','-run', dest='run_ansible', action='store_true', help="Run Ansible playbook on master node")
    parser.add_argument('--stop-kube', dest='stop_kube', action='store_true', help="Stop kubernetes on all nodes and remove all related files, it needs -run")
    parser.add_argument('--force', action='store_true', help="Force delete")
    args = parser.parse_args()
    nova = init_nova()
    name = args.network
    delete_key = False

    with open('config_nodes.yml') as f:
        config_nodes = yaml.load(f)

    key_root = config_nodes['master']['key']


    if not os.path.exists(key_root+'.key'):
        os.system("ssh-keygen -f {} -t rsa -N ''".format(key_root+'.key'))
        delete_key = True
    
    try:
        k = nova.keypairs.find(name=key_root)
        if delete_key:
            k.delete()
            print('deleting key')
    except:
        print('creating a new key')
        with open(key_root+'.key.pub','r') as f: pub=f.read()
        nova.keypairs.create(name=key_root,public_key=pub)
    k = nova.keypairs.find(name=key_root)
    
    C = ClusterNet(init_neutron(), name)
    try:
        net = nova.networks.find(label=name)
        C.get()
        if args.del_cl or args.del_net:
            if args.force:
                try:
                    os.remove('inventory.conf')
                except OSError:
                    pass
                for server in nova.servers.findall():
                    if server.interface_list()[0].net_id == net.id:
                        print('Deleting {} ...'.format(server.human_id))
                        server.delete()
                        time.sleep(1)
                if args.del_net:
                    C.delete()
                    print('\nNetwork {} was deleted\n'.format(name))
                os._exit(0)
            else:
                print('\n Add --force, extra security\n')
                os._exit(0)
    except:
        if not args.new_net:
            print('\nNetwork {} does not exists. Add --create-network to create a new one\n'.format(name))
            os._exit(0)
        else:
            C.create()
    
    net = nova.networks.find(label=name)
    
    inventory_dict = {'kube_stop' : 'false'}
    if args.stop_kube:
        inventory_dict = {'kube_stop' : 'true'}
    if args.master:
        try:
            ip = nova.floating_ips.findall(instance_id=None)[0]
        except:
            ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)
        inventory_dict['master_basics'] = 'true'
        inventory_dict['kube_init'] = 'true'
        inventory_dict['kube_basics'] = 'true'
        node_name = name+'-master'
        print('\nAdding node {0} to network {1} \n'.format(node_name, name))
        server=nova.servers.create(
                name=node_name,
                image=nova.images.find(name=config_nodes['master']['image']).id,
                flavor=nova.flavors.find(name=config_nodes['master']['flavor']).id,
                key_name=k.name,
                security_groups = [nova.security_groups.find(name=config_nodes['master']['security']).id],
                nics = [{'net-id':net.id}],
                min_count = 1,
                availability_zone='nova'
                )
        print(server.id)
        for i in range(20):
            time.sleep(1)
            try:
                server.add_floating_ip(ip)
                break
            except:
                continue
        for i in range(20):
            time.sleep(1)
            try:
                nova = init_nova()
                server = nova.servers.find(name=node_name)
                print(server.networks[name])
                break
            except:
                continue
        master_local  = server.networks[name][0]
        master_public = server.networks[name][1]
        master_name = node_name
        token = uuid.uuid4().hex[0:6]+'.'+uuid.uuid4().hex[0:16]

    all_nodes = None
    if args.add_node is not None:
        inventory_dict['node_basics'] = 'true'
        inventory_dict['kube_join'] = 'true'
        all_nodes = []
        for j in range(1,args.add_node+1):
            suf = '' if args.add_node==1 else '-'+str(j)
            if args.node_name is not None:
                node_name = args.node_name+suf
            else:
                node_name = name+'-'+uuid.uuid4().hex[0:6]

            print('\nAdding node {0} to network {1} \n'.format(node_name, name))
            server=nova.servers.create(
                name=node_name,
                image=nova.images.find(name=config_nodes['nodes']['image']).id,
                flavor=nova.flavors.find(name=config_nodes['nodes']['flavor']).id,
                key_name=k.name,
                security_groups = [nova.security_groups.find(name=config_nodes['nodes']['security']).id],
                nics = [{'net-id':net.id}],
                min_count = 1,
                availability_zone='nova'
                    )
            print(server.id)
            for i in range(20):
                time.sleep(1)
                try:
                    nova = init_nova()
                    server = nova.servers.find(name=node_name)
                    print(server.networks[name])
                    all_nodes.append([str(server.networks[name][0]),str(node_name)])
                    break
                except:
                    continue

    if not args.master:
        master_local  = ''
        master_public = ''
        master_name = ''
        token = ''
    inventory.create_inventory(
            m_public=master_public, 
            m_local=master_local, 
            m_name=master_name, 
            key=key_root+'.key', 
            token=token,
            nodes=all_nodes,
            **inventory_dict)

    if args.run_ansible:
        if not args.master:
            time.sleep(30) # give some time to set up the nodes
        res = pbook.run_playbook()
        if res == 0:
            inventory.update_inventory()
        if args.master:
            print()
            print('\n Dashboard at : http://{}:30080 \n'.format(master_public))
            print('\n Weavescope at : http://{}:30090 \n'.format(master_public))


        

