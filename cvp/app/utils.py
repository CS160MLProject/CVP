"""Utilities for routes.py"""
from itsdangerous import URLSafeTimedSerializer
from app import app

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


def check_cdc():
    return True
