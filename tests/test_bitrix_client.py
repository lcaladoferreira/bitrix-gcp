import pytest
from src.bitrix_client import BitrixClient

def test_bitrix_client_init():
    client = BitrixClient("https://example.bitrix24.com/rest/1/webhook/")
    assert client.webhook_url == "https://example.bitrix24.com/rest/1/webhook"

def test_get_deals_pagination(mocker):
    client = BitrixClient("https://example.com")

    # Mock session.post
    mock_post = mocker.patch.object(client.session, 'post')

    # Mock responses for two pages
    response1 = mocker.Mock()
    response1.json.return_value = {
        "result": [{"ID": "1", "TITLE": "Deal 1"}],
        "next": 1
    }
    response1.raise_for_status.return_value = None

    response2 = mocker.Mock()
    response2.json.return_value = {
        "result": [{"ID": "2", "TITLE": "Deal 2"}],
        "next": None
    }
    response2.raise_for_status.return_value = None

    mock_post.side_effect = [response1, response2]

    deals = list(client.get_deals())

    assert len(deals) == 2
    assert deals[0]["ID"] == "1"
    assert deals[1]["ID"] == "2"
    assert mock_post.call_count == 2

def test_bitrix_client_retry(mocker):
    client = BitrixClient("https://example.com")

    # We want to test if the retry strategy is configured.
    # Testing the actual retry logic of requests.Session is hard without a real server or deep mocking.
    # But we can verify the adapter configuration.

    adapter = client.session.adapters.get("https://")
    assert adapter.max_retries.total == 10
    assert 429 in adapter.max_retries.status_forcelist
    assert 503 in adapter.max_retries.status_forcelist
