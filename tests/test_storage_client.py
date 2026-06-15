from bitrix_gcp.storage_client import StorageClient

def test_upload(mocker):
    mocker.patch("google.cloud.storage.Client")
    c = StorageClient("b")
    mock_blob = mocker.Mock()
    c.bucket.blob.return_value = mock_blob
    c.upload_jsonl([{"ID": "1"}], "deals", "batch", 1)
    assert mock_blob.upload_from_string.called
