# Operational Runbook

## How to Trigger a Full Resync
If you need to refresh all data for a specific entity, ignore the existing watermark:
1.  Set environment variable `FORCE_FULL_SYNC=true`.
2.  Run the pipeline.

## How to Backfill from a Specific Date
To sync data starting from a historical point in time:
1.  Set environment variable `START_DATE_OVERRIDE=YYYY-MM-DD` (ISO-8601).
2.  Run the pipeline.

## How to Add a New Bitrix24 Entity
1.  Define the schema in `src/bitrix_gcp/schemas.py`. Use the `get_base_schema_fields()` helper.
2.  Add the new schema instance to the `ENTITY_MAP` dictionary in `schemas.py`.
3.  The pipeline will automatically handle the new entity when `ENTITY_NAME` environment variable is updated.

## Troubleshooting Common Errors

### 429 / 503 Bitrix API Errors
The pipeline has built-in exponential backoff. If these errors persist:
- Check if multiple jobs are running simultaneously.
- Verify Bitrix24 instance rate limits.

### BigQuery Merge Failures
- Ensure the `STAGING` and `FINAL` schemas match.
- Check the `pipeline_audit` table for detailed error messages.

### Permission Denied
- Verify the Service Account has the required IAM roles (see `architecture.md`).
- Ensure Secret Manager access is granted.
