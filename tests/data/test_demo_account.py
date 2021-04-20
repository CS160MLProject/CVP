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
            assert tokens[10] == tokens[12], f'Should take same type of vaccine for first and second dose.'
            assert tokens[11] < tokens[13], f'Should take second vaccine after first dose.'
            assert int(tokens[4]) <= 9999, f'Patient number should be less than or equal to 9999'
            assert int(tokens[4]) >= 1000, f'Patient number should be greater than or equal to 1000'
        assert counter == ACCOUNT_SIZE, f'Output file\'s account size should be {ACCOUNT_SIZE}, returned {counter}'
