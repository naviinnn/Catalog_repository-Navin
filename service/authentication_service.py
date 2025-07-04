import bcrypt
from service.user_service import UserService
from exception.catalog_exception import AuthenticationError, DatabaseConnectionError, ValidationError
from utils.logger import logger

class AuthenticationService:
    """
    Handles user authentication logic, including password hashing and verification.
    """

    def __init__(self):
        self.user_service = UserService()

    def hash_password(self, password: str) -> str:
        """
        Hashes a password using bcrypt.
        Raises ValidationError if the input is invalid.
        """
        if not isinstance(password, str) or not password.strip():
            logger.warning("Invalid password input for hashing.")
            raise ValidationError("Password must be a non-empty string.")
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        logger.debug("Password hashed successfully.")
        return hashed.decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        """
        Checks a plain password against a hashed password.
        Raises ValidationError or AuthenticationError on invalid input or failure.
        """
        if not isinstance(password, str) or not password.strip():
            raise ValidationError("Password must be a non-empty string.")
        
        if not isinstance(hashed_password, str) or not hashed_password.strip():
            raise ValidationError("Hashed password must be a non-empty string.")
        
        try:
            result = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            logger.debug(f"Password check result: {result}")
            return result
        except ValueError:
            logger.error("Invalid bcrypt hash format provided.", exc_info=True)
            raise AuthenticationError("Invalid password hash format.")
        except Exception as e:
            logger.error(f"Unexpected error during password check: {e}", exc_info=True)
            raise AuthenticationError(f"An unexpected error occurred during password check: {e}")

    def authenticate_user(self, username_or_email: str, password: str):
        """
        Authenticates a user by username/email and password.
        Returns the User DTO if authentication is successful.
        Raises AuthenticationError or ValidationError on failure.
        """
        if not username_or_email or not password:
            logger.warning("Missing username/email or password during authentication.")
            raise ValidationError("Username/Email and password are required.")

        try:
            logger.info(f"Authenticating user: {username_or_email}")
            
            user = self.user_service.get_user_by_username(username_or_email) or \
                   self.user_service.get_user_by_email(username_or_email)

            if not user:
                logger.warning(f"User '{username_or_email}' not found.")
                raise AuthenticationError("Invalid username or email.")

            if not self.check_password(password, user.password_hash):
                logger.warning(f"Incorrect password for user '{username_or_email}'.")
                raise AuthenticationError("Invalid password.")

            logger.info(f"User '{username_or_email}' authenticated successfully.")
            return user

        except DatabaseConnectionError as e:
            logger.critical(f"Database error during authentication: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Authentication failed due to database error: {e}")
        except (ValidationError, AuthenticationError):
            raise  # Already logged at origin
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
            raise AuthenticationError(f"An unexpected error occurred during authentication: {e}")
