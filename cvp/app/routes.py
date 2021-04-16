"""Covid-19 Vaccine Passport Application"""

from flask import render_template, request, redirect, url_for, session
from cvp.features.transform import generate_QR_code
from cvp.app.services.email_service import *
from cvp.app.utils import *
from app import app


@app.route('/', methods=['GET', 'POST'])
def homepage():
    """
    Homepage of this website with login and register option.
    Invoked when (1)Website homepage url is entered to show homepage.html
        (2)register button is clicked in homepage.html
        (3)login button is clicked in homepage.html.
    :return: (1)homepage.html
        (2)redirect to register function
        (3)redirect to login function
    """
    if request.method == 'POST':  # user clicked the option buttons
        if request.form.get('register_button'):  # process for case(2)
            return redirect(url_for('register'))
        if request.form.get('login_button'):  # process for case(3)
            return redirect(url_for('login'))
    # default. process for case(1)
    return render_template('index.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Invoked when (1)register button is clicked from homepage.html
        (2)continue button is clicked in uploading_of_document.html
        (3)confirm button is clicked in create_account.html.
    :return: (1)uploading_of_document.html
        (2)create_account page with user information of OCRed text if no error
            else uploading_of_document.html with error message.
        (3)success_welcome.html if registered successfully else Error message (page).
    """
    if request.method == "POST":
        if request.form.get('continue_button'): # process for case(2)
            error_msg = None
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')  # confirmation password named confirm_password
            # profile_pic = request.files["profile_pic"]
            if 'vaccine_rec' not in request.files:
                error_msg = 'file is not uploaded.'

            if not error_msg:
                error_msg = invalid_register_input(email, password, confirm_password)
                if not error_msg: # no error in entered information
                    vaccine_rec_pic = request.files["vaccine_rec"]
                    # vaccine_rec_pic = 'Vaccine_1.png' # to test
                    extracted_rec = model.predict(vaccine_rec_pic)
                    session['email'] = email
                    session['password'] = password
                    session['extracted_record'] = extracted_rec
                    return render_template('create_account.html', info=f'Welcome')

            # error found in entered information
            return render_template("uploading_of_document.html", invalid_input=error_msg)

        elif request.form.get('confirm_button'): # process for case(3)
            # obtain all requested information from frontend
            confirmed_data = request.form.to_dict('confirmed_data')

            # check CDC database at this point
            valid_rec = check_cdc(confirmed_data)

            if valid_rec:  # send confirmed account information to database and record them.
                # insert this data to db
                generate_account(session, confirmed_data)
                return render_template('success_welcome.html', success="Success! Welcome.")
            else:  # the information is not in CDC database, return (something_went_wrong.html)
                error_msg = 'Something went wrong'
                return f'<h1> {error_msg} <h1>'
    # initial default by GET for /register
    return render_template("uploading_of_document.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Invoked when (1)login button is clicked in homepage.html
        (2)login button is clicked in login.html
        (3)cancel button is clicked in login.html.
        (4)forgot password is clicked in login.html.
    :return: (1)login.html
        (2)redirect to profile function if logged in successfully else login.html with error message
        (3)redirect to homepage function
        (4)redirect to reset password html.
    """
    if request.method == 'POST':
        error_msg = ''
        if request.form.get("login_button"): # process for case(2)
            email = request.form.get('email')
            password = request.form.get('password')

            # authentication of login with email and password
            acc = authenticate(password, email=email)

            if type(acc) == tuple:  # logged in
                # generate encrypted token to be url
                url_token = encode_token(acc[4], salt=profile_key)
                session['logged_in'] = True
                return redirect(url_for('profile', token=url_token))

            elif not error_msg: error_msg = acc # if authentication failed, show error message from authenticate()

        if request.form.get('cancel_button'): # process for case(3)
            return redirect(url_for('homepage'))

        if request.form.get('forgot_password_button'): # process for case(4)
            return redirect(url_for('forgot_password')) # process for case(4)

        return render_template('login.html', error=error_msg)  # login.html with error message

    # default. process for case(1)
    return render_template('login.html')


@app.route('/login/reset', methods=['GET', 'POST'])
def forgot_password():
    """
    Invoked when (1)'Send Recovery Link' is clicked in recover.html
        (2)'Resend Link' is clicked in a resend.html
    :return: (1)resend.html if the email is in the database else return recover.html with error message.
        (2)resend.html
    """
    if request.method == 'POST':
        error_msg = ''
        if request.form.get('send_recovery_link_button') or request.form.get('resend_button'): # process of case(1), (2)
            if request.form.get('resend_button'): # if case(2)
                email = session['email']

            else: # if case(1)
                email = request.form.get('email')
                session['email'] = email

            # check if this email is in the database
            if type(error_msg := is_user(email)) == tuple:
                # encrypt link to reset password
                token = encode_token(email, salt=recovery_key)
                recover_url = url_for('reset_password', token=token, _external=True)
                html = render_template('email/password_recovery.html', recover_url=recover_url)

                # send email with setup link
                send_password_recovery_email(html, email)
                return render_template('resend.html')

        return render_template('recover.html', error=error_msg) # return with error message (email is not in db)

    return render_template('recover.html') # process of case(1)


@app.route('/login/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset password. User recieve their specific link to reset password from the email.
    Invoked when (1)User clicked the link of password recovery in the email.
        (2)'Reset' button is clicked in the password_reset.html
    """
    email = decode_token(token, salt=recovery_key, time=3600)  # 1 hours
    if email: # process of case(1)
        return render_template('password_reset.html')

    if request.method == 'POST':
        if request.form.get('reset_button'): # process of case(2)
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if password == confirm_password:  # save to database
                if update_password(password, email=email):
                    return f'password reset confirmation with login button to back to login page'
                else:
                    return f'Update Password Failed'

    return redirect(url_for('login')) # link has expired


@app.route('/profile_<token>', methods=['GET', 'POST'])
def profile(token):
    """
    First main page of application.
    Invoked when (1)login button is clicked in login.html.
        (2)'settings_button' is clicked in profile.html.
    :param token: user specific token encoded in login.
    :return: (1)redirect to settings page.
        (2)profile.html with user profile, sharing_url and name of qr file.
    """
    account_id, profile_token = renew_token(token, salt=profile_key, time=900)  # 15 min
    if not account_id:  # could not decode the account_id (the link has expired)
        return render_template('login.html', error_msg='Logged out for certain time of inactivity.')

    if request.method == 'POST':  # process for case(1)
        if request.form.get('settings_button'):
            return redirect(url_for('settings', token=profile_token))
        if request.form.get('sign-out-profile'):
            session.pop('logged_in', None)
            return redirect(url_for('homepage'))
    # process for case(2) (GET)
    user_profile = get_profile(account_id)

    # encrypt account id to be shared through qr or url
    sharing_token = encode_token(account_id, salt=sharing_profile_key)
    sharing_url = url_for('shared_profile', token=sharing_token, _external=True)

    # generate qr
    generate_QR_code(sharing_url, str(account_id), save=True)
    return render_template('profile.html', profile=user_profile,
                           sharing_url=sharing_url, qr=f'{account_id}.png', token=profile_token)


@app.route('/profile_<token>/settings', methods=['GET', 'POST'])
def settings(token):
    """
    Settings page of application.
    Invoked when (1)'Settings' button is clicked in the profile.html
        (2)'Save Changes' button for account info is clicked in the settings.html
        (3)'Save Changes' button for password change is clicked in the settings.html
        (4)'Back' button is clicked in the settings.html
    :param token: user specific token encoded in login.
    :return: (1)settings.html that includes user's basic info(name, email) and a form to change password.
        (2)settings.html with success notice if new account info is changed successfully
            else settings.html with error message
        (3)settings.html with success notice if new password is changed successfully
            else settings.html with error message
        (4)profile.html
    """
    account_id, token = renew_token(token, salt=profile_key, time=900)  # 15 min
    if not account_id:  # could not decode the account_id (the link has expired)
        return render_template('login.html', error_msg='Logged out for certain time of inactivity.')

    if request.method == 'POST':
        error_msg = ''

        if request.form.get('profile_save'): # Process of Case(2)
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('username_email')

            # save the info with database with account_id
            error_msg = update_account(account_id, first_name, last_name, email)

            if not error_msg:
                return f'saved changes successfully' # return to setting or profile with message

        elif request.form.get('password_save'): # Process of Case(3)
            current_pass = request.form.get('current_password')
            new_pass = request.form.get('new_password')
            conf_pass = request.form.get('confirm_password')

            # check if the current_pass is in the database
            acc = authenticate(current_pass, account_id=account_id)

            if type(acc) == tuple:  # authentication succeeded
                if new_pass == conf_pass: # check new password and confirm password
                    # update database
                    update_password(new_pass, acc=account_id)
                    return f'back to profile?'
                else:
                    error_msg = 'New Password and Confirm Password did not match.'

            elif not error_msg: # failed authentication with the 'current password'
                error_msg = 'Current password did not match.'

        elif request.form.get('back_button'): # process of case(4)
            return redirect(url_for('profile', token=token))

        # return with error message for POST
        return render_template('settings.html', token=token, error=error_msg)

    return render_template('settings.html', token=token) # process of case(1) (GET)


@app.route('/info_<token>', methods=['GET'])
def shared_profile(token):
    """
    Invoked when user open shared link.
    :param token: encrypted url for sharing info.
    :return: shared profile page with dict formatted user record.
    """
    account_id = decode_token(token, salt=sharing_profile_key, time=900)
    if not account_id: # link has expried
        return f'404'
    # obtain user record
    user_record = get_profile(account_id)
    return render_template('shared_profile.html', user_record=user_record)


if __name__ == '__main__':
    app.run()

