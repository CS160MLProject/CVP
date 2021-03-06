import sys

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
