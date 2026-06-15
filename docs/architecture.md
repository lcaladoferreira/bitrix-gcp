# Architecture
The pipeline uses a serverless architecture on GCP.
- **Bitrix24 REST API**: Source of CRM data.
- **Cloud Run Jobs**: Execution environment for long-running batch extraction.
- **Cloud Storage (GCS)**: Staging area for JSONL files.
- **BigQuery**: Final data warehouse with Staging and Final tables.
- **Cloud Scheduler**: Trigger for periodic synchronization.
- **Secret Manager**: Secure storage for the Bitrix24 Webhook URL.
