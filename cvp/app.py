"""Covid-19 Vaccine Passport Application"""

from flask import Flask
from flask import render_template, request
import re

from cvp.features.transform import generate_hash

app = Flask(__name__)


@app.route('/')
def homepage():
    """
    Homepage of this website with login and register option.
    :return: homepage.html with title and body for demo.
    """
    return render_template('homepage.html', title='this is title of homepage', body='option to register and login')


@app.route('/register', methods=["GET", "POST"])
def register_input():
    """
    Invoked when register button is clicked in homepage.
    :return: registration page of uploading_of_document
    """
    print(f'in register(), {request.method=}')
    return render_template('uploading_of_document.html')


@app.route('/register_confirm', methods=["GET", "POST"])
def register_create_account():
    """
    Invoked when register button is clicked with information of email, password, and confirm password.
    Obtain values from the user and validate email and password and confirm password.
    Obtain file from html post for profile picture and vaccine record.
    :return: create_account page with user information of OCRed text.
    """
    print(f'in register_confirm(), {request.method=}')
    error_msg = None
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # profile_pic = request.files["profile_pic"]
        # vaccine_rec_pic = request.files["vaccine_rec"]
        # pass this vaccine_rec_pic photo to perform OCR
        # extracted_rec = ocr(vaccine_rec_pit)

        error_msg = __invalid_register_input(email, password, confirm_password)
        if not error_msg:
            # pass extracted_rec as well
            return render_template('create_account.html', info=f'Welcome {email=}, {password=}, {confirm_password=} !'
                                                               f'\n Are these info correct? '
                                                               f'\n --OCRed Info')

    return render_template("uploading_of_document.html", invalid_input=error_msg)


@app.route('/login', methods=['GET', 'POST'])
def login_input():
    """
    Invoked when log in button is clicked in homepage.
    Check entered login information with database.
    :return: login page with error message if any error presents, else return profile page.
    """
    error = 'Please enter required fields.'
    if request.method == 'GET': # for the first time of page request.
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form.get('email')
        #password = request.form.get('password')
        #hashed_pass, _ = generate_hash(password)

        # check database with email and hashed_pass
        success = True
        if success: # login
            # here, get profile info to show profile
            return render_template('profile.html', profile='this is your profile but who is this?'
                                                           '\nYou cheated.')

        else: # not in database or typo
            error = 'Invalid email or password'

    return render_template('login.html', error=error)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    Invoked when login is succeeded.
    First main page of application.
    :return: profile page
    """
    return render_template('profile.html')


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

    elif __valid_email(email): # valid email
        if password != confirm_password:  # fail. password did not match
            error_msg = 'Password did not match!'
    else: # invalid email
        error_msg = 'Invalid email'

    return error_msg


def __valid_email(email):
    """
    Validate entered email.
    :param email: email address entered by user.
    :return: True if this email is valid.
    """
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(email_regex, email): # if valid email
        return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
