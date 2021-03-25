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
    return render_template('homepage.html', title='this is title of homepage', body='option to register and login')


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
            # vaccine_rec_pic = request.files["vaccine_rec"]
            # pass this vaccine_rec_pic photo to perform OCR
            # extracted_rec = ocr(vaccine_rec_pit)
            extracted_rec = "Sample data that demonstrates OCRed text information " \
                            "to be displayed to user in create_acount.html"

            error_msg = __invalid_register_input(email, password, confirm_password)
            if not error_msg: # no error in entered information
                return render_template('create_account.html',
                                       info=f'Welcome {email=}, {password=}, {confirm_password=} !'
                                            f'\n Are these info correct? '
                                            f'\n --OCRed Info \n {extracted_rec}')

            if error_msg: # error found in entered information
                return render_template("uploading_of_document.html", invalid_input=error_msg)

        elif request.form.get('confirm_button'): # process for case(3)
            # check CDC database at this point
            valid_rec = True
            if valid_rec:  # send confirmed account information to database and record them.
                # pass confirmed OCRed text data to database as their passport info
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
            # password = request.form.get('password')
            password = 'temp'
            # hashed_pass, _ = generate_hash(password)

            # check database with email and hashed_pass
            success = True
            if success:  # login
                # here, get profile info to show profile
                # obtain user account id from database with entered email
                account_id = 12345
                return redirect(url_for('profile', account_id=account_id))
            elif email == '' or password == '':
                error = 'Please enter required fields.'
            elif not success:  # not in database or typo
                error = 'Invalid email or password'

        if request.form.get("cancel_button"): # process for case(3)
            return redirect(url_for('homepage'))
        return render_template('login.html', error=error)

    # default. process for case(1)
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def forget_password():
    """
    Invoked when 'Continue' is clicked in page of password recovery.
    :return: Prompt of saying 'link is sent to your email.'
    """
    if request.method == 'POST':
        email = request.form.get('email')
        recovery_url = 'temp/recovery'
        # send email with setup link
        # send(email, recovery_url)
        return f'A link has been sent to the email.'

    # ---return html of Sign out pop up - 4 if implemented.
    return None


@app.route('/profile_<account_id>/settings', methods=['GET', 'POST'])
def change_account_profile(accont_id):
    """
    Invoked when 'Save Changes' is clicked in a page of settings.
    :return: 1) nothing or prompt to indicates that the saved successfully.
        2) error prompt to indicates that the info was not saved successfully.
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username_email')

        # save the info with database with account_id
        error_msg = None
        # error_msg = account_database_update(account_id, first_name, last_name, username)
        if not error_msg:
            return f'saved changes succsessfully'
        else:
            return f'error {error_msg}'

    # ---return Sign out pop up if implemented.
    return None

@app.route('/profile_<account_id>', methods=['GET', 'POST'])
def profile(account_id):
    """
    First main page of application.
    Invoked when (1)login button is clicked and succeeded in login.html
    :return: (1)profile.html with user information
    """
    # get user info with account_id
    user_info = f'this is your profile but who is this? \nYou cheated.'
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
