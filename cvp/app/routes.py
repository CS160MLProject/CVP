"""Covid-19 Vaccine Passport Application"""

from flask import render_template, request, redirect, url_for, session
from cvp.features.transform import generate_QR_code
from cvp.app.services.email_service import *
import itsdangerous
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
    print(app.url_map)
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
    error_msg = ''
    if request.method == 'POST':
        if request.form.get("login_button"): # process for case(2)
            email = request.form.get('email')
            password = request.form.get('password')

            if email == '' or password == '':
                error_msg = 'Please enter required fields.'

            # authentication of login with email and password
            acc = authenticate(password, email=email)

            if type(acc) == tuple:  # logged in
                # generate encrypted token to be url
                url_token = ts.dumps(acc[4], salt=profile_key)
                return redirect(url_for('profile', token=url_token))
            else: error_msg = acc # if authentication failed, show error message from authenticate()

            return render_template('login.html', error=error_msg) # login.html with error message
        if request.form.get('cancel_button'): # process for case(3)
            return redirect(url_for('homepage'))

        if request.form.get('forgot_password_button'): # process for case(4)
            return redirect(url_for('forget_password')) # process for case(4)

        return render_template('login.html')

    # default. process for case(1)
    return render_template('login.html')


@app.route('/login/reset', methods=['GET', 'POST'])
def forget_password():
    """
    Invoked when (1)'Send email' is clicked in recover.html
        (2)'Resend Link' is clicked in a resend.html
    :return: (1)resend.html
        (2)resend.html
    """
    error_msg = ''
    if request.method == 'POST':
        if request.form.get('send_button') or request.form.get('resend_button'):
            if request.form.get('resend_button'):
                email = session['email']
            else:
                email = request.form.get('email')
                session['email'] = email

            # check if this email is in the database
            if is_user(email):
                # encrypt link to reset password
                token = ts.dumps(email, salt=recovery_key)
                recover_url = url_for('reset_password', token=token, _external=True)
                html = render_template('email/password_recovery.html', recover_url=recover_url)

                # send email with setup link
                subject = 'Password Reset Requested'
                send_email(subject, html, email)
                return render_template('resend.html')

            else: error_msg = f'Account was not found with this email.'

        return render_template('recover.html', error=error_msg) # return with error message

    # ---return html of Sign out pop up - 4 if implemented.
    return render_template('recover.html')


@app.route('/login/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        try:
            email = ts.loads(token, salt=recovery_key, max_age=3600) # 1 hours
            return render_template('password_reset.html')
        except itsdangerous.exc.SignatureExpired as link_expried:
            raise Exception(link_expried)

    if request.method == 'POST':
        if request.form.get('login_button'):
            return redirect(url_for('login'))

        if request.form.get('reset_button'):
            try:
                url_email = ts.loads(token, salt=recovery_key, max_age=3600) # 1 hour
                email = request.form.get('email')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')

                if email == url_email and password == confirm_password: # save to database
                    if update_password(email, password):
                        return f'password reset confirmation with login button to back to login page'
                    else: return f'Update Password Failed'

            except itsdangerous.exc.SignatureExpired as link_expried:
                raise Exception(link_expried)

    return redirect(url_for(login))


@app.route('/profile_<token>/settings', methods=['GET', 'POST'])
def change_account_profile(token):
    """
    Invoked when 'Save Changes' is clicked in a page of settings.
    :param token: user specific encoded token.
    :return: 1) nothing or promlpt to indicates that the saved successfully.
        2) error prompt to indicates that the info was not saved successfully.
    """
    account_id = ts.loads(token, salt=change_account_key)
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username_email')

        # save the info with database with account_id
        error_msg = None
        # error_msg = account_database_update(account_id, first_name, last_name, username)
        if not error_msg:
            return f'saved changes successfully'
        else:
            return f'error {error_msg}'

    # ---return Sign out pop up if implemented.
    return None


@app.route('/profile_<token>', methods=['GET', 'POST'])
def profile(token):
    """
    First main page of application.
    Invoked when (1)login button is clicked and succeeded in login.html
    :param token: user specific token encoded in login.
    :return: (1)profile.html with user profile, account information, sharing_url and name of qr file.
    """
    # decrypt token to get account_id
    account_id = ts.loads(token, salt=profile_key, max_age=900) # 15 min
    # get user info with account_id
    # user_record = get_user_rec_database(account_id)
    db = Database(db_path)
    try:
        user_record = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')[:-3]
        user_info = db.select('*', profile_table, f'User_Account_ID = \"{account_id}\"')
    finally:
        db.close_connection()

    # encrypt account id to be shared through qr
    token = ts.dumps(account_id, salt=sharing_profile_key)
    sharing_url = url_for('shared_profile', token=token, _external=True)
    print(sharing_url)

    # generate qr
    generate_QR_code(sharing_url, str(account_id), save=True)
    return render_template('profile.html', profile=user_record, account_info=user_info,
                           sharing_url=sharing_url, qr=f'{account_id}.png')


@app.route('/info_<token>', methods=['GET'])
def shared_profile(token):
    """
    Invoked when user open shared url.
    :param token: encrypted url for sharing info.
    :return: shared profile page.
    """
    if request.method == 'GET':
        try:
            # decode the token
            # get user's account id
            account_id = ts.loads(token, salt=sharing_profile_key, max_age=900) # 15 min
            print(account_id)
            # get user account information with account_id
            # user_record = db.select("*", 'profile', f'User_Account_ID = {account_id}')
            user_record = ''
            return render_template('shared_profile.html', user_record=user_record)
        except itsdangerous.exc.SignatureExpired as link_expried:
            raise Exception(link_expried)

    return render_template('shared_profile.html')


@app.route('/profile_<token>/setting/change_password', methods=['GET', 'POST'])
def change_password(token):
    """
    Change password of user account.
    Invoked when 'Save Change' is clicked in a page of Change Password in setting.
    :param token: user specific encoded token.
    :return: 1) nothing or prompt to indicates that the saved successfully.
        2) error prompt to indicates that the new password was not saved successfully.
    """
    if request.method == 'POST':
        current_pass = request.form.get('current_password')
        new_pass = request.form.get('new_password')
        conf_pass = request.form.get('confirm_password')

        account_id = ts.loads(token, salt=profile_key, max_age=900)  # 15 min

        # check if the current_pass is in the database
        acc = authenticate(current_pass, account_id=account_id)

        if type(acc) == tuple: # authentication succeeded
            if new_pass == conf_pass:
                # update database
                return f'baack to profile?'
            return f'New Password and Confirm Password did not match.'
        else:
            return f'unexpected error'

    # ---return change_pass.html as landing page.
    return render_template('change_pass.html')


if __name__ == '__main__':
    app.run()

