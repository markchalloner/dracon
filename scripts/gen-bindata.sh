#!/bin/sh -e
statik -src=enrichment_service/configs/sql/migrations -dest=pkg/enrichment/db -p migrations
