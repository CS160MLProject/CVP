from cvp.app.utils import *


def test_invalid_register_input():
    """
    Test if invalid_register_input return error message if there is any errors.
    """

    valid_email_format = 'hello@me.com'
    valid_pass = valid_conf_pass = 'password'
    error = invalid_register_input(valid_email_format, valid_pass, valid_conf_pass)
    assert not error, f'Should return no error message for {valid_email_format=}, {valid_pass=}, {valid_conf_pass=}' \
                          f'returning {error}'

    empty_email = ''
    error = invalid_register_input(empty_email, valid_pass, valid_conf_pass)
    assert error, f'Should return error message for {empty_email=}, {valid_pass=}, {valid_conf_pass}'

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


def test_authenticate():
    """
    """
    db = Database(db_path)
    try:
        # get the existing information and test if it authenticate correctly
        email, lname, fname, password,  acc_id, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
        password = f'{fname}{lname}'.lower()
        assert type(authenticate(password, email=email)) == tuple, \
            'Authentication with existing account failed using email.'
        assert type(authenticate(password, account_id=acc_id)) == tuple, \
            'Authentication with existing account failed using account id.'

        # test if authentication failed with correct email and incorrect password
        wrong_pass = 'wrong_pass'
        assert type(authenticate(wrong_pass, email)) == str, \
            'Authentication with correct email and incorrect password should be failed'

        # test authentication of fail if checked with incorrect information
        email = 'fake email'
        acc_id = -1
        assert type(authenticate(wrong_pass, email=email)) == str, \
            'Authentication with fake email and password should be failed.'
        assert type(authenticate(wrong_pass, account_id=acc_id)) == str, \
            'Authentication with fake id and password should be failed.'

    finally:
        db.close_connection()


def test_is_user():
    """

    """
    db = Database(db_path)
    try:
        # get the existing information and test if it return True correctly
        email, lname, fname, password, acc_id, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
        # password = f'{fname}{lname}'.lower()
        assert type(is_user(email)) == tuple, 'should return account info with existing email.'

        # test if return False with fake email
        fake_email = 'fake email'
        assert type(is_user(fake_email)) == str, 'Should return error message with fake email.'

    finally:
        db.close_connection()


def test_update_password():
    db = Database(db_path)
    try:
        # get the existing information and test if it return True correctly
        email, lname, fname, password, acc_id, _ = db.select('*', account_table, f'User_Account_ID = \"2\"')[0]
        new_pass = 'new_password'
        assert update_password(new_pass, email=email), 'should return True if updated successfully.'

        # test if return False with fake email
        fake_email = 'fake email'
        assert not update_password(new_pass, email=fake_email), 'Should return False with fake email.'

        assert update_password(new_pass, acc=acc_id)
    finally:
        db.close_connection()


def test_update_account():
    db = Database(db_path)
    try:
        # get the existing information to test
        original_email, original_lname, original_fname, _, acc_id, _ = \
            db.select('*', account_table, f'User_Account_ID = \"1\"')[0]

        new_lname = 'new_lname'
        new_fname = 'new_fname'
        new_email = 'new_email@email.com'

        # test one by one
        # test first name update
        update_account(acc_id, fname=new_fname)
        _, _, fname, _, _, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
        assert fname == new_fname, f'New first name is not updated correctly'

        # test last name update
        update_account(acc_id, lname=new_lname)
        _, lname, _, _, _, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
        assert lname == new_lname, f'New last name is not updated correctly'

        # test email update
        update_account(acc_id, email=new_email)
        email, _, _, _, _, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
        assert email == new_email, f'New email is not updated correctly'

        # test all update
        update_account(acc_id, fname=original_fname, lname=original_lname, email=original_email)
        email, lname, fname, _, _, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
        assert email == original_email, f'Email is not updated correctly'
        assert lname == original_lname, f'Email is not updated correctly'
        assert fname == original_fname, f'Email is not updated correctly'

    finally:
        db.close_connection()
