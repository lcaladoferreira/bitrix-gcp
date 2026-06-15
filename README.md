# Bitrix24 to BigQuery Sync Pipeline

This project implements a robust, production-ready implementation for synchronizing data (starting with Deals) from Bitrix24 CRM to Google BigQuery using an Extract-Stage-Load-Merge (ESLM) pattern.

## Architecture Overview

The pipeline follows these steps:
1.  **Extract**: Fetches data from Bitrix24 REST API using a resilient client with exponential backoff and optimized pagination (`start=-1`).
2.  **Stage**: Serializes records to Newline Delimited JSON (JSONL) and uploads them in chunks to Google Cloud Storage (GCS).
3.  **Load**: Ingests the JSONL files from GCS into a BigQuery staging table.
4.  **Merge**: Atomically merges (UPSERT) data from the staging table into the final production table, ensuring deduplication and idempotency.

The pipeline is designed to run as a **Cloud Run Job**, allowing for long execution times required for large dataset backfills.

## Environment Variables

| Variable | Description | Mandatory | Default |
| :--- | :--- | :---: | :--- |
| `BITRIX_WEBHOOK_URL` | Your Bitrix24 REST API webhook URL | Yes | - |
| `GCS_BUCKET` | The GCS bucket for intermediate staging | Yes | - |
| `BQ_DATASET` | Target BigQuery dataset | No | `bitrix_sync` |
| `BQ_TABLE` | Target BigQuery table | No | `deals` |
| `FORCE_FULL_SYNC` | Set to `true` to ignore the BigQuery watermark | No | `false` |
| `START_DATE_OVERRIDE` | ISO-8601 date to force sync from a specific point | No | - |

## How to Run Locally

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Authenticate with GCP**:
    ```bash
    gcloud auth application-default login
    ```

3.  **Set environment variables**:
    ```bash
    export BITRIX_WEBHOOK_URL="your_webhook_url"
    export GCS_BUCKET="your_bucket_name"
    ```

4.  **Run the script**:
    ```bash
    PYTHONPATH=. python main.py
    ```

## Synchronization Modes

### Full Sync / Backfill
To run a full sync from the beginning of time:
```bash
export FORCE_FULL_SYNC=true
python main.py
```

### Incremental Sync
By default, the pipeline queries BigQuery for the `MAX(DATE_MODIFY)` and uses it as a watermark to fetch only new or updated records.

## Build and Deployment

### Build the container
```bash
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME=bitrix-sync-pipeline

docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME .
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME
```

### Deploy to Cloud Run Jobs
```bash
gcloud run jobs deploy bitrix-sync \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --tasks 1 \
    --max-retries 3 \
    --task-timeout 3600 \
    --set-env-vars BITRIX_WEBHOOK_URL=$BITRIX_WEBHOOK_URL,GCS_BUCKET=$GCS_BUCKET \
    --region us-central1
```
*Note: For full backfills, increase `--task-timeout` up to 86400 (24h).*

### Schedule with Cloud Scheduler
```bash
gcloud scheduler jobs create http bitrix-sync-hourly \
    --schedule="0 * * * *" \
    --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/bitrix-sync:run" \
    --http-method=POST \
    --oauth-service-account-email=$SERVICE_ACCOUNT_EMAIL \
    --region us-central1
```

## TODOs for Production Hardening

- [ ] Implement sharding via `CLOUD_RUN_TASK_INDEX` for extreme volumes if Bitrix24 rate limits allow.
- [ ] Add more entities (Leads, Contacts, Companies).
- [ ] Implement Alert Policies in Cloud Monitoring for job failures.
- [ ] Set up GCS Lifecycle Policy for the staging bucket.
- [ ] Use Secret Manager for `BITRIX_WEBHOOK_URL` instead of env vars.

## Testing
Run tests with:
```bash
PYTHONPATH=. pytest
```
