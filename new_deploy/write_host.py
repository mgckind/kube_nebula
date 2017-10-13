import os
import sys
F = open('list_ip')
try:
    N = open('list_ip_new')
    new = True
except:
    new = False
All = F.readlines()
hosts = '' 
ansible_hosts = ''
for j  in range(len(All)):
    temp = All[j].split()
    host,ip = temp 
    os.system('ssh-copy-id -i ~/.ssh/cloud.key {0}'.format(ip))
    hosts  += '{0} {1}\n'.format(ip,host)
    if j ==0:
        ansible_hosts += 'des-master ansible_ssh_host={0}\n'.format(ip)
        ansible_hosts += '\n[nodes]\n'
    if j>0:
        ansible_hosts += '{0} ansible_ssh_host={1}\n'.format(host,ip)
F.close()
if new:
    All = N.readlines()
    ansible_hosts += '\n[new]\n'
    for j  in range(len(All)):
    	temp = All[j].split()
    	host,ip = temp
        os.system('ssh-copy-id -i ~/.ssh/cloud.key {0}'.format(ip))
        ansible_hosts += '{0} ansible_ssh_host={1}\n'.format(host,ip)
    	hosts  += '{0} {1}\n'.format(ip,host)
    
    N.close()



print
print '----------------------------------------------'
print 'To be wrttein /etc/hosts'
print '----------------------------------------------'
print(hosts)
print
print '----------------------------------------------'
print 'To be written /etc/ansible/hosts'
print '----------------------------------------------'
print(ansible_hosts)

