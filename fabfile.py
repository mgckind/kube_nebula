from fabric.api import *
import time
import socket

env.user = 'ubuntu'
env.hosts = ['141.142.211.28']
env.key_filename = '/Users/Matias/test_kubernetes/kube_nebula/k_keys.key'

def set_up():
    put('script.sh')
    put('k_keys.key')
    run('sudo sh script.sh')
