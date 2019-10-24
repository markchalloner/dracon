
SRC_DIR := api/proto
DST_DIR := gen

VERSION="dev-`git rev-parse --short HEAD`"

.PHONY: proto

envsetup:
	export PYTHONPATH=$$PYTHONPATH:$$(pwd):$$(pwd)/gen
	pip3 install protobuf grpcio grpcio-tools psycopg2 bandit certifi elasticsearch

proto:
	protoc -I=$(SRC_DIR) -I=$(DST_DIR) --python_out=$(DST_DIR) $(SRC_DIR)/config.proto $(SRC_DIR)/engine.proto $(SRC_DIR)/issue.proto

image_producer_bandit:
	docker build -f images/Dockerfile-producer-bandit -t dracon/producer/bandit:latest .
image_enricher:
	docker build -f images/Dockerfile-enricher -t dracon/enrichment:latest .

image_consumer_stdout:
	docker build -f images/Dockerfile-consumer-stdout_json -t dracon/consumer/stdout-json:latest .

image_consumer_elasticsearch:
	docker build -f images/Dockerfile-consumer-elasticsearch -t dracon/consumer/elasticsearch:latest .


images: image_producer_bandit image_enricher image_consumer_stdout image_consumer_elasticsearch


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
	go build -o dist/dracon -ldflags "-X github.com/thought-machine/dracon/pkg/version.BuildVersion=${VERSION}" cmd/dracon/main.go

.PHONY: run_engine
run_engine:
	go run -ldflags "-X github.com/thought-machine/dracon/pkg/version.BuildVersion=${VERSION}" cmd/dracon/main.go
