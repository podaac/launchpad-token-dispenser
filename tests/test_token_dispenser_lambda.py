"""Unit tests for the token_dispenser_lambda.py module"""

import os
import pytest

import json

# import token_dispenser.token_dispenser_lambda as token_dispenser_lambda
from token_dispenser.token_dispenser_lambda import (satisfy_minimum_alive_secs, is_client_id_valid,
                                                    is_minimum_alive_secs_valid)
import token_dispenser.configuration as configuration
import json


@pytest.fixture(scope="session")
def data_dir():
    """Test data directory."""
    test_dir = os.path.dirname(os.path.realpath(__file__))
    yield os.path.join(test_dir, 'data')


def test_satisfy_minimum_alive_secs(data_dir):
    """Assert the correct satisfy_minimum_alive_secs function is called"""
    full_path = os.path.join(data_dir, 'sample_token.json')
    with open(full_path, 'r') as file:
        data = file.read().replace('\n', '')

    token_json = json.loads(data)
    is_satisfy_minimum_alive_secs = satisfy_minimum_alive_secs(token_json,None)
    assert is_satisfy_minimum_alive_secs == True
    is_satisfy_minimum_alive_secs = satisfy_minimum_alive_secs(token_json, -1)
    assert is_satisfy_minimum_alive_secs == True
    is_satisfy_minimum_alive_secs = satisfy_minimum_alive_secs(token_json, 100)
    assert is_satisfy_minimum_alive_secs == False

def test_is_client_id_valid():
    """Assert the correct is_client_id_valid function is called"""
    is_valid:bool = is_client_id_valid(None)
    assert is_valid == False
    is_valid = is_client_id_valid('  ')
    assert is_valid == False
    is_valid = is_client_id_valid('123')
    assert is_valid == True
    is_valid = is_client_id_valid('myId123')
    assert is_valid == True
    # String including dash is not Alphanumeric
    is_valid = is_client_id_valid('myId-123')
    assert is_valid == False

def test_is_minimum_alive_secs_valid():
    """Assert the correct is_minimum_alive_secs_valid function is called"""
    # None is acceptable because minimum_alive_secs is not a required field
    is_valid:bool = is_minimum_alive_secs_valid(None)
    assert is_valid == True
    is_valid = is_minimum_alive_secs_valid(0)
    assert is_valid == True
    # Input negative minimum_alive_secs value is not allowed
    is_valid = is_minimum_alive_secs_valid(-2)
    assert is_valid == False
    # Number smaller than SESSION_MAXTIMEOUT is allowed
    is_valid = is_minimum_alive_secs_valid(configuration.SESSION_MAXTIMEOUT -2)
    assert is_valid == True
    # Number greater than SESSION_MAXTIMEOUT is not allowed
    is_valid = is_minimum_alive_secs_valid(configuration.SESSION_MAXTIMEOUT +3)
    assert is_valid == False



