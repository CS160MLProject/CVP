"""Test of demo_account.py"""
# import target file
import pytest

from cvp.data.demo_account import *
TOKEN_SIZE = 14  # token length of output line
NAMES = 'dataset/raw/names.txt'
ACCOUNTS = 'tests/data/test_accounts.txt'


def test_accounts_txt():
    """Test output file accounts.txt."""
    generate_accounts(NAMES, ACCOUNTS)
    with pytest.raises(OSError):
        generate_accounts(inputfile='Wrong file directory', outputfile=ACCOUNTS)
    # open output file
    with open(ACCOUNTS) as output_file:
        counter = 0 # initiate counter to count number of accounts generated
        output_file.readline() # skip first header line
        while account := output_file.readline():
            counter += 1
            tokens = account.split(DELIM)
            assert len(tokens) == TOKEN_SIZE, \
                f'Output\'s token size should be {TOKEN_SIZE}, returned {len(tokens)}'
        assert counter == ACCOUNT_SIZE, f'Output file\'s account size should be {ACCOUNT_SIZE}, returned {counter}'
