from cvp.app.utils import *
import time
import pytest


class TestUtils():
    def test_invalid_register_input(self):
        """
        Test if invalid_register_input return error message if there is any errors.
        """

        valid_email_format = 'hello@me.com'
        valid_pass = valid_conf_pass = 'ValidPassword12!'
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

    def test_valid_email(self):
        """
        Test if valid_email validate email as expected.
        """
        valid_email_format = 'hello@me.com'
        invalid_email = 'this is invalid'
        assert valid_email(valid_email_format), f'Should return True for email {valid_email_format}'
        assert not valid_email(invalid_email), f'Should return False for email {invalid_email}'

    def test_valid_password(self):
        # === Test Inputs ===#
        PASSWORD = 'Correct@Password*101'
        WRONG_PASS = 'wrong_password'

        # === Trigger Outputs ===#
        assert valid_password(PASSWORD)
        assert not valid_password(WRONG_PASS)

    def test_get_file_ext(self):
        """
        Test get_file_ext return classified file type as expected.
        """
        image_file = 'image_file.png'
        pdf_file = 'pdf_file.pdf'
        other_file = 'other.exe'
        assert get_file_ext(image_file) == 'image', f'Should return \'image\' for {image_file}'
        assert get_file_ext(pdf_file) == 'pdf', f'Should return \'pdf\' for {pdf_file}'
        assert get_file_ext(other_file) is None, f'Should return None for {other_file}'

    def test_check_cdc(self):
        # === Test Inputs ===#
        db_path = 'tests/data/test_cdc.db'
        confirmed_data = {
            'first_name': 'Quang Duy',
            'mid_initial': '',
            'dob': '11/19/1999',
            'first_dose': 'Janssen',
            'second_dose': '',
            'last_name': 'Tran',
            'patient_num': '',
            'clinic_site': 'mo vax',
            'date_first': '04/08/21',
            'date_second': ''
        }
        email = 'quangduytran99@gmail.com'

        # === Trigger Outputs ===#
        assert check_cdc(confirmed_data=confirmed_data, email=email, db_path=db_path)

        with pytest.raises(FileNotFoundError):
            WRONG_PATH = 'WRONG/PATH'
            check_cdc(confirmed_data, email, WRONG_PATH)

    def test_authenticate(self):
        """
        """
        db = Database(db_path)
        try:
            # get the existing information and test if it authenticate correctly
            email, _, acc_id, _, username = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
            rec = db.select('*', profile_table, f'User_Account_ID = \"1\"')[0]
            password = f'{rec[3]}{rec[2]}'.lower()
            assert type(authenticate(password, email=email)) == tuple, \
                f'Authentication with existing account failed using email {email=}, {password=}'
            assert type(authenticate(password, account_id=acc_id)) == tuple, \
                f'Authentication with existing account failed using account id. {acc_id=}, {password=}'

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

    def test_is_user(self):
        """
        """
        db = Database(db_path)
        try:
            # get the existing information and test if it return True correctly
            email, _, acc_id, _, username = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
            # password = f'{fname}{lname}'.lower()
            assert type(is_user(email)) == tuple, 'should return account info with existing email.'

            # test if return False with fake email
            fake_email = 'fake email'
            assert type(is_user(fake_email)) == str, 'Should return error message with fake email.'

        finally:
            db.close_connection()

    def test_update_password(self):
        db = Database(db_path)
        try:
            # get the existing information and test if it return True correctly
            email, _, acc_id, _, username = db.select('*', account_table, f'User_Account_ID = \"2\"')[0]
            new_pass = 'new_password'
            assert update_password(new_pass, email=email), 'should return True if updated successfully.'

            # test if return False with fake email
            fake_email = 'fake email'
            assert isinstance(update_password(new_pass, email=fake_email), str), 'Should return False with fake email.'

            assert update_password(new_pass, acc=acc_id)
        finally:
            db.close_connection()

    def test_update_account(self):
        db = Database(db_path)
        try:
            # get the existing information to test
            original_email, _, acc_id, _, original_username = \
                db.select('*', account_table, f'User_Account_ID = \"1\"')[0]

            new_username = 'new_username'
            new_email = 'new_email@email.com'

            # test one by one
            # test first name update
            update_account(acc_id, uname=new_username)
            _, _, _, _, username = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
            assert username == new_username, f'New first name is not updated correctly'

            # test email update
            update_account(acc_id, email=new_email)
            email, _, _, _, _ = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
            assert email == new_email, f'New email is not updated correctly'

            # test all update
            update_account(acc_id, uname=new_username, email=original_email)
            email, _, _, _, username = db.select('*', account_table, f'User_Account_ID = \"1\"')[0]
            assert email == original_email, f'Email is not updated correctly'
            assert username == new_username, f'username is not updated correctly'

        finally:
            db.close_connection()

    def test_generate_account(self):
        db = Database(db_path)
        try:
            size = db.select(values='count(*)', table_name=account_table)[0][0]
        finally:
            db.close_connection()

        new_session = dict()
        new_session['email'] = f'email{size}@test.com'
        new_session['password'] = 'password'

        profile_data = dict()
        profile_data['last_name'] = 'lastname'
        profile_data['first_name'] = 'firstname'
        profile_data['patient_num'] = '1234'
        profile_data['mid_initial'] = 'T'
        profile_data['dob'] = 'Apr 16, 1990'
        profile_data['first_dose'] = 'Something'
        profile_data['date_first'] = 'Apr 08, 2021'
        profile_data['clinic_site'] = 'Hospital'
        profile_data['second_dose'] = 'Something2'
        profile_data['date_second'] = 'Apr 12, 2021'

        # assert generate_account(new_session, profile_data), f'Did not generate account successfully with valid data'
        account_id = generate_account(new_session, profile_data)
        assert account_id == size + 1

    def test_get_profile(self):
        acc, is_tampered = get_profile(1)
        assert type(acc) == dict, f'Did not get profile with valid ID'
        assert not is_tampered, f'User_Account_ID 1 is tampered'
        assert len(acc) == 13

    def test_encode_decode_token(self):
        to_be_encrypted = 'Super Secret'
        test_key = 'TEST_KEY'
        # test encoded token can decode and obtain the same value as encrypted.
        assert decode_token(encode_token(to_be_encrypted, salt=test_key), salt=test_key, time=10) == to_be_encrypted, \
            f'Decode function with encoded token should return the same as the to_be_encrypted.'

    def test_renew_token(self):
        to_be_encrypted = 'Super Secret'
        test_key = 'TEST_KEY'
        token = encode_token(to_be_encrypted, salt=test_key)
        extracted, token = renew_token(token, salt=test_key, time=1)
        assert extracted == to_be_encrypted, f'Did not extract the encrypted value.'
        time.sleep(2)
        extracted, token = renew_token(token, salt=test_key, time=1)

        assert not extracted, f'Expired token should not extract any value and should return False.'

    def test_upload_and_download_profile_picture(self):
        # === Test Inputs ===#
        photo_name = 'Duy.jpg'
        folder_path = 'dataset/raw'
        save_path = 'tests/app'

        #=== Trigger Output ===#
        upload_to_s3(file_name=photo_name, folder_path=folder_path)
        download_from_s3(file_name=photo_name, save_path=save_path)

        assert os.path.exists(os.path.join(save_path, photo_name))

        with pytest.raises(FileNotFoundError):
            wrong_path = 'wrong/path'
            upload_to_s3(photo_name, wrong_path)

        with pytest.raises(FileNotFoundError):
            non_existed_photo = 'wrong_photo.png'
            upload_to_s3(non_existed_photo, save_path)

        with pytest.raises(FileNotFoundError):
            wrong_path = 'wrong/path'
            download_from_s3(photo_name, wrong_path)

        with pytest.raises(FileNotFoundError):
            non_existed_photo = 'wrong_photo.png'
            download_from_s3(non_existed_photo, save_path)


    def test_clean_up_images(self):
        #=== Test Inputs ===#
        save_folder = 'tests/app'
        file_name = 'will_be_deleted.txt'
        save_path = os.path.join(save_folder, file_name)
        with open(save_path, 'w') as file:
            pass

        #=== Trigger Output ===#
        clean_up_images(file_name, save_folder)

        assert not os.path.exists(save_path)


    def test_generate_block_hash(self):
        #=== Test Inputs ===#
        items = ['dummy name', 'dummy sentence']
        salt = os.urandom(16)

        #=== Trigger Output ===#
        result = generate_block_hash(items, salt)
        byte_result = b64decode(result)

        assert isinstance(result, str)
        assert isinstance(byte_result, bytes)
