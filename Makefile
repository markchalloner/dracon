
SRC_DIR := api/proto
DST_DIR := gen

.PHONY: proto
proto:
	protoc -I=$(SRC_DIR) --python_out=$(DST_DIR) $(SRC_DIR)/config.proto $(SRC_DIR)/engine.proto $(SRC_DIR)/issue.proto

dockerimages:
	docker build -f images/Dockerfile-producer-bandit -t dracon/producer/bandit producers/
	docker build -f images/Dockerfile-enricher -t dracon/enrichment enrichment_service