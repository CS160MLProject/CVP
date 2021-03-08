"""Test of demo_account.py"""
from cvp.data.demo_account import *

TOKEN_SIZE = 14  # token length of output line


def test_accounts_txt():
    assert generate_accounts(), 'Error occoured when generating sample accounts'
    with open(ACCOUNTS) as output_file:
        counter = 0
        while account := output_file.read():
            counter += 1
            tokens = account.split()
            print(tokens)
            assert len(tokens) == TOKEN_SIZE, f'Output\'s token size should be {TOKEN_SIZE}, returned {len(tokens)}'
        assert counter == ACCOUNT_SIZE, f'Output file\'s account size should be {ACCOUNT_SIZE}, returned {counter}'
