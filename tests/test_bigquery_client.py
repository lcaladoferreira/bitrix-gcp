import pytest
from src.bitrix_gcp.bigquery_client import BigQueryClient
from src.bitrix_gcp.schemas import DEAL_SCHEMA

def test_merge_query_generation(mocker):
    mocker.patch("google.cloud.bigquery.Client")
    client = BigQueryClient("proj")
    mock_query = mocker.patch.object(client.client, 'query')

    client.merge_to_final("staging", "final", DEAL_SCHEMA)

    args, _ = mock_query.call_args
    query = args[0]
    assert "MERGE `final` T" in query
    assert "USING (" in query
    assert "ROW_NUMBER() OVER(PARTITION BY ID ORDER BY DATE_MODIFY DESC)" in query
