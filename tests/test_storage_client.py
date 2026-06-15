import json
import pytest
from src.storage_client import StorageClient

def test_jsonl_generation(mocker):
    # Mock storage.Client
    mocker.patch("google.cloud.storage.Client")

    client = StorageClient("test-bucket")

    # Mock bucket and blob
    mock_bucket = mocker.Mock()
    mock_blob = mocker.Mock()
    client.bucket = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    records = [{"ID": "1", "TITLE": "Deal 1"}]
    client.upload_jsonl_chunk(records, "deals")

    # Check what was uploaded
    args, kwargs = mock_blob.upload_from_string.call_args
    uploaded_content = args[0]

    # Content should be JSONL and contain the payload field
    lines = uploaded_content.split("\n")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["ID"] == "1"
    assert data["payload"]["ID"] == "1"
    assert data["payload"]["TITLE"] == "Deal 1"
