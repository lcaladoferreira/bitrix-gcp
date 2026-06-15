import os
from datetime import datetime
from typing import Optional

class Config:
    BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL")
    GCS_BUCKET = os.getenv("GCS_BUCKET")
    BQ_DATASET = os.getenv("BQ_DATASET", "bitrix_sync")
    BQ_TABLE = os.getenv("BQ_TABLE", "deals")

    FORCE_FULL_SYNC = os.getenv("FORCE_FULL_SYNC", "false").lower() == "true"
    START_DATE_OVERRIDE = os.getenv("START_DATE_OVERRIDE")

    # Default start date if no watermark and no override
    DEFAULT_START_DATE = "2010-01-01T00:00:00+00:00"

    @classmethod
    def validate(cls):
        missing = []
        if not cls.BITRIX_WEBHOOK_URL:
            missing.append("BITRIX_WEBHOOK_URL")
        if not cls.GCS_BUCKET:
            missing.append("GCS_BUCKET")

        if missing:
            raise ValueError(f"Missing mandatory environment variables: {', '.join(missing)}")

        if cls.START_DATE_OVERRIDE:
            try:
                datetime.fromisoformat(cls.START_DATE_OVERRIDE.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(f"START_DATE_OVERRIDE must be in ISO-8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), got: {cls.START_DATE_OVERRIDE}")

    @property
    def full_table_id(self):
        return f"{self.BQ_DATASET}.{self.BQ_TABLE}"

    @property
    def staging_table_id(self):
        return f"{self.BQ_DATASET}.{self.BQ_TABLE}_staging"

config = Config()
