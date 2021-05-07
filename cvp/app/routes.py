"""Covid-19 Vaccine Passport Application"""

from flask import render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from cvp.features.transform import generate_QR_code
from cvp.app.services.email_service import *
from cvp.app.utils import *
from datetime import datetime
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
            if 'vaccine_rec' not in request.files:
                error_msg = 'file is not uploaded.'

            if not error_msg:
                uploads_dir = 'dataset/processed/upload_vaccine_record'

                # Create a new directory for the upload
                os.makedirs(uploads_dir, exist_ok=True)
                os.makedirs(PROFILE_IMAGE_PATH, exist_ok=True)
                error_msg = invalid_register_input(email, password, confirm_password)

                if not error_msg: # no error in entered information
                    vaccine_rec_pic = request.files["vaccine_rec"]
                    filename = secure_filename(vaccine_rec_pic.filename)
                    profile_pic = request.files["profile_pic"]

                    # Save file(s) to local folder
                    if vaccine_rec_pic:
                        vaccine_rec_pic.save(os.path.join(uploads_dir, filename))
                        extracted_rec = model.predict(filename, folder_path=uploads_dir)

                    # Remove File after OCR returned the prediction
                        os.remove(os.path.join(uploads_dir, filename))
                    else:
                        extracted_rec = None

                    session['email'] = email
                    session['password'] = password
                    session['extracted_record'] = extracted_rec

                    # Get photo name and convert it into type .png
                    if profile_pic:
                        pic_name = secure_filename(profile_pic.filename.split('.')[0] + f'{datetime.now().strftime("%H:%M:%S")}' + '.png')
                        temp_save_path = os.path.join(PROFILE_IMAGE_PATH, pic_name)
                        profile_pic.save(temp_save_path)
                    else:
                        pic_name = secure_filename(DEFAULT_PROFILE_PHOTO)

                    session['profile_photo'] = pic_name

                    return render_template('create_account.html', info=f'Welcome', profpic='profile_pic/' + pic_name)

            # error found in entered information
            return render_template("uploading_of_document.html", invalid_input=error_msg, email=email)

        elif request.form.get('confirm_button'): # process for case(3)
            # obtain all requested information from frontend
            confirmed_data = request.form.to_dict('confirmed_data')

            # check CDC database at this point
            valid_rec = check_cdc(confirmed_data, session['email'])

            if valid_rec:  # send confirmed account information to database and record them.
                # insert this data to db
                new_id = generate_account(session, confirmed_data)

                # Upload profile photo to AWS S3 Bucket
                profile_photo = session['profile_photo']
                temp_path = os.path.join(PROFILE_IMAGE_PATH, profile_photo)
                if os.path.exists(temp_path) and profile_photo != DEFAULT_PROFILE_PHOTO:
                    new_photo_name = f'{str(new_id)}.png'
                    os.rename(temp_path, os.path.join(PROFILE_IMAGE_PATH, new_photo_name))
                    upload_to_s3(new_photo_name, PROFILE_IMAGE_PATH)
                    os.remove(os.path.join(PROFILE_IMAGE_PATH, new_photo_name))

                # rename the temp profile pic to a unique name based on the account's information

                return redirect(url_for('login'))
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
                url_token = encode_token(acc[2], salt=profile_key)
                session['logged_in'] = True
                session['url'] = url_token
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

                # send email with setup link
                send_password_recovery_email(recover_url, email)
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
    email, reset_token = renew_token(token, salt=recovery_key, time=3600)  # 1 hours
    if not email:  # could not decode the email (the link has expired)
        return render_template('login.html', error_msg='URL Expired.')

    if request.method == 'POST':
        if request.form.get('reset_button'): # process of case(2)
            password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if valid_password(password) and password == confirm_password:  # save to database
                if update_password(password, email=email):
                    return f'password reset confirmation with login button to back to login page'
                else:
                    return f'Update Password Failed'

    return render_template('password_reset.html', token=reset_token) # process of case(1)


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

    user_profile, is_tampered = get_profile(account_id)

    # Grab user's profile picture from AWS S3 Bucket
    try:
        profile_photo = str(account_id) + '.png'
        download_from_s3(profile_photo,
                         PROFILE_IMAGE_PATH)  # Will throw exception if file is not found on AWS S3 Bucket
        pic = 'profile_pic/' + profile_photo
    except FileNotFoundError:
        pic = 'profile_pic/Smiley.png'

    if request.method == 'POST':  # process for case(1)
        if request.form.get('settings_button'):
            return redirect(url_for('settings', token=profile_token, pic=pic))
        if request.form.get('sign_out_button'):
            session.pop('logged_in', None)
            for path in (PROFILE_IMAGE_PATH, QR_IMAGE_PATH):
                clean_up_images(str(account_id) + '.png', path)

            return redirect(url_for('homepage'))
    # process for case(2) (GET)

    # encrypt account id to be shared through qr or url
    sharing_token = encode_token(account_id, salt=sharing_profile_key)
    sharing_url = url_for('shared_profile', token=sharing_token, _external=True)

    # generate qr
    generate_QR_code(sharing_url, str(account_id), save=True, save_folder='static/QR_Code')
    msg = session['message'] if session.get('message') else ''
    session['qr'] = f'{account_id}.png'
    session['sharing_url'] = sharing_url




    return render_template('profile.html', profile=user_profile, pic=pic, token=profile_token, msg=msg)


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
            first_name = request.form.get('user_name')
            email = request.form.get('username_email')

            # save the info with database with account_id
            error_msg = update_account(account_id, first_name, email)

            if not error_msg:
                session['message'] = 'Saved change successfully'
                return redirect(url_for('profile', token=token)) # return to setting or profile with message

        elif request.form.get('password_save_button'): # Process of Case(3)
            current_pass = request.form.get('current_password')
            new_pass = request.form.get('new_password')
            conf_pass = request.form.get('confirm_password')

            # check if the current_pass is in the database
            acc = authenticate(current_pass, account_id=account_id)

            if type(acc) == tuple:  # authentication succeeded
                if new_pass == conf_pass: # check new password and confirm password
                    # update database
                    update_password(new_pass, acc=account_id)
                    session['message'] = 'Saved change successfully'
                    return redirect(url_for('profile', token=token)) # return to setting or profile with message

                else:
                    error_msg = 'New Password and Confirm Password did not match.'

            elif not error_msg: # failed authentication with the 'current password'
                error_msg = 'Current password did not match.'

        elif request.form.get('back_button'): # process of case(4)
            return redirect(url_for('profile', token=token))

        elif request.form.get('sign_out_button'):
            session.pop('logged_in', None)
            for path in (PROFILE_IMAGE_PATH, QR_IMAGE_PATH):
                clean_up_images(str(account_id) + '.png', path)

            return redirect(url_for('homepage'))

        # return with error message for POST
        return render_template('settings.html', token=token, error=error_msg)

    return render_template('settings.html', token=token)  # process of case(1) (GET)


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
