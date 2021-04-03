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
    invlid_email = 'this is invalid'
    assert valid_email(valid_email), f'Should return True for email {valid_email_format}'
    assert not valid_email(invlid_email), f'Should return Flase for email {invlid_email}'