import pytest
import os
from cvp.utils import *


def test_sharing_qr():
    account_id = 12345
    qr_file = sharing_qr(account_id=account_id)
    assert os.path.exists(qr_file) is True, f'The qr file is not created in the expected directory.'


def test_invalid_register_input():
    valid_email_format = 'hello@me.com'
    valid_pass = valid_conf_pass = 'password'
    error = invalid_register_input(valid_email_format, valid_pass, valid_conf_pass)
    assert error is None, f'Should return no error message for {valid_email_format=}, {valid_pass=}, {valid_conf_pass=}' \
                          f'returning {error}'

    invalid_email = 'this is invalid'
    error = invalid_register_input(invalid_email, valid_pass, valid_conf_pass)
    assert error, f'Should return error message for {valid_email_format=}, {valid_pass=}, {valid_conf_pass=}' \
                  f'returning {error}'


def test_valid_email():
    valid_email_format = 'hello@me.com'
    invalid_email = 'this is invalid'
    assert valid_email(valid_email), f'Should return True for email {valid_email_format}'
    assert not valid_email(invalid_email), f'Should return Flase for email {invalid_email}'


def test_get_file_ext():
    image_file = 'image_file.png'
    pdf_file = 'pdf_file.pdf'
    other_file = 'other.exe'
    assert get_file_ext(image_file) == 'image', f'Should return \'image\' for {image_file}'
    assert get_file_ext(pdf_file) == 'pdf', f'Should return \'pdf\' for {pdf_file}'
    assert not get_file_ext(pdf_file), f'Should return None for {other_file}'
