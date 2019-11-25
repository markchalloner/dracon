
VERSION="dev-`git rev-parse --short HEAD`"

.PHONY: proto

envsetup:
	export PYTHONPATH=$$PYTHONPATH:$$(pwd):$$(pwd)/gen
	pip3 install protobuf grpcio grpcio-tools psycopg2 bandit certifi elasticsearch

proto:
	scripts/gen-proto.sh

image_producers: image_producer_bandit image_producer_gosec image_producer_spotbugs
image_producer_bandit:
	docker build -f build/docker/Dockerfile-producer-bandit -t dracon/producer/bandit:latest .
image_producer_gosec:
	docker build -f build/docker/Dockerfile-producer-gosec -t dracon/producer/gosec:latest .
image_producer_spotbugs:
	docker build -f build/docker/Dockerfile-spotbugs -t dracon/producer/spotbugs:latest .

image_tools: image_bandit image_spotbugs
image_bandit:
	docker build -f build/docker/Dockerfile-bandit -t dracon/bandit:latest .
image_spotbugs:
	docker build -f build/docker/Dockerfile-spotbugs -t dracon/spotbugs:latest .

image_enricher:
	docker build -f build/docker/Dockerfile-enricher -t dracon/enrichment:latest .

image_consumers: image_consumer_stdout image_consumer_elasticsearch
image_consumer_stdout:
	docker build -f build/docker/Dockerfile-consumer-stdout_json -t dracon/consumer/stdout-json:latest .
image_consumer_elasticsearch:
	docker build -f build/docker/Dockerfile-consumer-elasticsearch -t dracon/consumer/elasticsearch:latest .

image_sources: image_source_git
image_source_git:
	docker build -f build/docker/Dockerfile-source-git -t dracon/source/git:latest .

images: image_tools image_producers image_enricher image_consumers image_sources


test_producers:
	python -m unittest discover producers/ -p '*test.py'
test_consumers:
	python -m unittest discover consumers/ -p '*test.py'

test_enrichment_service:
	python -m unittest discover enrichment_service/ -p '*test.py'

test_templating_engine:
	echo "Templating engine not released yet"

test_utils:
	python -m unittest discover utils/ -p '*test.py'

tests: test_producers test_consumers test_enrichment_service test_templating_engine test_utils

.PHONY: build_engine
build_engine:
	CGO_ENABLED=0 go build -o dist/dracon -ldflags "-X github.com/thought-machine/dracon/pkg/version.BuildVersion=${VERSION}" cmd/dracon/main.go

.PHONY: run_engine
run_engine:
	go run -ldflags "-X github.com/thought-machine/dracon/pkg/version.BuildVersion=${VERSION}" cmd/dracon/main.go
