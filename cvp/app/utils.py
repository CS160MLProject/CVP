"""Utilities for routes.py"""
from app import *
from credentials import *
from cvp.data.rel_database import Database
from cvp.features.transform import generate_hash
import itsdangerous
from itsdangerous import URLSafeTimedSerializer
from base64 import b64decode, b64encode
import hmac
import re
import os

ts = URLSafeTimedSerializer(secret_key=secret_key)


def invalid_register_input(email, password, confirm_password):
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

    elif valid_email(email):  # valid email
        if password != confirm_password:  # fail. password did not match
            error_msg = 'Password did not match!'
    else:  # invalid email
        error_msg = 'Invalid email'

    return error_msg


def valid_email(email):
    """
    Validate entered email.
    :param email: email address entered by user.
    :return: True if this email is valid.
    """
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(email_regex, email):  # if valid email
        return True
    return False

def valid_password(password:str):
    """Validate password. Password must follow these conditions:
    - 8 characters minimum
    - 21 characters maximum
    - At least 1 uppercase character
    - At least 1 lowercase character
    - Must contains at least 1 special character: @, $, !, %, *, #, ?, &

    Usage:

        >>> from cvp.app.utils import valid_password
        >>> bool_ = valid_password(password)

    Args:
        password (str): user registration password

    Returns:
        flag (bool): True if password matches all the conditions. False otherwise

    """
    pass_reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,21}$"
    if re.search(re.compile(pass_reg), password):
        return True
    return False


def get_file_ext(filename):
    """
    Get file extension and classify image or pdf.
    :param filename: filename or file path
    :return: group of file type (image or pdf). None if this is not supported.
    """
    _, ext = os.path.splitext(filename)
    if ext in ('.png', '.jpeg'):
        return 'image'
    if ext == '.pdf':
        return 'pdf'


def check_cdc(confirmed_data: dict, email: str, db_path: str = None) -> bool:
    """ Check if user's data is found in CDC Database to prevent fraud vaccine cards

    Usage:

        >>> from cvp.app.utils import check_cdc
        >>> bool_ = check_cdc(confirmed_data, email)

    Args:
        confirmed_data (dict): Data from users' vaccine cards
        email (str): user's email that associate with CDC Database

    Returns:
        flag (bool): False if account email not found in CDC Database or data does not match. True otherwise

    """
    db_path = db_path or cdc_db_path
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"File {db_path} was not found. Current dir: {os.getcwd()}")

    db = Database(db_path)
    try:
        acc = db.select('*', profile_table, f'Email = "{email}"')
        if not acc:
            return False  # Account was not found.
        acc_dict = {
            'first_name': acc[0][3],
            'mid_initial': acc[0][4],
            'dob': acc[0][5],
            'first_dose': acc[0][6],
            'second_dose': acc[0][9],
            'last_name': acc[0][2],
            'patient_num': acc[0][1],
            'clinic_site': acc[0][8],
            'date_first': acc[0][7],
            'date_second': acc[0][10]
        }
        for key, value in acc_dict.items():
            if re.sub(r'\s+', '', str(acc_dict[key])) == re.sub(r'\s+', '', str(confirmed_data[key])):
                continue
            else:
                return False

    finally:
        db.close_connection()
    return True


def authenticate(password, email=None, account_id=None):
    """
    Authenticate user's email and password with database.
    Has to have email or account_id to find account information. Only one of them is required.
    :param email: email of user
    :param password: password of user
    :param account_id: user's account_id
    return tuple of account information if succeeded else return error message
    """
    if not password or (not email and not account_id):
        return 'Incorrect input.'
    db = Database(db_path)
    try:
        if email:
            acc = db.select('*', account_table, f'Email = \"{email}\"')
        elif account_id:
            acc = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')
        else: acc = None

        if not acc:  # account was not found with this email
            return 'Account was not found.'
        if acc:  # account with this email is in our database
            # handle incorrect input
            db_password, db_salt = b64decode(acc[0][1]), b64decode(acc[0][3])
            hashed_pass, _ = generate_hash(password=password, salt=db_salt)
            if hmac.compare_digest(hashed_pass, db_password):  # login
                return acc[0]
            else: return 'Password did not match'

    finally:
        db.close_connection()


def is_user(email):
    """
    Check if this email is in the database.
    :param email: email of the user to be searched.
    :return: account information if found else False
    """
    db = Database(db_path)
    try:
        acc = db.select('*', account_table, f'Email = \"{email}\"')
        if not acc:  # account was not found with this email
            return f'Account was not found with this email.'
        else: return acc[0]

    finally:
        db.close_connection()


def update_password(new_password, email=None, acc=None):
    """
    Update account's password.
    :param email: email
    :param new_password: new password
    :param acc: account id
    :return: True if succeeded else False.
    """
    db = Database(db_path)
    try:
        hashed_pass, hashed_salt = generate_hash(new_password)
        hashed_pass = b64encode(hashed_pass).decode('utf-8')
        hashed_salt = b64encode(hashed_salt).decode('utf-8')
        if acc:
            db.update((hashed_pass, hashed_salt), ('Password', 'Salt'), account_table, f'User_Account_ID = \"{acc}\"')
        elif email and type(is_user(email)) == tuple:
            db.update((hashed_pass, hashed_salt), ('Password', 'Salt'), account_table, f'Email = \"{email}\"')
        else: return False
        return True

    finally:
        db.close_connection()


def update_account(account_id, fname=None, lname=None, email=None):
    db = Database(db_path)
    try:
        if fname:
            db.update((fname,), ('First_Name',), account_table, f'User_Account_ID = \"{account_id}\"')
        if lname:
            db.update((lname,), ('Last_Name',), account_table, f'User_Account_ID = \"{account_id}\"')
        if email:
            db.update((email,), ('Email',), account_table, f'User_Account_ID = \"{account_id}\"')
    finally:
        db.close_connection()


def generate_account(session, profile_data):
    db = Database(db_path)
    try:
        # Get largest account_id in database and increment account_id by 1
        new_account_id = db.select(values='max(User_Account_ID)', table_name=account_table)[0][0] + 1

        hashed_pass, hashed_salt = generate_hash(session['password'])
        hashed_pass = b64encode(hashed_pass).decode('utf-8')
        hashed_salt = b64encode(hashed_salt).decode('utf-8')
        account_value = (session['email'], profile_data['last_name'], profile_data['first_name'],
                         hashed_pass, new_account_id, hashed_salt)

        profile_value = (new_account_id, profile_data['patient_num'], profile_data['last_name'],
                         profile_data['first_name'], profile_data['mid_initial'], profile_data['dob'], profile_data['first_dose'],
                         profile_data['date_first'], profile_data['clinic_site'], profile_data['second_dose'],
                         profile_data['date_second'])

        db.insert(account_value, account_table)
        db.insert(profile_value, profile_table)
        return True
    finally:
        db.close_connection()


def get_profile(account_id):
    db = Database(db_path)
    try:
        acc = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')[0]
        record = db.select('*', profile_table, f'User_Account_ID = \"{account_id}\"')[0]
        return __form_dict(acc, record)
    finally:
        db.close_connection()


def __form_dict(acc, record):
    res = dict()
    res['email'] = acc[0]
    res['user_name'] = acc[4]
    res['patient_num'] = record[1]
    res['record_last_name'] = record[2]
    res['record_first_name'] = record[3]
    res['middle_initial']: record[4]
    res['dob'] = record[5]
    res['vaccine_name'] = record[6]
    res['vaccine_date1'] = record[7]
    res['hospital'] = record[8]
    res['vaccine_date2'] = record[10]
    return res


def encode_token(to_be_encrypted, salt):
    return ts.dumps(to_be_encrypted, salt)


def decode_token(token, salt, time):
    try:
        return ts.loads(token, salt=salt, max_age=time)

    except itsdangerous.exc.SignatureExpired or itsdangerous.exc.BadSignature or itsdangerous.exc.BadTimeSignature:
        return False


def renew_token(token, salt, time):
    extracted = decode_token(token, salt, time)
    if extracted:
        token = encode_token(extracted, salt)

    return extracted, token

