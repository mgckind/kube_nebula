https://github.com/kubernetes/ingress/tree/master/examples/rbac/nginx

Add :
    spec:
      serviceAccountName: nginx-ingress-serviceaccount
      hostNetwork: true
and

          ports:
          - name: http
            containerPort: 80
            hostPort: 80

and nodeSelector:
      nodetype:master

!! need to label master
kubectl create secret tls tls-certificate --cert=file.crt --key=file.key -n nginx-ingress 
kubectl create -f nginx-ingress-controller-rbac.yml
kubectl create -f default-backend.yml
kubectl create -f nginx-ingress-controller.yml
kubectl create -f nginx-ingress-controller-service.yml
