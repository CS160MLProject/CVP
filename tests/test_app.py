from cvp.app import app


def test_homepage(app, client):
    res = client.get('/')
    assert res.status_code == 200



