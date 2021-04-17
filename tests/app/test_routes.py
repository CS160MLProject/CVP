from cvp.app.routes import app
from cvp.app.utils import get_profile


class TestRoutes:

    def __init__(self):
        self.test_account_info = get_profile(1)

    def test_homepage_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.get('/')
        assert response.status_code == 200

    def test_homepage_post(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is post (POST)
        THEN check that the response is valid
        """
        response = test_client.post('/')
        html = response.data.decode()
        assert 'register_button' in html, f'Should contain register button {html}'
        assert 'login_button' in html, f'Should contain login button'
        assert response.status_code == 200

        response = self.__click_button_post(test_client, '/', 'register_button')
        assert response.status_code == 302 # redirect

        response = self.__click_button_post(test_client, '/', 'login_button')
        assert response.status_code == 302

    def test_register_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.get('/register')
        assert response.status_code == 200, f'{response.data.decode()}'

    def test_register_post(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is post (POST)
        THEN check that the response is valid
        """
        response = test_client.post('/register')
        html = response.data.decode()
        assert 'continue_button' in html, f'Should contain continue button'
        assert response.status_code == 200

        response = self.__click_button_post(test_client, '/register', 'continue_button')
        assert response.status_code == 200

    def test_login_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.get('/login')
        html = response.data.decode()
        assert 'login_button' in html, f'Should contain login button'
        assert 'cancel_button' in html, f'Should contain cancel button'
        assert 'forgot_password_button' in html, f'Should contain forgot password button'
        assert response.status_code == 200

    def test_login_post(self, test_client):
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

    def test_login_password_recovery(self, test_client):
        response = test_client.get('/login/reset')
        assert response.status_code == 200, f'{response.data.decode()}'

    def test_forgot_password_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is requested (GET)
        THEN check that the response is valid
        """
        response = test_client.get('/login/reset')
        assert response.status_code == 200, f'{response.data.decode()}'

    def test_forgot_password_post(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/' (homepage) is post (POST)
        THEN check that the response is valid
        """
        data = dict()
        data['email'] = self.test_account_info['email']

        # test when user click 'Send Recovery Link' button in recover.html
        response = self.__click_button_post(test_client, '/login/reset', 'send_recovery_link_button')
        assert response.status_code == 200  # render template

        # test when user click 'Resend' button in recover.html
        response = self.__click_button_post(test_client, '/login/reset', 'resend_button')
        assert response.status_code == 200 # render template

    def __click_button_post(self, test_client, url, button, data=None):
        if data: # with data
            data[button] = button
            return test_client.post(url, data=data)

        # only button
        return test_client.post(url, data={button: button})


