from cvp.utils import *


def test_sharing_qr():
    """
    Test if sharing_qr obtain qr file correctly.
    """
    account_id = 12345
    qr_file = sharing_qr(account_id=account_id)
    assert qr_file == f'dataset/user/{account_id}.png', f'The qr file is not created in the expected directory.'


def test_invalid_register_input():
    """
    Test if invalid_register_input return error message if there is any errors.
    """
    valid_email_format = 'hello@me.com'
    valid_pass = valid_conf_pass = 'password'
    error = invalid_register_input(valid_email_format, valid_pass, valid_conf_pass)
    assert not error, f'Should return no error message for {valid_email_format=}, {valid_pass=}, {valid_conf_pass=}' \
                          f'returning {error}'

    invalid_conf_pass = 'pass'
    error = invalid_register_input(valid_email_format, valid_pass, invalid_conf_pass)
    assert error, f'Should return error message for {valid_email_format=}, {valid_pass=}, {invalid_conf_pass=}' \
                  f'returning {error}'

    invalid_email = 'this is invalid'
    error = invalid_register_input(invalid_email, valid_pass, valid_conf_pass)
    assert error, f'Should return error message for {valid_email_format=}, {valid_pass=}, {valid_conf_pass=}' \
                  f'returning {error}'


def test_valid_email():
    """
    Test if valid_email validate email as expected.
    """
    valid_email_format = 'hello@me.com'
    invalid_email = 'this is invalid'
    assert valid_email(valid_email_format), f'Should return True for email {valid_email_format}'
    assert not valid_email(invalid_email), f'Should return False for email {invalid_email}'


def test_get_file_ext():
    """
    Test get_file_ext return classified file type as expected.
    """
    image_file = 'image_file.png'
    pdf_file = 'pdf_file.pdf'
    other_file = 'other.exe'
    assert get_file_ext(image_file) == 'image', f'Should return \'image\' for {image_file}'
    assert get_file_ext(pdf_file) == 'pdf', f'Should return \'pdf\' for {pdf_file}'
    assert get_file_ext(other_file) is None, f'Should return None for {other_file}'
