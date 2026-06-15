#!/bin/bash
set -e

echo "Building and deploying to Dev..."

# Simplified for brevity
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME=gcr.io/$PROJECT_ID/bitrix-gcp

docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME

gcloud run jobs deploy bitrix-sync-dev \
    --image $IMAGE_NAME \
    --region us-central1
