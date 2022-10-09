#!/bin/bash
for file in {1..6}
do
    kubectl create -f sample$file.yaml
    sleep 0.2
    kubectl get cm vcode-operator-sample-org -o yaml | grep record$file
    sleep 0.2
    kubectl delete -f sample$file.yaml
done
