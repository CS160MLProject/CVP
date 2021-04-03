import pytest
import os
from cvp.utils import *


def test_sharing_qr():
    account_id = 12345
    qr_file = sharing_qr(account_id=account_id)
    assert os.path.exists(qr_file) is True, f'The qr file is not created in the expected directory.'


def test_invalid_register_input():
    valid_email = 'hello@me.com'
    valid_pass = valid_conf_pass = 'password'
    error = invalid_register_input(valid_email, valid_pass, valid_conf_pass)
    assert error is None, f'Should return no error message for {valid_email=}, {valid_pass=}, {valid_conf_pass=}' \
                          f'returning {error}'

    invalid_email = 'this is invalid'
    error = invalid_register_input(invalid_email, valid_pass, valid_conf_pass)
    assert error, f'Should return error message for {valid_email=}, {valid_pass=}, {valid_conf_pass=}' \
                  f'returning {error}'


