copy pod-selector-file to :
/etc/kubernetes/manifest

add PodNodeSelector to admission control in kubernetes-api manifest
add --admission-control-config-file=/etc/kubernetes/manifest/pod-selector.yaml to kube-api options
