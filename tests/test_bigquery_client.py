import pytest
from src.bigquery_client import BigQueryClient

def test_merge_sql_construction(mocker):
    # Mock bigquery.Client
    mocker.patch("google.cloud.bigquery.Client")

    bq_client = BigQueryClient()
    mock_query = mocker.patch.object(bq_client.client, 'query')

    staging_table = "project.dataset.deals_staging"
    final_table = "project.dataset.deals"

    bq_client.merge_staging_to_final(staging_table, final_table)

    # Verify the SQL construction
    args, kwargs = mock_query.call_args
    sql = args[0]

    assert f"MERGE `{final_table}` T" in sql
    assert f"FROM `{staging_table}`" in sql
    assert "ROW_NUMBER() OVER(PARTITION BY ID ORDER BY DATE_MODIFY DESC)" in sql
    assert "WHEN MATCHED THEN" in sql
    assert "WHEN NOT MATCHED THEN" in sql
    assert "T.payload = S.payload" in sql
