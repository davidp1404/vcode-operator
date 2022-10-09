# vcode-operator
Kubernetes  operator based on [microsoft/vscode](https://github.com/Microsoft/vscode)and developed with python3 using [kubernetes](https://github.com/kubernetes-client/python) and [kopf](https://kopf.readthedocs.io/en/stable/) libraries.     

## What it does?
It gives you a declarative way to deploy instances of vscode on-the-web automating the creation of related native objects:
- Deployment
- Service
- Ingresses
- Persitent volume claim
```
$ cat qa/sample1.yaml 
---
apiVersion: davidp1404.github.com/v1
kind: vcodeWorkspace
metadata:
  name: sample1
  namespace: default
spec:
  volumeSize: "100Mi"
  storageClassName: "nfs-volumes"
  resources:
    requests:
      cpu: "1"
  password: "1234"
 
$ k get vcws sample1 
NAME      STORAGECLASSNAME   VOLUMESIZE   RESOURCES                                                                     AGE
sample1   nfs-volumes        100Mi        {"limits":{"cpu":"1","memory":"1Gi"},"requests":{"cpu":"1","memory":"1Gi"}}   29m

```

As a result and instance of microsoft/vscode will become available at address https://<your_ingress_fqdn>/\<namespace>/\<name>/

![Screenshot](/vscode-screenshot.png)
  
## What problems does it solve?
- Allow developing of apps from inside the k8s instance, solving issues that port-forward doesn't usually solve well (like connect to kafka brokers or any distributted component).
- Restrict access to sensible code avoiding copies outside your control.


## Installation:
```
$ git clone --depth 1 --branch v1.0 https://github.com/davidp1404/vcode-operator.git
$ cd vcode-operator
# Tune the docker-image defintion in the Makefile to reflect your scenario
# Modify yaml/vcode-operator-deployment.yaml file with the image url/tag chosen 
# Ensure your kubeconfig/context grants you the privileges needed to create crds, clusterroles, clusterrolebindings, serviceaccounts, configmaps, deployments
$ make docker-image
$ make install-crd
$ make install-operator
$ make install-qasamples
```

## Uninstallation
```
$ make uninstall-crd
$ make uninstall-operator
$ make uninstall-qasamples
```

## Status:
Maturity: early beta   
Limitations:
- [ ] We currently don't manage pvc resize


## To-Do:
- [x] Makefile to create docker images and install
- [x] Operator with multiple replicas 
- [x] Package with kustomize

