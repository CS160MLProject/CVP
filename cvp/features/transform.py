"""Transform Operation

Transform operations module currently contains functions for the following:
- generate hash for password

USAGE
-----

$ python cvp/features/transform.py

"""
# Standard Dist
import logging
import os
import hashlib
import hmac

# Third Party Imports

# Project Level Imports

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def generate_hash(password: str, salt: bytes=None):
    """Generate hash and salt for password

    Usage
    -----
    >>> from cvp.features.features import generate_hash
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

    logger.debug("Finished hashing password!")
    return password_hash, salt

if __name__ == '__main__':
    password = "mypassword"
    hash, salt = generate_hash(password)

    checking = True  # Change this into True if you want to check if password is being hashed correctly
    if checking:
        logger.info("Checking hashing value ...")
        correct_password = "mypassword"
        new_hash, _ = generate_hash(password, salt)
        logger.debug(f"Hashing is {hmac.compare_digest(new_hash, hash)}")

