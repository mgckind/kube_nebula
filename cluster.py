from novaclient import client
from keystoneclient.auth.identity import v2
from keystoneclient import session
from neutronclient.v2_0 import client as nclient
import time
import os

def init():
    Credentials = {}
    Credentials['username']  = os.environ['OS_USERNAME']
    Credentials['password']  = os.environ['OS_PASSWORD']
    Credentials['auth_url']  = os.environ['OS_AUTH_URL']
    Credentials['tenant_id'] = os.environ['OS_TENANT_ID']
    
    auth    = v2.Password(**Credentials)
    sess = session.Session(auth=auth)
    nova = client.Client("2", session=sess)
    neutron = nclient.Client(session=sess)
    return nova, neutron





if __name__=='__main__':
    nova,_ = init()
    im = nova.images.find(name="Ubuntu 16.04")
    fl = nova.flavors.find(name="m1.medium")
    try:
        k = nova.keypairs.find(name='k_keys')
        k.delete()
        print('deleting key')
    except:
        pass

    print('creating a new key')
    with open('k_keys.key.pub','r') as f: pub=f.read()
    nova.keypairs.create(name='k_keys',public_key=pub)
    k = nova.keypairs.find(name='k_keys')
    net = nova.networks.find(label='kube-net')
    sec = nova.security_groups.find(name='kubenet_sec')


    try:
        ip = nova.floating_ips.findall(instance_id=None)[0]
    except:
        ip = nova.floating_ips.create(nova.floating_ip_pools.list()[0].name)

    nova.servers.create(
            name='kcc',
            image=im.id,
            flavor=fl.id,
            key_name=k.name,
            security_groups = [sec.id],
            nics = [{'net-id':net.id}],
            min_count = 3,
            )


