#!/usr/bin/env python
from __future__ import print_function
from novaclient import client
from keystoneclient.auth.identity import v2
from keystoneclient import session 
from neutronclient.v2_0 import client as nclient
import time
import os,sys
import argparse
import uuid
import time


def get_session():
    credentials = {}
    credentials['username']  = os.environ['OS_USERNAME']
    credentials['password']  = os.environ['OS_PASSWORD']
    credentials['auth_url']  = os.environ['OS_AUTH_URL']
    credentials['tenant_id'] = os.environ['OS_TENANT_ID']
    
    auth    = v2.Password(**credentials)
    my_session = session.Session(auth=auth)
    return my_session

def init_nova():
    return client.Client("2", session=get_session())

def init_neutron():
    return nclient.Client(session=get_session())

class Network(object):
    def __init__(self, neutron,name, create=True):
        self.name = name
        self.neutron = neutron
        self.body = {'name': self.name, 'admin_state_up': True}
        if create:
            self.neutron.create_network({'network':self.body})
        self.id = self.neutron.list_networks(name=self.name)['networks'][0]['id']
    def delete(self):
        self.neutron.delete_network(self.id)


class SubNet(object):
    def __init__(self, neutron, name, net_id,create=True):
        self.name = name
        self.neutron = neutron
        self.net_id = net_id
        self.cidr = '10.0.0.0/24'
        self.dns = ['141.142.2.2']
        self.body = {'name':self.name, 'network_id': self.net_id,'cidr': self.cidr,'ip_version':'4', 'dns_nameservers': self.dns}
        if create:
            self.neutron.create_subnet({'subnet':self.body  })
        self.id = self.neutron.list_subnets(name=self.name)['subnets'][0]['id']
    def delete(self):
        self.neutron.delete_subnet(self.id)


class Router(object):
    def __init__(self, neutron, name,create=True):
        self.name = name
        self.neutron = neutron
        ext_id = self.neutron.list_networks(name='ext-net')['networks'][0]['id']
        sub_id = self.neutron.list_networks(name='ext-net')['networks'][0]['subnets'][0]
        self.gate = {'network_id': ext_id, 'subnet_id':sub_id}
        self.body = {'name':self.name+'-router', 'admin_state_up': True,'external_gateway_info':self.gate}
        if create:
            self.neutron.create_router({'router':self.body})
        self.id = self.neutron.list_routers(name=self.name+'-router')['routers'][0]['id']

    def add_interface(self, subnet):
        self.neutron.add_interface_router(self.id,{'subnet_id':subnet})
        self.port_id  = self.neutron.list_ports(device_id=self.id)['ports'][0]['id']


    def delete(self):
        port_id  = self.neutron.list_ports(device_id=self.id)['ports'][0]['id']
        #self.neutron.delete_port(port_id)
        com = 'neutron router-interface-delete '+ self.id + ' port='+port_id
        print(com)
        os.system(com)
        self.neutron.delete_router(self.id)


class ClusterNet(object):
    def __init__(self, neutron, name):
        self.name = name
        self.neutron = neutron

    def create(self):
        print('creating a new network') 
        self.Network = Network(self.neutron, self.name)
        self.SubNet = SubNet(self.neutron,self.name, self.Network.id)
        self.Router = Router(self.neutron,self.name)
        self.Router.add_interface(self.SubNet.id)

    def get(self):
        self.Network = Network(self.neutron, self.name,create=False)
        self.SubNet = SubNet(self.neutron,self.name, self.Network.id,create=False)
        self.Router = Router(self.neutron,self.name,create=False)

    def delete(self):
        self.Router.delete()
        self.SubNet.delete()
        self.Network.delete()





if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create Kubernetes cluster in Openstack')
    parser.add_argument('network', type=str, help="NETWORK name")
    parser.add_argument('--add-node', '-an', dest='add_node', action='store_true', help="Add an extra node to the NETWORK")
    parser.add_argument('--multiple', '-mn', dest='multiple', type=int, default=1, help="Number of nodes (default:1)")
    parser.add_argument('--master', action='store_true', help="Use with --add-node to make that node master with public ip")
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
    
    if args.node_name is not None:
        node_name = args.node_name
    else:
        node_name = name+'-'+uuid.uuid4().hex[0:6]

    if args.add_node:
        if args.master: args.multiple = 1
        for j in range(1,args.multiple+1):
            suf = '' if args.multiple==1 else '-'+str(j)
            if args.node_name is not None:
                node_name = args.node_name+suf
            else:
                node_name = name+'-'+uuid.uuid4().hex[0:6]
            if args.master : node_name = name+'-master'

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
                    if args.master:
                        server.add_floating_ip(ip)
                        break
                    else:
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


        

