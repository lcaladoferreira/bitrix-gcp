import os
import pytest
from src.config import Config

def test_config_validation_missing():
    # Clear env vars
    if "BITRIX_WEBHOOK_URL" in os.environ: del os.environ["BITRIX_WEBHOOK_URL"]
    if "GCS_BUCKET" in os.environ: del os.environ["GCS_BUCKET"]

    # We need to re-instantiate or use class methods since config is a singleton in src/config.py
    with pytest.raises(ValueError, match="Missing mandatory environment variables"):
        Config.validate()

def test_config_validation_success(mocker):
    mocker.patch.dict(os.environ, {
        "BITRIX_WEBHOOK_URL": "https://example.com",
        "GCS_BUCKET": "my-bucket"
    })
    # Update Config class attributes because they are set at import time
    Config.BITRIX_WEBHOOK_URL = "https://example.com"
    Config.GCS_BUCKET = "my-bucket"

    Config.validate() # Should not raise

def test_invalid_date_override(mocker):
    Config.START_DATE_OVERRIDE = "invalid-date"
    with pytest.raises(ValueError, match="START_DATE_OVERRIDE must be in ISO-8601 format"):
        Config.validate()
    Config.START_DATE_OVERRIDE = None # Reset
