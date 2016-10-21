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

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create Kubernetes cluster in Openstack')
    parser.add_argument('network', type=str, help="NETWORK name")
    parser.add_argument('--add-node', '-an', dest='add_node', action='store_true', help="Add an extra node to the NETWORK")
    parser.add_argument('--multiple', '-mn', dest='multiple', type=int, default=1, help="Number of nodes (default:1)")
    parser.add_argument('--master', action='store_true', help="Creates a  node master with public ip")
    parser.add_argument('--node-name', '-nn', dest='node_name', type=str, default=None, help="Node name (default: random)")
    parser.add_argument('--create-network', dest='new_net', action='store_true', help="Create a new NETWORK")
    parser.add_argument('--delete-network', dest='del_net', action='store_true', help="Delete a NETWORK")
    parser.add_argument('--delete-cluster', dest='del_cl', action='store_true', help="Delete a cluster inside NETWORK")
    parser.add_argument('--force', action='store_true', help="Force delete")
    args = parser.parse_args()
    nova = init_nova()
    name = args.network

    im = nova.images.find(name="Ubuntu 16.04")
    fl = nova.flavors.find(name="m1.medium")
    sec = nova.security_groups.find(name='kubenet_sec')
    try:
        ip = nova.floating_ips.findall(instance_id=None)[0]
    except:
        ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name) 
    try:
        k = nova.keypairs.find(name='k_keys')
        #k.delete()
        #print('deleting key')
    except:
        print('creating a new key')
        with open('k_keys.key.pub','r') as f: pub=f.read()
        nova.keypairs.create(name='k_keys',public_key=pub)
    k = nova.keypairs.find(name='k_keys')
    
    C = ClusterNet(init_neutron(), name)
    try:
        net = nova.networks.find(label=name)
        C.get()
        if args.del_cl or args.del_net:
            if args.force:
                for server in nova.servers.findall():
                    if server.interface_list()[0].net_id == net.id:
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
    if args.master:
        inventory_dict['master_basics'] = 'true'
        inventory_dict['kube_init'] = 'true'
        inventory_dict['kube_basics'] = 'true'
        node_name = name+'-master'
        print('\nAdding node {0} to network {1} \n'.format(node_name, name))
        server=nova.servers.create(
                        name=node_name,
                        image=im.id,
                        flavor=fl.id,
                        key_name=k.name,
                        security_groups = [sec.id],
                        nics = [{'net-id':net.id}],
                        min_count = 1,
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
        os.system('ssh-keygen -R {}'.format(master_public))
        #os.system('ssh-keyscan -H {} >> ~/.ssh/known_hosts'.format(master_public))

    all_nodes = None
    if args.add_node:
        inventory_dict['node_basics'] = 'true'
        inventory_dict['kube_join'] = 'true'
        all_nodes = []
        for j in range(1,args.multiple+1):
            suf = '' if args.multiple==1 else '-'+str(j)
            if args.node_name is not None:
                node_name = args.node_name+suf
            else:
                node_name = name+'-'+uuid.uuid4().hex[0:6]

            print('\nAdding node {0} to network {1} \n'.format(node_name, name))
            server=nova.servers.create(
                        name=node_name,
                        image=im.id,
                        flavor=fl.id,
                        key_name=k.name,
                        security_groups = [sec.id],
                        nics = [{'net-id':net.id}],
                        min_count = 1,
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
            key='k_keys.key', 
            token=token,
            nodes=all_nodes,
            **inventory_dict)

        

