"""Covid-19 Vaccine Passport Application"""

from flask import render_template, request, redirect, url_for
from utils import *
from cvp.features.transform import generate_hash, generage_QR_code
from utils import ts
from app import *
import sqlite3
import hmac
from services.email_service import *
from base64 import b64decode


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
    return render_template('index.html', title='this is title of homepage', body='option to register and login')


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
                vaccine_rec_pic = request.files["vaccine_rec"]
                extracted_rec = model.predict(vaccine_rec_pic)
                error_msg = invalid_register_input(email, password, confirm_password)
                if not error_msg: # no error in entered information
                    return render_template('create_account.html',
                                           info=f'Welcome {email=}, {password=}, {confirm_password=} !'
                                                f'\n Are these info correct? '
                                                f'\n --OCRed Info \n {extracted_rec}')

            # error found in entered information
            return render_template("uploading_of_document.html", invalid_input=error_msg)

        elif request.form.get('confirm_button'): # process for case(3)
            # obtain all requested information from frontend
            confirmed_data = request.form.to_dict('confirmed_data')

            # check CDC database at this point
            valid_rec = check_cdc(confirmed_data)

            if valid_rec:  # send confirmed account information to database and record them.
                # insert this data to db
                db = Database(db_path)
                try:

                    new_account_id = db.select(values='count(account_ID)', table_name=account_table)
                    account_data = list(confirmed_data.values())
                    # align confirmed data to the order of schema of db

                    # handle exception here
                    db.create_connection(db_path)
                    db.insert(tuple(account_data), account_table)
                except sqlite3.Error as e:
                    raise Exception(e)
                finally:
                    db.close_connection()

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
    :return: (1)login.html
        (2)redirect to profile function if logged in successfully else login.html with error message
        (3)redirect to homepage function
    """
    if request.method == 'POST':
        error = None
        if request.form.get("login_button"): # process for case(2)
            email = request.form.get('email')
            password = request.form.get('password')

            email = 'margaret.hall@patient.abc.com'
            password = 'margarethall'

            if email == '' or password == '':
                error = 'Please enter required fields.'

            # check database with email and hashed_pass
            db = Database(db_path)
            try:
                db.create_connection(db_path)
                acc = db.select('*', account_table, f'Email = \"{email}\"')
            except sqlite3.Error as e:
                raise Exception(e)
            finally:
                db.close_connection()

            print(acc)
            db_password, db_salt = b64decode(acc[0][3]), b64decode(acc[0][5])
            hashed_pass, _ = generate_hash(password=password, salt=db_salt)
            if not error and acc: # if this is in database, check password
                if hmac.compare_digest(hashed_pass, db_password): # login
                    url_token = ts.dumps(acc[0][4], salt=profile_key)
                    return redirect(url_for('profile', token=url_token))
                else: # incorrect password
                    error = 'Password did not match'
            if not error and not acc: # this email is not in database
                error = 'Invalid email'

        if request.form.get('cancel_button'): # process for case(3)
            return redirect(url_for('homepage'))

        if request.form.get('forgot_password_button'):
            return redirect(url_for('forget_password'))

        return render_template('login.html', error=error)

    # default. process for case(1)
    return render_template('login.html')


@app.route('/login/reset', methods=['GET', 'POST'])
def forget_password():
    """
    Invoked when 'Continue' is clicked in a page of password recovery.
    :return: Prompt of saying 'link is sent to your email.'
    """
    if request.method == 'POST':
        if request.form.get('send_button'):
            subject = 'Password Reset Requested'
            email = request.form.get('email')
            token = ts.dumps(email, salt=recovery_key)
            recover_url = url_for('reset_password', token=token, _external=True)
            html = render_template('email/password_recovery.html', recover_url=recover_url)
            # send email with setup link
            send_email(email, subject, html)
            return f'A link has been sent to the email.'

    # ---return html of Sign out pop up - 4 if implemented.
    return render_template('recovery.html')


@app.route('/login/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        try:
            email = ts.loads(token, salt=recovery_key, max_age=43200) # 12 hours
            return render_template('password_reset.html')
        except:
            return f'404'

    if request.method == 'POST':
        if request.form.get('login_button'):
            return redirect(url_for('login'))

        if request.form.get('reset_button'):
            url_email = ts.loads(token, salt=recovery_key, max_age=43200)
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if email == url_email and password == confirm_password: # save to database
                # account_change_pass(email, password)
                new_pass, new_salt = generate_hash(password)
                # db.update((new_pass, new_salt), ('Password', 'Salt'), 'account')
                return f'password reset confirmation with login button to back to login page'

    return redirect(url_for(login))


@app.route('/profile_<token>/settings', methods=['GET', 'POST'])
def change_account_profile(token):
    """
    Invoked when 'Save Changes' is clicked in a page of settings.
    :param account_id: account's id.
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
    :return: (1)profile.html with user information
    """
    # decrypt token to get account_id
    account_id = ts.loads(token, salt=profile_key, max_age=900) # 15 min
    # get user info with account_id
    # user_record = get_user_rec_database(account_id)
    db = Database(db_path)
    try:
        db.create_connection(db_path)
        user_record = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')
        user_info = db.select('*', profile_table, f'User_Account_ID = \"{account_id}\"')
    except sqlite3.Error as e:
        raise Exception(e)
    finally:
        db.close_connection()

    # encrypt account id to be shared through qr
    token = ts.dumps(account_id, salt=sharing_profile_key)
    sharing_url = url_for('shared_profile', token=token, _external=True)
    print(sharing_url)
    # qr = sharing_qr(sharing_url)
    qr = generage_QR_code(sharing_url, '')
    return render_template('profile.html', profile=user_record, account_info=user_info, sharing_url=sharing_url)


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
            user_record = 'record'
            return render_template('shared_profile.html', user_record=user_record)
        except:
            return f'404'

    return f'404'


@app.route('/profile_<account_id>/setting/change_password', methods=['GET', 'POST'])
def change_password(account_id):
    """
    Change password of user account.
    Invoked when 'Save Change' is clicked in a page of Change Password in setting.
    :param account_id: account's id.
    :return: 1) nothing or prompt to indicates that the saved successfully.
        2) error prompt to indicates that the new password was not saved successfully.
    """
    if request.method == 'POST':
        current_pass = request.form.get('current_password')
        new_pass = request.form.get('new_password')
        conf_pass = request.form.get('confirm_password')

        # check if the current_pass is in the database
        hashed_pass, _ = generate_hash(current_pass)
        # check database with email and hashed_pass
        # success = db_login(account_id, hashed_pass)
        success = True
        if not success: # current password is not correct.
            error_msg = f'Current Password is not correct.'
            return error_msg # return change_pass.html with error msg

        # check if new password and confirm password match.
        success = new_pass == conf_pass
        if not success: # they does not match
            error_msg = f'New Password and Confim Password did not match.'
            return error_msg # return change_pass.html with error msg

        # success, change password
        # db_account_change_pass(new_password)
        return None # return change_pass.html with success confirmation.

    # ---return change_pass.html as landing page.
    return None


if __name__ == '__main__':
    app.run(debug=True)
