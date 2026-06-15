# Bitrix24 to Google BigQuery Data Pipeline

Production-grade Extract-Stage-Load-Merge (ESLM) pipeline for synchronizing high-volume Bitrix24 CRM data to Google BigQuery.

## Features
- **Multi-entity support**: Deals, Leads, Contacts, etc.
- **Resilient**: Exponential backoff, rate-limit handling, and retries.
- **Audit & Idempotency**: Full tracking of batches and atomic UPSERTs.
- **Cloud-Native**: Fully integrated with GCS, BigQuery, Cloud Run, and Secret Manager.
- **Infrastructure as Code**: Terraform modules included.

## Quick Start
1. **Local Run**:
   ```bash
   ./scripts/run_local.sh
   ```

2. **Test**:
   ```bash
   pytest
   ```

3. **Deploy**:
   ```bash
   ./scripts/deploy.sh
   ```

Refer to `docs/` for detailed documentation.
