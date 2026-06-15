import os
from typing import Optional
from google.cloud import secretmanager
from src.bitrix_gcp.errors import ConfigurationError

class Config:
    def __init__(self):
        self.GCP_PROJECT_ID = self._get_required("GCP_PROJECT_ID")
        self.GCP_REGION = os.getenv("GCP_REGION", "us-central1")

        # Bitrix Config
        self.BITRIX_WEBHOOK_URL = self._load_bitrix_webhook()
        self.ENTITY_NAME = os.getenv("ENTITY_NAME", "deals").lower()

        # Storage Config
        self.GCS_BUCKET = self._get_required("GCS_BUCKET")
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))
        self.COMPRESSION_ENABLED = os.getenv("COMPRESSION_ENABLED", "false").lower() == "true"

        # BigQuery Config
        self.BQ_RAW_DATASET = os.getenv("BQ_RAW_DATASET", "bitrix_raw")
        self.BQ_STAGING_DATASET = os.getenv("BQ_STAGING_DATASET", "bitrix_staging")
        self.BQ_FINAL_DATASET = os.getenv("BQ_FINAL_DATASET", "bitrix_final")

        # Sync Logic
        self.FORCE_FULL_SYNC = os.getenv("FORCE_FULL_SYNC", "false").lower() == "true"
        self.START_DATE_OVERRIDE = os.getenv("START_DATE_OVERRIDE")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def _get_required(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ConfigurationError(f"Missing required environment variable: {name}")
        return value

    def _load_bitrix_webhook(self) -> str:
        """Loads webhook from env or Secret Manager."""
        # Check env first (useful for local dev)
        webhook = os.getenv("BITRIX_WEBHOOK_URL")
        if webhook:
            return webhook

        secret_name = os.getenv("BITRIX_WEBHOOK_SECRET_NAME")
        if not secret_name:
            raise ConfigurationError("Neither BITRIX_WEBHOOK_URL nor BITRIX_WEBHOOK_SECRET_NAME is set.")

        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.GCP_PROJECT_ID}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            raise ConfigurationError(f"Failed to load secret {secret_name}: {str(e)}")

# Singleton instance for the pipeline
config = Config()
