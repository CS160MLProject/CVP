import re
from cvp.app.routes import app
from cvp.app.utils import get_profile


class TestRoutes:

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
        assert response.status_code == 200

        response = self.__click_button_post(test_client, '/', 'register_button')
        assert response.status_code == 302  # redirect

        response = self.__click_button_post(test_client, '/', 'login_button')
        assert response.status_code == 302

    def test_register_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/register' is GET
        THEN check that the response is valid
        """
        response = test_client.get('/register')
        assert response.status_code == 200, f'{response.data.decode()}'

    def test_register_post(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/register' is POST
        THEN check that the response is valid
        """
        response = test_client.post('/register')
        assert 'continue_button' in response.data.decode(), f'Should contain continue button'
        assert response.status_code == 200

        # have to pass file for register post.
        # response = self.__click_button_post(test_client, '/register', 'confirm_button')
        # assert response.status_code == 200

    def test_login_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/login' is GET
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
        GIVEN a flask app configuration and login information as test client
        WHEN the '/login' is POST
        THEN check that the response is valid
        """
        response = test_client.post('/login')
        html = response.data.decode()
        assert 'login_button' in html, f'Should contain login button'
        assert 'cancel_button' in html, f'Should contain cancel button'
        assert 'forgot_password_button' in html, f'Should contain forgot password button'
        assert response.status_code == 200

        # login test of success
        test_account_info = self.__get_test_account_info()
        test_account_info['password'] = \
            f'{test_account_info["record_first_name"]}{test_account_info["record_last_name"]}'.lower()
        assert response.status_code == 200

        # login test of fail with wrong email
        wrong_email = 'doesnotexist@test.com'
        test_account_info['email'] = wrong_email
        response = self.__click_button_post(test_client, '/login', 'login_button', data=test_account_info)
        assert 'Account was not found' in response.data.decode()

        # login test of cancel button
        response = self.__click_button_post(test_client, '/login', 'cancel_button', data=test_account_info)
        assert response.status_code == 200  # render template

        # login test of forgot password button
        response = self.__click_button_post(test_client, '/login', 'forgot_password_button')
        assert response.status_code == 302

    def test_forgot_password_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/login/reset' is GET
        THEN check that the response is valid
        """
        response = test_client.get('/login/reset')
        assert response.status_code == 200, f'{response.data.decode()}'

    def test_forgot_password_post(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/login/reset' is POST
        THEN check that the response return render template of corresponding pages correctly.
        """
        data = dict()
        test_account_info = get_profile(1)
        data['email'] = test_account_info['email']

        # test when user click 'Send Recovery Link' button in recover.html
        response = self.__click_button_post(test_client, '/login/reset', 'send_recovery_link_button', data=data)
        assert response.status_code == 200  # render template

        # test when user click 'Send Recovery Link' button with incorrect email
        data['email'] = 'wrong@email.com'
        response = self.__click_button_post(test_client, '/login/reset', 'send_recovery_link_button', data=data)
        assert 'Account was not found with this email.' in response.data.decode()

        # test shen user click 'Resend Link' button in recover.html
        response = self.__click_button_post(test_client, '/login/reset', 'resend_button')
        assert response.status_code == 200

    def test_reset_password_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/login/reset' is GET
        THEN check that the response return render template of corresponding pages correctly.
        """
        data = dict()
        test_account_info = get_profile(1)
        data['email'] = test_account_info['email']

        response = self.__click_button_post(test_client, '/login/reset', 'send_recovery_link_button', data=data)
        '''
        This response does not contain url. 
        TODO - how to obtain password reset url that is sent to email?
        '''

    def test_profile_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/profile' is GET
        THEN check if the profile function return render template or redirect of corresponding pages correctly.
        """
        token, _ = self.__login(test_client)
        response = test_client.get(f'/profile_{token}')
        assert response.status_code == 200  # redirect

    def test_profile_post(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/profile' is POST
        THEN check if the profile function return render template or redirect of corresponding pages correctly.
        """
        token, _ = self.__login(test_client)

        # test setting button
        response = self.__click_button_post(test_client, f'/profile_{token}', 'settings_button')
        assert response.status_code == 302

        # test sign out button
        response = self.__click_button_post(test_client, f'/profile_{token}', 'sign_out_button')
        assert response.status_code == 302

    def test_settings_get(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/profile_<token>/settings' is GET
        THEN check if the settings function's response is valid.
        """
        token, _ = self.__login(test_client)

        response = test_client.get(f'/profile_{token}/settings')
        assert response.status_code == 200  # render template

    def test_settings_post(self, test_client):
        """
        Need change the way to detect button for same web page.
        GIVEN a flask app configuration as test client
        WHEN the '/profile_<token>/settings' is POST
        THEN Test if the settings function redirects to profile after performing the operation.
        """
        token, test_account_info = self.__login(test_client)

        # test profile_save button
        saving_data = dict()
        saving_data['user_name'] = test_account_info['user_name']
        saving_data['username_email'] = test_account_info['email']
        response = self.__click_button_post(test_client, f'/profile_{token}', 'settings_button')
        response = self.__click_button_post(test_client, f'/profile_{token}/settings',
                                            'profile_save', data=test_account_info)
        assert response.status_code == 200  # redirect
        # assert 'Saved change successfully' in response.data.decode(), f'Should return with saved notice.'

        # test password_save button
        saving_data = dict()
        saving_data['current_password'] = saving_data['new_password'] = \
            saving_data['confirm_password'] = test_account_info['password']
        response = self.__click_button_post(test_client, f'/profile_{token}', 'settings_button')
        response = self.__click_button_post(test_client, f'/profile_{token}/settings',
                                            'password_save_button', data=test_account_info)
        assert response.status_code == 200  # redirect
        # assert 'Saved change successfully' in response.data.decode(), f'Should return with saved notice.'

        # test back_button
        response = self.__click_button_post(test_client, f'/profile_{token}/settings',
                                            'back_button', data=test_account_info)
        assert response.status_code == 200  # redirect

        # test sign_out button
        response = self.__click_button_post(test_client, f'/profile_{token}/settings',
                                            'sign_out_button', data=test_account_info)
        assert response.status_code == 200  # redirect

    def test_shared_profile(self, test_client):
        """
        GIVEN a flask app configuration as test client
        WHEN the '/info_<token>' is GET
        THEN Test if the shared profile function return render template to the shared_profile.html
        """
        token, test_account_info = self.__login(test_client)
        response = test_client.get(f'/profile_{token}')
        token = self.__get_sharing_url(response.data.decode())
        response = test_client.get(f'/info_{token}')
        assert response.status_code == 200  # redirect

    def __login(self, test_client):
        """
        Helper for test client to login.
        :param test_client: test_client.
        :return: token of this profile and test account info in form of dict.
        """
        url = '/login'
        button = 'login_button'
        test_account_info = self.__get_test_account_info()
        test_account_info['password'] = \
            f'{test_account_info["record_first_name"]}{test_account_info["record_last_name"]}'.lower()

        login = self.__click_button_post(test_client, url, button, data=test_account_info)
        token = self.__get_profile_url(login.data.decode())
        return token, test_account_info

    def __click_button_post(self, test_client, url, button, data=None):
        """
        Helper for test client to click a button.
        :param test_client: test client.
        :param url: url of the button is placed.
        :param button: the button name to be clicked.
        :param data: data to be passed as post other than the button.
        :return: test_client post.
        """
        if data:  # with data
            data[button] = True
            return test_client.post(url, data=data, follow_redirects=True)

        # only button
        return test_client.post(url, data={button: True})

    def __get_test_account_info(self):
        """
        Helper to get test account profile (account_id = 1)
        """
        return get_profile(1)

    def __get_pass_recovery_url(self, data):
        """
        Helper to extract password recovery url from the data returned as response.
        """
        pattern = r'/login/reset/([\w.-]+)'
        found = re.findall(pattern, data)
        return found[0]

    def __get_profile_url(self, data):
        """
        Helper to extract profile url from the data returned as response.
        """
        pattern = r'profile_([\w.-]+)'
        found = re.findall(pattern, data)
        return found[0]

    def __get_sharing_url(self, data):
        """
        Helper to extract sharing url from the data returned as response.
        """
        pattern = r'info_([\w.-]+)'
        found = re.findall(pattern, data)
        return found[0]