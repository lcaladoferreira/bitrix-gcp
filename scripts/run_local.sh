#!/bin/bash
export GCP_PROJECT_ID="test-project"
export BITRIX_WEBHOOK_URL="https://example.com/rest/1/secret/"
export GCS_BUCKET="test-bucket"
export ENTITY_NAME="deals"
export LOG_LEVEL="DEBUG"
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

python src/bitrix_gcp/main.py
