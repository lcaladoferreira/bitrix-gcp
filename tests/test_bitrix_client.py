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
