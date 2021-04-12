import hmac
import sys
import hmac

# Standard Dist
import pytest

# Project Level Imports
from cvp.features.transform import *

class TestTransform():

    def test_generate_hash(self):
        #=== Test Inputs ===#
        PASSWORD_IN_DATABASE = "Correct&Password.101"

        USER_INPUT_PASSWORD = "Correct&Password.101"

        password_hash, salt = generate_hash(PASSWORD_IN_DATABASE)
        new_hash, _ = generate_hash(USER_INPUT_PASSWORD, salt)

        assert hmac.compare_digest(new_hash, password_hash)

        with pytest.raises(TypeError):
            password_hash, _ = generate_hash(USER_INPUT_PASSWORD, "WRONG_SALT")

    def test_generate_QR_code(self):
        #=== Test Inputs ===#
        LINK = 'https://www.youtube.com/'
        USER_ID = '777'
        SAVE_FOLDER = 'tests/features'

        #=== Expected Output ===#
        expected_file = 'tests/features/777.png'

        #=== Trigger Output ===#
        generate_QR_code(LINK, USER_ID, save=True, save_folder=SAVE_FOLDER)

        assert os.path.exists(expected_file)

        with pytest.raises(FileNotFoundError):
            save_folder = 'WRONG/FOLDER'
            generate_QR_code(LINK, USER_ID, save=True, save_folder=save_folder)