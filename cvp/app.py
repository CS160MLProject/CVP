"""Covid-19 Vaccine Passport Application"""

from flask import Flask
from flask import render_template, request, redirect, url_for
import re

from cvp.features.transform import generate_hash

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    """
    Homepage of this website with login and register option.
    :return: redirect to register page or login page based on user's option.
    """
    if request.method == 'POST':  # user clicked the option buttons
        if request.form.get('register_button'):  # user clicked the register button
            return redirect(url_for('register'))
        if request.form.get('login_button'):  # user clicked the login button
            return redirect(url_for('login'))
    return render_template('homepage.html', title='this is title of homepage', body='option to register and login')


@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Invoked when (1)register button is clicked from homepage.html
        (2)continue button is clicked in uploading_of_document.html
        (3)confirm button is clicked in create_account.html.
    Obtain values from the user and validate email and password and confirm password.
    Obtain file from html post for profile picture and vaccine record.
    :return: create_account page with user information of OCRed text.
    """
    error_msg = None
    if request.method == "POST":
        if request.form.get('continue_button'): # if continue button is clicked in the uploading_of_document.html
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')  # confirmation password named confirm_password
            # profile_pic = request.files["profile_pic"]
            # vaccine_rec_pic = request.files["vaccine_rec"]
            # pass this vaccine_rec_pic photo to perform OCR
            # extracted_rec = ocr(vaccine_rec_pit)
            extracted_rec = "Sample data that demonstrates OCRed text information " \
                            "to be displayed to user in create_acount.html"

            #error_msg = __invalid_register_input(email, password, confirm_password)
            if not error_msg:
                # pass extracted_rec as well
                return render_template('create_account.html', info=f'Welcome {email=}, {password=}, {confirm_password=} !'
                                                                   f'\n Are these info correct? '
                                                                   f'\n --OCRed Info \n {extracted_rec}')

            if error_msg:
                return render_template("uploading_of_document.html", invalid_input=error_msg)
        elif request.form.get('confirm_button'):
            # check CDC database at this point
            temp_CDC = True
            if temp_CDC:  # send confirmed account information to database and record them.
                return redirect(url_for('profile'))
            else:  # the information is not in CDC database, return (something_went_wrong.html)
                pass
    # initial default by GET for /register
    return render_template("uploading_of_document.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Invoked when log in button is clicked in homepage.
    Check entered login information with database.
    :return: login page with error message if any error presents, else return profile page.
    """
    error = 'Please enter required fields.'
    if request.method == 'GET':  # for the first time of page request.
        return render_template('login.html')

    if request.method == 'POST':
        if request.form.get("login_button"):
            email = request.form.get('email')
            # password = request.form.get('password')
            # hashed_pass, _ = generate_hash(password)

            # check database with email and hashed_pass
            success = True
            if success:  # login
                # here, get profile info to show profile
                # obtain user account id from database with entered email
                account_id = 12345
                return redirect(url_for('profile', account_id=account_id))

            else:  # not in database or typo
                error = 'Invalid email or password'
        if request.form.get("cancel_button"):
            return render_template('login.html')

    return render_template('login.html', error=error)


@app.route('/profile_<account_id>', methods=['GET', 'POST'])
def profile(account_id):
    """
    Invoked when login is succeeded.
    Also invoked when 'confirm button is clicked in create account page.
    First main page of application.
    :return: profile page
    """
    # get user info with account_id
    user_info = 'this is your profile but who is this? \nYou cheated.'
    return render_template('profile.html', profile=user_info)


def __invalid_register_input(email, password, confirm_password):
    """
    Validate entered register information is correct or not.
    :param email: email address.
    :param password: password.
    :param confirm_password: confirm password.
    :return: error_msg if there is any error, else None
    """
    error_msg = None

    if email == '' or password == '':
        error_msg = 'Please enter required fields.'

    elif __valid_email(email):  # valid email
        if password != confirm_password:  # fail. password did not match
            error_msg = 'Password did not match!'
    else:  # invalid email
        error_msg = 'Invalid email'

    return error_msg


def __valid_email(email):
    """
    Validate entered email.
    :param email: email address entered by user.
    :return: True if this email is valid.
    """
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(email_regex, email):  # if valid email
        return True
    return False


if __name__ == '__main__':
    app.run(debug=True)
