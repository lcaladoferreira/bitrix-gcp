# Security and Secret Manager

## Secret Manager
The pipeline retrieves sensitive credentials like the `BITRIX_WEBHOOK_URL` from Google Cloud Secret Manager at runtime.

### Configuration
1. Create a secret named `bitrix_webhook_url`.
2. Set the environment variable `BITRIX_WEBHOOK_SECRET_NAME=bitrix_webhook_url`.

### IAM
The Cloud Run Job Service Account must have the `roles/secretmanager.secretAccessor` role.
