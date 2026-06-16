import google.api_core.exceptions
from bitrix_gcp.bigquery_client import BigQueryClient
from bitrix_gcp.schemas import DEAL_SCHEMA

def test_query(mocker):
    mocker.patch("google.cloud.bigquery.Client")
    c = BigQueryClient("p")
    mocker.patch.object(c.client, "query")
    c.merge_to_final("s", "f", DEAL_SCHEMA)
    assert c.client.query.called

def test_get_watermark_not_found(mocker):
    mocker.patch("google.cloud.bigquery.Client")
    c = BigQueryClient("p")

    # Mock client.query to raise google.api_core.exceptions.NotFound
    mocker.patch.object(
        c.client,
        "query",
        side_effect=google.api_core.exceptions.NotFound("Table not found")
    )

    res = c.get_watermark("dataset.table", "field")
    assert res is None
