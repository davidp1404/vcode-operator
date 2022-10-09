SHELL:=/bin/bash
NAMESPACE=vcode-operator
docker-image: Dockerfile
	docker build -t davidp1404/vcode-operator .
	kind load docker-image davidp1404/vcode-operator # for my k8s setup based on kind

yaml-stanzas:
	mkdir -p yaml
	kubectl create ns ${NAMESPACE} --dry-run=client -o yaml > yaml/namespace.yaml
	kubectl -n ${NAMESPACE} create sa vcode-operator-sa --dry-run=client -o yaml > yaml/vcode-operator-sa.yaml
	kubectl create cm vcode-operator-app --from-file=vcode-operator.py=src/vcode-operator.py \
	  --dry-run=client -o yaml > yaml/vcode-operator-app.yaml
	kubectl create cm vcode-operator-templates --from-file=src/templates --dry-run=client -o yaml > yaml/vcode-operator-templates.yaml

install-crds:
	@kubectl apply -f crds/vcode-operator-crds.yaml
	@kubectl apply -f crds/kopf-peering.yaml

uninstall-crds:
	-@read -n1 -p "Delete all vcws to avoid orphans? (ctrl+c to stop)" && kubectl delete vcws -A --all 
	kubectl delete -f crds/vcode-operator-crds.yaml
	kubectl delete -f crds/kopf-peering.yaml

install-operator: yaml-stanzas
	kubectl kustomize yaml | kubectl apply -f -

uninstall-operator:
	kubectl kustomize yaml | kubectl delete -f -

install-qasamples:
	-cat qa/sample*.yaml | kubectl -n default apply -f -

uninstall-qasamples:
	-cat qa/sample*.yaml | kubectl -n default delete -f -
