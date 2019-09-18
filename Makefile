
SRC_DIR := api/proto
DST_DIR := gen

.PHONY: proto
proto:
	protoc -I=$(SRC_DIR) --python_out=$(DST_DIR) $(SRC_DIR)/config.proto $(SRC_DIR)/engine.proto $(SRC_DIR)/issue.proto
