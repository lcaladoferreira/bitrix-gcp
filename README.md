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

## Infrastructure and Security

### Service Account Roles
The Service Account running the Cloud Run Job and Cloud Scheduler should have the following roles:
- `roles/storage.objectAdmin`: To write/read staging files in GCS.
- `roles/bigquery.jobUser`: To run BigQuery load and merge jobs.
- `roles/bigquery.dataEditor`: To write data to the target dataset.
- `roles/secretmanager.secretAccessor`: To access the Bitrix24 webhook URL secret.
- `roles/run.invoker`: For Cloud Scheduler to trigger the Cloud Run Job.
- `roles/logging.logWriter`: To send logs to Cloud Logging.

### Production Hardening: Secret Manager
Instead of plain environment variables, use Google Cloud Secret Manager for the `BITRIX_WEBHOOK_URL`.

1. **Create the secret**:
   ```bash
   echo -n "https://your-portal.bitrix24.com/rest/1/secret-key" | \
   gcloud secrets create BITRIX_WEBHOOK_URL --data-file=-
   ```

2. **Grant access to the Service Account**:
   ```bash
   gcloud secrets add-iam-policy-binding BITRIX_WEBHOOK_URL \
       --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

## Detailed Deployment Commands

### 1. Setup Resources
```bash
# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
BUCKET_NAME=${PROJECT_ID}-bitrix-staging
DATASET_ID=bitrix_sync

# Create GCS Bucket
gsutil mb -l ${REGION} gs://${BUCKET_NAME}

# Create BigQuery Dataset
bq --location=${REGION} mk --dataset ${DATASET_ID}
```

### 2. Build and Push Image
```bash
IMAGE_NAME=bitrix-sync-pipeline
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME .
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME
```

### 3. Create/Update Cloud Run Job
```bash
gcloud run jobs deploy bitrix-sync \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --tasks 1 \
    --max-retries 3 \
    --task-timeout 3600 \
    --region $REGION \
    --set-env-vars GCS_BUCKET=$BUCKET_NAME,BQ_DATASET=$DATASET_ID \
    --set-secrets BITRIX_WEBHOOK_URL=BITRIX_WEBHOOK_URL:latest
```

### 4. Schedule the Job
```bash
# Create a Service Account for the Scheduler
SA_NAME=bitrix-sync-scheduler
gcloud iam service-accounts create ${SA_NAME}

# Grant Invoker role
gcloud run jobs add-iam-policy-binding bitrix-sync \
    --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --region $REGION

# Create Scheduler Job (Hourly)
gcloud scheduler jobs create http bitrix-sync-hourly \
    --schedule="0 * * * *" \
    --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/bitrix-sync:run" \
    --http-method=POST \
    --oauth-service-account-email="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --region $REGION
```

## How to Run Locally for Testing

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

## Testing
Run tests with:
```bash
PYTHONPATH=. pytest
```
