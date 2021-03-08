"""Test of demo_account.py"""
# import target file
from cvp.data.demo_account import *
TOKEN_SIZE = 14  # token length of output line


def test_accounts_txt():
    """Test output file accounts.txt."""
    assert generate_accounts(), 'Error occoured when generating sample accounts'
    try:
        # open output file
        with open(ACCOUNTS) as output_file:
            counter = 0 # initiate counter to count number of accounts generated
            while account := output_file.readline():
                counter += 1
                tokens = account.split(DELIM)
                assert len(tokens) == TOKEN_SIZE, \
                    f'Output\'s token size should be {TOKEN_SIZE}, returned {len(tokens)}, {tokens}'
            assert counter == ACCOUNT_SIZE, f'Output file\'s account size should be {ACCOUNT_SIZE}, returned {counter}'
    except IOError:
        print(IOError)
