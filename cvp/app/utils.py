"""Utilities for routes.py"""
from itsdangerous import URLSafeTimedSerializer
from app import *
import sqlite3
from base64 import b64decode
import hmac
from cvp.features.transform import generate_hash
import re
import os

ts = URLSafeTimedSerializer('secret-key')


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


def send_recovery_email(email, account_id):
    msg_body = 'this is recovery email. Please follow the link\n'


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
        db.create_connection(db_path)
        if email:
            acc = db.select('*', account_table, f'Email = \"{email}\"')
        elif account_id:
            acc = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')
        else:
            return 'Error in select'
        if not acc: # account was not found with this email
            return 'Account was not found.'
        if acc: # account with this email is in our database
            db_password, db_salt = b64decode(acc[0][3]), b64decode(acc[0][5])
            hashed_pass, _ = generate_hash(password=password, salt=db_salt)
            if hmac.compare_digest(hashed_pass, db_password):  # login
                return acc[0]
            else: return 'Password did not match'

    except sqlite3.Error as e:
        raise Exception(e)
    finally:
        db.close_connection()

    return 'Error'


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
        if not acc: # account was not found with this email
            return False
        else:
            return acc[0]

    except sqlite3.Error as e:
        raise Exception(e)
    finally:
        db.close_connection()
