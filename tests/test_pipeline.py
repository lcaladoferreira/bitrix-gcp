import pytest
from bitrix_gcp.pipeline import Pipeline
from bitrix_gcp.errors import PipelineError
from unittest.mock import patch

def test_run_unsupported_entity_raises_error(mock_pipeline_deps):
    pipeline = Pipeline()
    with pytest.raises(PipelineError, match="Entity unknown not supported."):
        pipeline.run("unknown")

def test_run_full_sync_no_records(mock_pipeline_deps):
    # Setup mocks
    mock_pipeline_deps.bitrix.get_entities.return_value = iter([])

    pipeline = Pipeline()
    pipeline.run("deals")

    # Assert audit was logged with 0 records and success
    mock_pipeline_deps.audit.log_finish.assert_called_with(
        pipeline.batch_id, "SUCCESS", entity_name="deals", records_extracted=0
    )

def test_run_incremental_uses_watermark(mock_pipeline_deps):
    mock_pipeline_deps.bq.get_watermark.return_value = "2023-01-01T00:00:00"
    mock_pipeline_deps.bitrix.get_entities.return_value = iter([])

    pipeline = Pipeline()
    pipeline.run("deals")

    # Check if get_watermark was called
    mock_pipeline_deps.bq.get_watermark.assert_called()
    # Check if get_entities was called with that watermark
    mock_pipeline_deps.bitrix.get_entities.assert_called_with(
        "deals", watermark_field="DATE_MODIFY", start_date="2023-01-01T00:00:00"
    )

@patch('bitrix_gcp.pipeline.config')
def test_run_uploads_chunks_to_gcs(mock_config, mock_pipeline_deps):
    mock_config.CHUNK_SIZE = 2
    mock_config.GCP_PROJECT_ID = "p"
    mock_config.BQ_RAW_DATASET = "r"
    mock_config.BQ_STAGING_DATASET = "s"
    mock_config.BQ_FINAL_DATASET = "f"

    mock_pipeline_deps.bitrix.get_entities.return_value = iter([{"ID": "1"}, {"ID": "2"}, {"ID": "3"}])
    mock_pipeline_deps.storage.upload_jsonl.return_value = "gs://uri"

    pipeline = Pipeline()
    pipeline.run("deals")

    # 3 records with chunk size 2 should result in 2 uploads
    assert mock_pipeline_deps.storage.upload_jsonl.call_count == 2
