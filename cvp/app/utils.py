"""Utilities for routes.py"""
from app import *
from cvp.data.rel_database import Database, HISTORY_LOG_PATH
from cvp.features.transform import generate_hash
import itsdangerous
from itsdangerous import URLSafeTimedSerializer
from base64 import b64decode, b64encode
import pandas as pd
import hmac
import re
import boto3
import botocore
import copy
import os
from dotenv import load_dotenv

load_dotenv()

# Profile Photo
DEFAULT_PROFILE_PHOTO = 'Smiley.png'
SAVE_PROFILE_PICTURE_PATH = 'dataset/processed'
PROFILE_IMAGE_PATH = 'static/profile_pic'
QR_IMAGE_PATH = 'static/QR_Code'

ts = URLSafeTimedSerializer(secret_key=os.environ['secret_key'])


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
        error_msg = 'Please enter all required fields.'

    elif valid_email(email):  # valid email
        if not valid_password(password):
            error_msg = 'Password did not match one of these requirements'
        elif password != confirm_password:  # fail. password did not match
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


def valid_password(password: str) -> bool:
    """Validate password. Password must follow these conditions:
    - 8 characters minimum
    - 21 characters maximum
    - At least 1 uppercase character
    - At least 1 lowercase character
    - Must contains at least 1 special character: @, $, !, %, *, #, ?, &

    Usage
    -----
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

    Usage
    -----
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
            # acc_dict will return `none` from database if the column in null,
            # and confirmed_data will have '' if column is empty or not filled
            # Hence we need to fill the empty string with `none` before comparing them
            if not str(confirmed_data[key]):
                confirmed_data[key] = 'none'

            if re.sub(r'\s+', '', str(acc_dict[key])).lower() == re.sub(r'\s+', '', str(confirmed_data[key])).lower():
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
        else:
            acc = None

        if not acc:  # account was not found with this email
            return 'Account was not found.'
        if acc:  # account with this email is in our database
            # handle incorrect input
            db_password, db_salt = b64decode(acc[0][1]), b64decode(acc[0][3])
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
        acc = db.select('*', account_table, f'Email = \"{email}\"')
        if not acc:  # account was not found with this email
            return f'Account was not found with this email.'
        else:
            return acc[0]

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
        if acc:
            salt = db.select('Salt', account_table, f'''User_Account_ID = {acc}''')
        elif email:
            salt = db.select('Salt', account_table, f'Email = \"{email}\"')
        else:
            salt = None

        if not salt:  # account was not found with this email
            return 'Account was not found.'

        salt = b64decode(salt[0][0])
        hashed_pass, _ = generate_hash(new_password, salt)
        hashed_pass = b64encode(hashed_pass).decode('utf-8')
        if acc:
            db.update((hashed_pass,), ('Password',), account_table, f'User_Account_ID = \"{acc}\"')
        elif email and type(is_user(email)) == tuple:
            db.update((hashed_pass,), ('Password',), account_table, f'Email = \"{email}\"')
        else:
            return False
        return True

    finally:
        db.close_connection()


def update_account(account_id, uname=None, email=None):
    """
    Update account of username or email.
    :param uname: new username.
    :param email: new email.
    """
    db = Database(db_path)
    try:
        if uname:
            db.update((uname,), ('Username',), account_table, f'User_Account_ID = \"{account_id}\"')
        if email:
            db.update((email,), ('Email',), account_table, f'User_Account_ID = \"{account_id}\"')
    finally:
        db.close_connection()


def generate_account(session, profile_data):
    """
    Generate account for registration.
    :param session: dict of session from flask.
    :param profile_data: dict of profile data from flask.
    :return: True if successfully generated.
    """
    db = Database(db_path)
    try:
        # Get cur_hash from last record in database
        last_record_hash = \
        db.select('Block_Hash', profile_table, 'User_Account_ID = (SELECT max(User_Account_ID) FROM profile)')[0][0]

        # Get largest account_id in database and increment account_id by 1
        new_account_id = db.select(values='max(User_Account_ID)', table_name=account_table)[0][0] + 1

        hashed_pass, temp_hashed_salt = generate_hash(session['password'])
        hashed_pass = b64encode(hashed_pass).decode('utf-8')
        hashed_salt = b64encode(temp_hashed_salt).decode('utf-8')
        username = profile_data['first_name'] + ' ' + profile_data['last_name']
        account_value = (session['email'], hashed_pass, new_account_id, hashed_salt, username)

        items = [last_record_hash, new_account_id, profile_data['patient_num'], profile_data['last_name'],
                 profile_data['first_name'], profile_data['mid_initial'], profile_data['dob'],
                 profile_data['first_dose'], profile_data['date_first'], profile_data['clinic_site'],
                 profile_data['second_dose'], profile_data['date_second'], last_record_hash]
        new_hash = generate_block_hash(items, temp_hashed_salt)
        with open(HISTORY_LOG_PATH, 'a') as hist_log_file:
            hist_log_file.write(f'{new_account_id}\t{new_hash}\n')

        items.pop(len(items) - 1)
        items.pop(0)
        items.append(new_hash)

        profile_value = tuple(items)

        db.insert(account_value, account_table)
        db.insert(profile_value, profile_table)
        return new_account_id
    finally:
        db.close_connection()


def get_profile(account_id):
    """
    Get profile with account id.
    :param account_id: account id.
    :return: dictionary of the account and record.
    """
    db = Database(db_path)
    try:
        acc = db.select('*', account_table, f'User_Account_ID = \"{account_id}\"')[0]
        record = db.select('*', profile_table, f'User_Account_ID = \"{account_id}\"')[0]

        # Get block_hash from previous block
        if record[0] == 1:
            prev_hash = os.environ['hash_0']
        else:
            prev_hash = db.select('Block_Hash', profile_table, f'User_Account_ID = \"{account_id - 1}\"')[0][0]

        salt = b64decode(acc[3])
        block_hash = b64decode(record[len(record) - 1])

        # Deep copy record and add prev_block_hash to front and back of the list
        items = copy.deepcopy(list(record[:-1]))
        items.insert(0, prev_hash)
        items.append(prev_hash)

        new_block_hash = generate_block_hash(items, salt)
        new_block_hash_decoded = b64decode(new_block_hash)
        correct_hash = hmac.compare_digest(block_hash, new_block_hash_decoded)

        # Double checking method, check if this_block_hash is stored in local history logs
        if correct_hash:
            hist_log_df = pd.read_csv(HISTORY_LOG_PATH, sep='\t')
            hist_log_block_hash = hist_log_df[hist_log_df['User_Account_ID'] == account_id]['Block_Hash'].values
            if hist_log_block_hash == new_block_hash:
                correct_hash = True
            else:
                correct_hash = False

        # True if correct_hash is wrong (is tampered), False otherwise (is not tampered)
        is_tampered = not correct_hash
        return __form_dict(acc, record), is_tampered
    finally:
        db.close_connection()


def __form_dict(acc, record):
    """
    Helper to form dictionary to be returned in get_profile.
    :param acc: account.
    :param record: profile record.
    :return: dictionary of account and record.
    """
    res = dict()
    res['email'] = acc[0]
    res['user_name'] = acc[4]
    res['user_id'] = record[0]
    res['patient_num'] = record[1]
    res['record_last_name'] = record[2]
    res['record_first_name'] = record[3]
    res['middle_initial'] = record[4]
    res['dob'] = record[5]
    res['vaccine_name'] = record[6]
    res['vaccine_date1'] = record[7]
    res['hospital'] = record[8]
    res['vaccine_name2'] = record[9]
    res['vaccine_date2'] = record[10]
    return res


def encode_token(to_be_encrypted, salt):
    """"
    Encode token.
    :param to_be_encrypted: data to be encrypted.
    :param salt: salt of this token.
    :return: encrypted token.
    """
    return ts.dumps(to_be_encrypted, salt)


def decode_token(token, salt, time):
    """
    Decode token.
    :param token: token to be decrypted.
    :param salt: salt used to encrypt this token.
    :pram time: upper limit of this token's age.
    :return decoded data.
    """
    try:
        return ts.loads(token, salt=salt, max_age=time)

    except itsdangerous.exc.SignatureExpired or itsdangerous.exc.BadSignature or itsdangerous.exc.BadTimeSignature:
        return False


def renew_token(token, salt, time):
    """
    Regenerate token and time signature.
    :param token: to ken to be decrypted.
    :param salt: salt used to encrypt this token.
    :pram time: upper limit of this token's age.
    :return decoded data and new token with new time signature.
    """
    extracted = decode_token(token, salt, time)
    if extracted:
        token = encode_token(extracted, salt)

    return extracted, token


def upload_to_s3(file_name: str, folder_path: str):
    """ Upload users' profile pictures to AWS S3 Bucket. One of the two type is required to be True

    Usage
    -----
    >>> from cvp.app.utils import upload_to_s3
    >>> upload_profile_picture(photo_name, folder_path)

    Args:
        file_name (str): name of file (include file extension)
        folder_path (str): path contains photo

    Returns:

    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder {folder_path} was not found. Current dir: {os.getcwd()}")

    local_path = os.path.join(folder_path, file_name)
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File {local_path} was not found. Current dir: {os.getcwd()}")

    # We have to keep reconnecting to s3 client because it will close after a few second of not using
    client = boto3.client('s3', aws_access_key_id=os.environ['s3_key'],
                          aws_secret_access_key=os.environ['s3_secret_key'], region_name='us-east-2')

    upload_file = profile_bucket + file_name

    client.upload_file(local_path, bucket_name, upload_file)


def download_from_s3(file_name: str, save_path: str = None):
    """ Download file from AWS S3 Bucket to local disk

    Usage
    -----
    >>> from cvp.app.utils import download_from_s3
    >>> get_profile_picture(file_name)

    Args:
        file_name: name of file to download from S3 Bucket
        save_path: local path to save file to

    Returns:

    """
    save_path = save_path or SAVE_PROFILE_PICTURE_PATH

    if not os.path.exists(save_path):
        raise FileNotFoundError(f"Folder {save_path} was not found. Current dir: {os.getcwd()}")

    # We have to keep reconnecting to s3 client because it will close after a few second of not using
    client = boto3.client('s3', aws_access_key_id=os.environ['s3_key'],
                          aws_secret_access_key=os.environ['s3_secret_key'], region_name='us-east-2')

    s3_download_path = profile_bucket + file_name
    save_file = os.path.join(save_path, file_name)

    try:
        client.download_file(bucket_name, s3_download_path, save_file)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == '404':
            raise FileNotFoundError(f'File {s3_download_path} was not found. Please check S3 Bucket in AWS Console.')
        else:
            raise Exception(err)


def clean_up_images(file_name: str, path_to_file: str):
    """ Remove profile and QR_Code image after downloading from S3 Bucket when user logs out

    Usage
    -----
    >>> from cvp.app.utils import clean_up_images
    >>> clean_up_images(file_name, path_to_file)

    Args:
        file_name (str): full name (include file extension) of a file
        path_to_file (str): path to folder where this file is located

    Returns:

    """
    file_to_clean = os.path.join(path_to_file, file_name)
    if os.path.exists(file_to_clean):
        os.remove(file_to_clean)


def generate_block_hash(items: list, salt):
    """ Generate hash for each block in the database

    Args:
        items (list): list of items that need to be converted to hash
        salt (bytes): unique salt to generate hash

    Returns:
        cur_hash (str): hash that converted to string to stored into database and written to file
    """
    string = ""
    for element in items:
        string += str(element)

    cur_hash, _ = generate_hash(string, salt)
    cur_hash = b64encode(cur_hash).decode("utf-8")

    return cur_hash
