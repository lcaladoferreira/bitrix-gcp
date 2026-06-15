import json
import pytest
from src.bitrix_gcp.storage_client import StorageClient

def test_upload_jsonl_format(mocker):
    mocker.patch("google.cloud.storage.Client")
    client = StorageClient("bucket")
    mock_blob = mocker.Mock()
    client.bucket.blob.return_value = mock_blob

    records = [{"ID": "1"}]
    client.upload_jsonl(records, "deals", "batch1", 1)

    # Check upload content
    args, _ = mock_blob.upload_from_string.call_args
    uploaded_bytes = args[0]
    line = json.loads(uploaded_bytes.decode("utf-8"))
    assert line["ID"] == "1"
    assert "metadata" in line
    assert line["metadata"]["batch_id"] == "batch1"
