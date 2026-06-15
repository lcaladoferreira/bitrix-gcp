# Security
All secrets are managed via Google Cloud Secret Manager.

## Secret Manager Integration
The application uses the `google-cloud-secret-manager` client to retrieve the `BITRIX_WEBHOOK_URL` at runtime.

### IAM Roles
The Service Account requires `roles/secretmanager.secretAccessor` on the specific secret.

### Configuration
Set `BITRIX_WEBHOOK_SECRET_NAME` to the name of the secret in GCP. The app will fetch the `latest` version.
