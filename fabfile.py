from fabric.api import *
import time
import socket

env.user = 'ubuntu'
env.hosts = ['my_server']
env.key_filename = 'k_keys.key'

def set_up():
    put('script.sh')
    put('k_keys.key')
    run('sudo sh script.sh')
