# service/authentication_service.py

import bcrypt
from service.user_service import UserService
from exception.catalog_exception import AuthenticationError, DatabaseConnectionError, ValidationError

class AuthenticationService:
    """
    Handles user authentication logic, including password hashing and verification.
    """
    def __init__(self):
        self.user_service = UserService()

    def hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt."""
        if not isinstance(password, str) or not password:
            raise ValidationError("Password must be a non-empty string.")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        """Checks a plain password against a hashed password."""
        if not isinstance(password, str) or not password:
            raise ValidationError("Password must be a non-empty string.")
        if not isinstance(hashed_password, str) or not hashed_password:
            raise ValidationError("Hashed password must be a non-empty string.")
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError:
            # This can happen if the hashed_password is not a valid bcrypt hash
            raise AuthenticationError("Invalid password hash format.")
        except Exception as e:
            raise AuthenticationError(f"An unexpected error occurred during password check: {e}")

    def authenticate_user(self, username_or_email: str, password: str):
        """
        Authenticates a user by username/email and password.
        Returns the User DTO if authentication is successful.
        """
        if not username_or_email or not password:
            raise ValidationError("Username/Email and password are required.")

        try:
            # Try fetching by username first
            user = self.user_service.get_user_by_username(username_or_email)
            if not user:
                # If not found by username, try by email
                user = self.user_service.get_user_by_email(username_or_email)

            if not user:
                raise AuthenticationError("Invalid username or email.")

            if not self.check_password(password, user.password_hash):
                raise AuthenticationError("Invalid password.")

            return user
        except DatabaseConnectionError as e:
            raise DatabaseConnectionError(f"Authentication failed due to database error: {e}")
        except ValidationError as e:
            raise e # Re-raise validation errors directly
        except AuthenticationError as e:
            raise e # Re-raise authentication errors directly
        except Exception as e:
            raise AuthenticationError(f"An unexpected error occurred during authentication: {e}")