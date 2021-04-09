

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
    response = test_client.post('/')
    html = response.data.decode()
    assert 'register_button' in html, f'Should contain register button'
    assert 'login_button' in html, f'Should contain login button'
    assert response.status_code == 200


def test_register_get(test_client):
    """
    GIVEN a flask app configuration as test client
    WHEN the '/' (homepage) is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/register')
    assert response.status_code == 200


def test_register_post(test_client):
    """
    GIVEN a flask app configuration as test client
    WHEN the '/' (homepage) is post (POST)
    THEN check that the response is valid
    """
    response = test_client.post('/register')
    html = response.data.decode()
    assert 'continue_button' in html, f'Should contain continue button'
    assert 'confirm_button' in html, f'Should contain confirm button'
    assert response.status_code == 200


def test_login_get(test_client):
    """
    GIVEN a flask app configuration as test client
    WHEN the '/' (homepage) is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200


def test_login_post(test_client):
    """
    GIVEN a flask app configuration as test client
    WHEN the '/' (homepage) is post (POST)
    THEN check that the response is valid
    """
    response = test_client.post('/login')
    html = response.data.decode()
    assert 'login_button' in html, f'Should contain login button'
    assert 'cancel_button' in html, f'Should contain cancel button'
    assert 'forgot_password_button' in html, f'Should contain forgot password button'
    assert response.status_code == 200