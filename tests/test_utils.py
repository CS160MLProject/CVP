import pytest
import os
from cvp.utils import *


def test_sharing_qr():
    account_id = 12345
    qr_file = sharing_qr(account_id=account_id)
    assert os.path.exists(qr_file) is True, f'The qr file is not created in the expected directory.'



