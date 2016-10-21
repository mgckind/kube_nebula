from __future__ import print_function
from novaclient import client
from keystoneclient.auth.identity import v2
from keystoneclient import session 
from neutronclient.v2_0 import client as nclient
import os,sys

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

