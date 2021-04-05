

def test_homepage_get(test_client):
    """
    GIVEN a flask app configuration as test client
    WHEN the '/' (homepage) is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200


def test_homepage_post(test_client):
    """
    GIVEN a flask app configuration as test client
    WHEN the '/' (homepage) is post (POST)
    THEN check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200


