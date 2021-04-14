"""Utilities for routes.py"""
from itsdangerous import URLSafeTimedSerializer
from app import *
from credentials import *
from base64 import b64decode, b64encode
import hmac
from cvp.data.rel_database import Database
from cvp.features.transform import generate_hash
import re
import os

ts = URLSafeTimedSerializer(secret_key=secret_key)


def sharing_qr(account_id):
    """
    Obtain qr for sharing user's profile.
    :param account_id: account's specific id
    :return: Directory of QR code created for user.
    """
    url = f'www.application_home/info_{account_id}.com'
    # directory = get_qr(url)
    directory = f'dataset/user/{account_id}.png'
    return directory


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

    return None


def check_cdc(confirmed_data):
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
    db = Database(db_path)
    try:
        # db.create_connection(db_path)
        if email:
            acc = db.select('*', account_table, f'Email = \"{email}\"')
        elif account_id:
            acc = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')

        if not acc:  # account was not found with this email
            return 'Account was not found.'
        if acc:  # account with this email is in our database
            db_password, db_salt = b64decode(acc[0][3]), b64decode(acc[0][5])
            hashed_pass, _ = generate_hash(password=password, salt=db_salt)
            if hmac.compare_digest(hashed_pass, db_password):  # login
                return acc[0]
            else:
                return 'Password did not match'

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
        db.create_connection(db_path)
        acc = db.select('*', account_table, f'Email = \"{email}\"')
        if not acc:  # account was not found with this email
            return False
        else:
            return acc[0]

    finally:
        db.close_connection()


def update_password(email, password):
    """
    Update account's password.
    :param email: email
    :param password: password
    :return: True if succeeded else False.
    """
    acc = authenticate(password, email=email)
    db = Database(db_path)
    if type(acc) == tuple:
        try:
            hashed_pass, hashed_salt = generate_hash(password)
            hashed_pass = b64encode(hashed_pass).decode('utf-8')
            hashed_salt = b64encode(hashed_salt).decode('utf-8')
            db.update((hashed_pass, hashed_salt), ('Password', 'Salt'), account_table, f'Email = \"{email}\"')
            return True
        finally:
            db.close_connection()
    return False


def generate_account(session, profile_data):
    db = Database(db_path)
    try:
        db.create_connection(db_path)
        new_account_id = db.select(values='count(*)', table_name=account_table)

        hashed_pass, hashed_salt = generate_hash(session['password'])
        hashed_pass = b64encode(hashed_pass).decode('utf-8')
        hashed_salt = b64encode(hashed_salt).decode('utf-8')
        account_value = (session['email'], profile_data['last_name'], profile_data['first_name'],
                         hashed_pass, new_account_id, hashed_salt)
        # dob is not in the html
        dob = 'dob'
        profile_value = (new_account_id, profile_data['patient_num'], profile_data['last_name'],
                         profile_data['first_name'], profile_data['mid_initial'], dob, profile_data['first_dose'],
                         profile_data['date_first'], profile_data['clinic_site'], profile_data['second_dose'],
                         profile_data['date_second'])

        db.insert(account_value, account_table)
        db.insert(profile_value, profile_table)
        return True
    finally:
        db.close_connection()
