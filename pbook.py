from __future__ import print_function
import os
import sys
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
import yaml
import inventory
import time


def run_playbook():
    with open('config_nodes.yml') as f:
        conf = yaml.load(f)
    mykey = conf['master']['key']+'.key'
    import inventory as inventory
    master_public = inventory.get_master_ip()
    os.system('ssh-keygen -R {}'.format(master_public))
    for i in range(1000):
        time.sleep(1)
        check = os.system("ssh -i {0} -o StrictHostKeyChecking=no ubuntu@{1} 'exit' ".format(mykey,master_public))
        if check == 0:
            os.system('ssh-keyscan -H {} >> ~/.ssh/known_hosts'.format(master_public))
            break
        if check != 0:
            print('\nHostname {} is not up!\n'.format(master_public))
            sys.exit()

    
    variable_manager = VariableManager()
    loader = DataLoader()
    passwords = {}

    inventory = Inventory(loader=loader, variable_manager=variable_manager,  host_list='inventory.conf')
    playbook_path = 'master.yml'


    Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])

    options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user='slotlocker', private_key_file=mykey, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method=None, become_user='root', verbosity=None, check=False)

    variable_manager.set_inventory(inventory)

    pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, options=options, passwords=passwords)

    results = pbex.run()

    return results



