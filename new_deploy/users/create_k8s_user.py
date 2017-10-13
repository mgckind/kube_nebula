import os
import sys

user = sys.argv[1]
group = 'sqre'
print(user)
if not os.path.exists('/home/{0}'.format(user)):
    print('ERROR: {0} does not exists'.format(user))
    sys.exit(0) 

os.system('openssl genrsa -out {user}.key 2048'.format(user=user))
os.system('openssl req -new -key {user}.key -out {user}.csr -subj "/CN={user}/O={group}"'.format(user=user, group=group))
os.system('sudo openssl x509 -req -in {user}.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out {user}.crt -days 500'.format(user=user))
os.system('sudo mkdir -p /home/{user}/.certs')
os.system('sudo mv {user}.key {user}.crt {user}.csr /home/{user}/.certs/'.format(user=user))
os.system('sudo chown -R {user}:{user} /home/{user}/.certs/'.format(user=user))
os.system('kubectl config set-credentials {user} --client-certificate=/home/{user}/.certs/{user}.crt --client-key=/home/{user}/.certs/{user}.key'.format(user=user))
os.system('kubectl config set-context sqre-context --namespace=sqre --user=matias')
os.system('sudo mkdir -p /home/{user}/.kube'.format(user=user))
os.system('sudo cp /home/centos/.kube/config /home/{user}/.kube/config'.format(user=user))
os.system('sudo chown -R {user}:{user} /home/{user}/.kube'.format(user=user))
