SHELL := /bin/bash

docker-build :
	docker build -t pachyderm/script_to_pipeline:${tag}        . --target base
	docker build -t pachyderm/script_to_pipeline:${tag}-opencv . --target opencv

docker-push : docker-build
	docker push pachyderm/script_to_pipeline:${tag}
	docker push pachyderm/script_to_pipeline:${tag}-opencv
	sed -i.old -e 's/DEFAULT_TAG = ".*"/DEFAULT_TAG = "${tag}"/' script_to_pipeline/constants.py
	rm script_to_pipeline/constants.py.old

run-example :
	script_to_pipeline example/edges.py --pipeline example/edges.json
	cd example && ./run.sh

.PHONY: docker-build docker-push run-example
