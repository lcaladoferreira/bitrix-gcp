import pytest
from unittest.mock import patch
from bitrix_gcp.pipeline import Pipeline
from bitrix_gcp.errors import PipelineError

@patch('bitrix_gcp.pipeline.BitrixClient')
@patch('bitrix_gcp.pipeline.StorageClient')
@patch('bitrix_gcp.pipeline.BigQueryClient')
@patch('bitrix_gcp.pipeline.AuditManager')
def test_run_unsupported_entity_raises_error(mock_audit, mock_bq, mock_storage, mock_bitrix):
    pipeline = Pipeline()
    with pytest.raises(PipelineError, match="Entity unknown not supported."):
        pipeline.run("unknown")

@patch('bitrix_gcp.pipeline.BitrixClient')
@patch('bitrix_gcp.pipeline.StorageClient')
@patch('bitrix_gcp.pipeline.BigQueryClient')
@patch('bitrix_gcp.pipeline.AuditManager')
def test_run_full_sync_no_records(mock_audit_cls, mock_bq_cls, mock_storage_cls, mock_bitrix_cls):
    # Setup mocks
    mock_bitrix = mock_bitrix_cls.return_value
    mock_bitrix.get_entities.return_value = iter([])

    mock_audit = mock_audit_cls.return_value

    pipeline = Pipeline()
    pipeline.run("deals")

    # Assert audit was logged with 0 records and success
    mock_audit.log_finish.assert_called_with(
        pipeline.batch_id, "SUCCESS", entity_name="deals", records_extracted=0
    )

@patch('bitrix_gcp.pipeline.BitrixClient')
@patch('bitrix_gcp.pipeline.StorageClient')
@patch('bitrix_gcp.pipeline.BigQueryClient')
@patch('bitrix_gcp.pipeline.AuditManager')
def test_run_incremental_uses_watermark(mock_audit, mock_bq_cls, mock_storage, mock_bitrix_cls):
    mock_bq = mock_bq_cls.return_value
    mock_bq.get_watermark.return_value = "2023-01-01T00:00:00"

    mock_bitrix = mock_bitrix_cls.return_value
    mock_bitrix.get_entities.return_value = iter([])

    pipeline = Pipeline()
    pipeline.run("deals")

    # Check if get_watermark was called with correct field
    mock_bq.get_watermark.assert_called()
    # Check if get_entities was called with that watermark
    mock_bitrix.get_entities.assert_called_with(
        "deals", watermark_field="DATE_MODIFY", start_date="2023-01-01T00:00:00"
    )

@patch('bitrix_gcp.pipeline.BitrixClient')
@patch('bitrix_gcp.pipeline.StorageClient')
@patch('bitrix_gcp.pipeline.BigQueryClient')
@patch('bitrix_gcp.pipeline.AuditManager')
@patch('bitrix_gcp.pipeline.config')
def test_run_uploads_chunks_to_gcs(mock_config, mock_audit, mock_bq, mock_storage_cls, mock_bitrix_cls):
    mock_config.CHUNK_SIZE = 2
    mock_config.GCP_PROJECT_ID = "p"
    mock_config.BQ_RAW_DATASET = "r"
    mock_config.BQ_STAGING_DATASET = "s"
    mock_config.BQ_FINAL_DATASET = "f"

    mock_bitrix = mock_bitrix_cls.return_value
    mock_bitrix.get_entities.return_value = iter([{"ID": "1"}, {"ID": "2"}, {"ID": "3"}])

    mock_storage = mock_storage_cls.return_value
    mock_storage.upload_jsonl.return_value = "gs://uri"

    pipeline = Pipeline()
    pipeline.run("deals")

    # 3 records with chunk size 2 should result in 2 uploads
    assert mock_storage.upload_jsonl.call_count == 2
