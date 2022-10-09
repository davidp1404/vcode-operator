#!/bin/bash

start() {
    source ~/.venv/bin/activate
    clear
    kopf run -A --priority 100 src/vcode-operator.py
}

qa-run() {
    cat qa/sample*.yaml | kubectl create -f -
    kubectl get vcws
}

qa-clean() {
    cat qa/sample*.yaml | kubectl delete -f -
    kubectl get vcws
}

qa-check() {
    kubectl get vcws
}


"$@"
