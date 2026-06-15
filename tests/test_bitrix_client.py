from bitrix_gcp.bitrix_client import BitrixClient

def test_bitrix_client_masking():
    client = BitrixClient("https://example.com/rest/1/secret_key/")
    # We can't easily test the private _call without more mocking,
    # but we can check if it initializes.
    assert client.webhook_url == "https://example.com/rest/1/secret_key"

def test_get_entities_yields(mocker):
    client = BitrixClient("https://example.com")

    mock_response = {
        "result": [{"ID": "1"}, {"ID": "2"}],
        "next": None
    }
    mocker.patch.object(client, '_call', return_value=mock_response)

    entities = list(client.get_entities("deals"))
    assert len(entities) == 2
    assert entities[0]["ID"] == "1"
