import pytest
import bcrypt
from unittest.mock import MagicMock
from service.authentication_service import AuthenticationService
from dto.user import User
from exception.catalog_exception import ValidationError, AuthenticationError, DatabaseConnectionError

class TestAuthenticationService:

    def setup_method(self):
        self.auth_service = AuthenticationService()

    def test_hash_password_success(self):
        password = "SecurePass123!"
        hashed = self.auth_service.hash_password(password)
        assert isinstance(hashed, str)
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @pytest.mark.parametrize("invalid_password", ["", "   ", None])
    def test_hash_password_invalid_inputs(self, invalid_password):
        with pytest.raises(ValidationError):
            self.auth_service.hash_password(invalid_password)

    def test_check_password_success(self):
        password = "mypassword"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        assert self.auth_service.check_password(password, hashed) is True
        assert self.auth_service.check_password("wrongpassword", hashed) is False

    @pytest.mark.parametrize("password, hashed_password, expected_exception", [
        ("", "somehash", ValidationError),
        ("somepass", "", ValidationError),
        ("", "", ValidationError),
        (None, "somehash", ValidationError),
        ("somepass", None, ValidationError),
        ("somepass", "invalidbcrypthash", AuthenticationError),
        ("validpass", "anotherbadhash", AuthenticationError),
    ])
    def test_check_password_invalid_inputs(self, password, hashed_password, expected_exception):
        with pytest.raises(expected_exception):
            self.auth_service.check_password(password, hashed_password)

    def test_authenticate_user_success_with_username(self):
        password = "userpass"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(user_id=1, username="testuser", password_hash=hashed_password, email="test@example.com", created_at=None)

        self.auth_service.user_service = MagicMock()
        self.auth_service.user_service.get_user_by_username.return_value = user
        self.auth_service.user_service.get_user_by_email.return_value = None

        result = self.auth_service.authenticate_user("testuser", password)
        assert result == user

    def test_authenticate_user_success_with_email(self):
        password = "userpass"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(user_id=2, username="user2", password_hash=hashed_password, email="user2@example.com", created_at=None)

        self.auth_service.user_service = MagicMock()
        self.auth_service.user_service.get_user_by_username.return_value = None
        self.auth_service.user_service.get_user_by_email.return_value = user

        result = self.auth_service.authenticate_user("user2@example.com", password)
        assert result == user

    def test_authenticate_user_missing_username_or_password(self):
        with pytest.raises(ValidationError):
            self.auth_service.authenticate_user("", "somepass")
        with pytest.raises(ValidationError):
            self.auth_service.authenticate_user("user", "")

    def test_authenticate_user_invalid_username_email(self):
        self.auth_service.user_service = MagicMock()
        self.auth_service.user_service.get_user_by_username.return_value = None
        self.auth_service.user_service.get_user_by_email.return_value = None

        with pytest.raises(AuthenticationError):
            self.auth_service.authenticate_user("nonexistent", "somepass")

    def test_authenticate_user_wrong_password(self):
        password = "correctpass"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(user_id=1, username="testuser", password_hash=hashed_password, email="test@example.com", created_at=None)

        self.auth_service.user_service = MagicMock()
        self.auth_service.user_service.get_user_by_username.return_value = user
        self.auth_service.user_service.get_user_by_email.return_value = None

        with pytest.raises(AuthenticationError):
            self.auth_service.authenticate_user("testuser", "wrongpass")

    def test_authenticate_user_database_connection_error(self):
        self.auth_service.user_service = MagicMock()
        self.auth_service.user_service.get_user_by_username.side_effect = DatabaseConnectionError("DB error")

        with pytest.raises(DatabaseConnectionError):
            self.auth_service.authenticate_user("testuser", "somepass")
