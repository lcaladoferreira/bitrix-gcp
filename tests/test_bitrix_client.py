from bitrix_gcp.bitrix_client import BitrixClient

def test_client_init():
    c = BitrixClient("http://test")
    assert c.webhook_url == "http://test"

def test_get_entities(mocker):
    c = BitrixClient("http://test")
    mocker.patch.object(c, "_call", return_value={"result": [{"ID": "1"}], "next": None})
    res = list(c.get_entities("deals"))
    assert len(res) == 1
    assert res[0]["ID"] == "1"

def test_bitrix_client_503_retry(mocker):
    c = BitrixClient("http://test")

    # Mock responses
    mock_503 = mocker.Mock()
    mock_503.status_code = 503

    mock_200 = mocker.Mock()
    mock_200.status_code = 200
    mock_200.json.return_value = {"result": [{"ID": "retry_success"}], "next": None}

    # Patch session.post and time.sleep
    mocker.patch("time.sleep")
    mock_post = mocker.patch.object(c.session, "post", side_effect=[mock_503, mock_200])

    res = list(c.get_entities("deals"))

    assert len(res) == 1
    assert res[0]["ID"] == "retry_success"
    assert mock_post.call_count == 2
