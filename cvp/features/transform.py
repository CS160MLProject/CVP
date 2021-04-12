"""Transform Operation

Transform operations module currently contains functions for the following:
- generate hash for password
- generate_QR_code

USAGE
-----

$ python cvp/features/transform.py

"""
# Standard Dist
import coloredlogs
import logging
import os
import hashlib

# Third Party Imports
import pyqrcode
import png
from pyqrcode import QRCode

# Project Level Imports

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

QR_CODE_FOLDER = 'dataset/processed/QR_Code'


def generate_hash(password: str, salt: bytes=None):
    """Generate hash and salt for password

    Usage
    -----
    >>> from cvp.features.transform import generate_hash
    >>> password = "mypassword"
    >>> hash_ salt = generate_hash(password)

    :param password: User's password
    :return: hash and salt associate with that user's password
    """
    logger.info("Preparing to hash")
    password = password.encode()  # Get an UTF-8 version of the password
    salt = salt or os.urandom(16)  # Save this salt in the database with password
    if not isinstance(salt, bytes):
        raise TypeError("Error found with type of input `salt` when hashing password")
    logger.debug(f"Salt: {salt}")

    logger.info("Hashing password ...")
    password_hash = hashlib.pbkdf2_hmac("sha256", password, salt, 100000)
    logger.debug(f"Hash: {password_hash}")

    logger.info("Finished hashing password!")

    return password_hash, salt


def generate_QR_code(link: str, user_account_id: str, save=False, save_folder: str = None):
    """ Generate QR code with a given profile link

    Args:
        save_folder (str): directory to save the QR image
        link (str): profile link
        user_account_id (str): unique account id
        save (bool): save image as png or not

    Returns:
        *.png: photo of QR_Code
    """
    logger.info('Preparing ...')
    save_folder = save_folder or QR_CODE_FOLDER

    if not os.path.exists(save_folder):
        raise FileNotFoundError(f"File {save_folder} was not found. Current dir: {os.getcwd()}")

    qr_code = pyqrcode.create(link)

    logger.debug(f'{os.path.join(save_folder, user_account_id + ".png")}')

    if save:
        qr_code.png(os.path.join(save_folder, user_account_id + '.png'), scale=8)
        logger.info('SUCCESS: QR_Code saved!')

    logger.info('Finished operation')