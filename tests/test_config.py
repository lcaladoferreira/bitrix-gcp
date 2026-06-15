import os
import pytest
from src.bitrix_gcp.config import Config
from src.bitrix_gcp.errors import ConfigurationError

def test_config_missing_vars():
    # Clear env
    for k in ["GCP_PROJECT_ID", "BITRIX_WEBHOOK_URL", "GCS_BUCKET"]:
        if k in os.environ: del os.environ[k]

    with pytest.raises(ConfigurationError):
        Config()

def test_config_valid(mocker):
    mocker.patch.dict(os.environ, {
        "GCP_PROJECT_ID": "p",
        "BITRIX_WEBHOOK_URL": "h",
        "GCS_BUCKET": "b"
    })
    c = Config()
    assert c.GCP_PROJECT_ID == "p"
    assert c.GCS_BUCKET == "b"
