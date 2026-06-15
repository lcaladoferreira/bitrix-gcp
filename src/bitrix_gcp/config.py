import os
from google.cloud import secretmanager
from bitrix_gcp.errors import ConfigurationError

class Config:
    def __init__(self):
        self.GCP_PROJECT_ID = self._get_required("GCP_PROJECT_ID")
        self.GCP_REGION = os.getenv("GCP_REGION", "us-central1")
        self.BITRIX_WEBHOOK_URL = self._load_secret("BITRIX_WEBHOOK_URL", "BITRIX_WEBHOOK_SECRET_NAME")
        self.ENTITY_NAME = os.getenv("ENTITY_NAME", "deals").lower()
        self.GCS_BUCKET = self._get_required("GCS_BUCKET")
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))
        self.BQ_RAW_DATASET = os.getenv("BQ_RAW_DATASET", "bitrix_raw")
        self.BQ_STAGING_DATASET = os.getenv("BQ_STAGING_DATASET", "bitrix_staging")
        self.BQ_FINAL_DATASET = os.getenv("BQ_FINAL_DATASET", "bitrix_final")
        self.FORCE_FULL_SYNC = os.getenv("FORCE_FULL_SYNC", "false").lower() == "true"
        self.START_DATE_OVERRIDE = os.getenv("START_DATE_OVERRIDE")

    def _get_required(self, name: str) -> str:
        val = os.getenv(name)
        if not val:
            raise ConfigurationError(f"Missing required environment variable: {name}")
        return val

    def _load_secret(self, env_name: str, secret_env_name: str) -> str:
        val = os.getenv(env_name)
        if val:
            return val
        secret_id = os.getenv(secret_env_name)
        if not secret_id:
            raise ConfigurationError(f"Missing {env_name} or {secret_env_name}")
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.GCP_PROJECT_ID}/secrets/{secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            raise ConfigurationError(f"Failed to load secret {secret_id}: {str(e)}")

config = Config()
