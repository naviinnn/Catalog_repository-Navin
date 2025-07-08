"""
Pytest tests for UserService methods.

Includes tests for:
- Retrieving users by username, email, and ID
- Creating users
- Checking user existence by username and email
- Handling user not found and data exceptions
"""

import pytest
from unittest.mock import patch, MagicMock
from service.user_service import UserService
from dto.user import User
from exception.catalog_exception import DataNotFoundError, DatabaseConnectionError

import bcrypt
import pytest
from unittest.mock import patch
from service.user_service import UserService
from dto.user import User
from exception.catalog_exception import DataNotFoundError

# Sample password for hashing
# This should be a secure password in a real application
sample_password = "TestPassword123!"
hashed_password = bcrypt.hashpw(sample_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@pytest.fixture
def sample_user_dict():
    return {
        'user_id': 1,
        'username': 'navin',
        'email': 'navin@example.com',
        'password_hash': hashed_password,
        'created_at': '2025-07-07 10:00:00'
    }

@pytest.fixture
def sample_user():
    return User(
        user_id=1,
        username='navin',
        email='navin@example.com',
        password_hash=hashed_password,
        created_at='2025-07-07 10:00:00'
    )

@patch.object(UserService, '_execute_query')
def test_get_user_by_username_found(mock_execute, sample_user_dict):
    mock_execute.return_value = sample_user_dict
    service = UserService()
    user = service.get_user_by_username('navin')
    assert user.username == 'navin'
    assert user.email == 'navin@example.com'

@patch.object(UserService, '_execute_query')
def test_get_user_by_username_not_found(mock_execute):
    mock_execute.return_value = None
    service = UserService()
    user = service.get_user_by_username('unknown')
    assert user is None

@patch.object(UserService, '_execute_query')
def test_get_user_by_email_found(mock_execute, sample_user_dict):
    mock_execute.return_value = sample_user_dict
    service = UserService()
    user = service.get_user_by_email('navin@example.com')
    assert user.username == 'navin'
    assert user.user_id == 1

@patch.object(UserService, '_execute_query')
def test_get_user_by_email_not_found(mock_execute):
    mock_execute.return_value = None
    service = UserService()
    user = service.get_user_by_email('unknown@example.com')
    assert user is None

@patch.object(UserService, '_execute_query')
def test_get_user_by_id_found(mock_execute, sample_user_dict):
    mock_execute.return_value = sample_user_dict
    service = UserService()
    user = service.get_user_by_id(1)
    assert user.username == 'navin'

@patch.object(UserService, '_execute_query')
def test_get_user_by_id_not_found(mock_execute):
    mock_execute.return_value = None
    service = UserService()
    with pytest.raises(DataNotFoundError):
        service.get_user_by_id(999)

@patch.object(UserService, '_execute_query')
def test_create_user(mock_execute, sample_user):
    mock_execute.return_value = 5
    service = UserService()
    user_id = service.create_user(sample_user)
    assert user_id == 5

@patch.object(UserService, '_execute_query')
def test_check_user_exists_by_username_true(mock_execute):
    mock_execute.return_value = {'exists': 1}
    service = UserService()
    assert service.check_user_exists_by_username('navin') is True

@patch.object(UserService, '_execute_query')
def test_check_user_exists_by_username_false(mock_execute):
    mock_execute.return_value = {'exists': 0}
    service = UserService()
    assert service.check_user_exists_by_username('unknown') is False

@patch.object(UserService, '_execute_query')
def test_check_user_exists_by_email_true(mock_execute):
    mock_execute.return_value = {'exists': 1}
    service = UserService()
    assert service.check_user_exists_by_email('navin@example.com') is True

@patch.object(UserService, '_execute_query')
def test_check_user_exists_by_email_false(mock_execute):
    mock_execute.return_value = {'exists': 0}
    service = UserService()
    assert service.check_user_exists_by_email('no@mail.com') is False
