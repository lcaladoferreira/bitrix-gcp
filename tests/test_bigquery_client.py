from bitrix_gcp.bigquery_client import BigQueryClient
from bitrix_gcp.schemas import DEAL_SCHEMA

def test_query(mocker):
    mocker.patch("google.cloud.bigquery.Client")
    c = BigQueryClient("p")
    mocker.patch.object(c.client, "query")
    c.merge_to_final("s", "f", DEAL_SCHEMA)
    assert c.client.query.called
