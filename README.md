# Bitrix24 to BigQuery Production Pipeline

Professional-grade data pipeline to synchronize Bitrix24 CRM data to Google BigQuery using Cloud Run Jobs and GCS.

## Architecture
- **Compute**: Cloud Run Jobs (Long-running batch execution)
- **Staging**: Google Cloud Storage (JSONL with metadata and hashes)
- **Warehouse**: BigQuery (Staging, Final, and Audit tables)
- **Orchestration**: Cloud Scheduler
- **Security**: Secret Manager & IAM Least Privilege
- **IaC**: Terraform

## Local Development
```bash
./scripts/run_local.sh
```

## Deployment
1. Initialize Terraform:
   ```bash
   cd infra/terraform/environments/dev
   terraform init
   terraform apply
   ```
2. Build and Push Docker:
   ```bash
   docker build -t gcr.io/PROJECT/bitrix-sync .
   docker push gcr.io/PROJECT/bitrix-sync
   ```

## Supported Entities
- Deals
- Leads
- Contacts
- Companies
- Activities
