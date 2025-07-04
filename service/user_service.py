import mysql.connector
from utils.db_get_connection import get_connection
from dto.user import User
from exception.catalog_exception import DataNotFoundError, DatabaseConnectionError
from utils.logger import logger

class UserService:
    """
    Service layer for User operations, interacting with the database.
    Encapsulates business logic and abstracts database access.
    Logs key user-related actions and errors.
    """

    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False, commit: bool = False):
        """
        Internal helper to execute database queries, manage connections,
        and handle common database exceptions.
        Logs query execution details.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True) if fetch_one or fetch_all else conn.cursor()
            cursor.execute(query, params or ())

            if commit:
                conn.commit()
                result = cursor.lastrowid if 'INSERT' in query.upper() else cursor.rowcount
                logger.debug(f"Executed query with commit: {query.strip()} | Params: {params} | Result: {result}")
                return result
            elif fetch_one:
                result = cursor.fetchone()
                logger.debug(f"Executed query (fetch_one): {query.strip()} | Params: {params} | Result: {result}")
                return result
            elif fetch_all:
                result = cursor.fetchall()
                logger.debug(f"Executed query (fetch_all): {query.strip()} | Params: {params} | Result count: {len(result)}")
                return result
            return None
        except mysql.connector.Error as e:
            logger.critical(f"MySQL Error: {e} | Query: {query.strip()} | Params: {params}", exc_info=True)
            if conn and commit:
                conn.rollback()
            raise DatabaseConnectionError(f"Database error during operation: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in _execute_query: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred in service layer: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_user_by_username(self, username: str) -> User | None:
        """Retrieves a user by their username."""
        logger.info(f"Fetching user by username: {username}")
        query = "SELECT user_id, username, email, password_hash, created_at FROM users WHERE username = %s"
        params = (username,)
        user_data = self._execute_query(query, params, fetch_one=True)
        if user_data:
            logger.debug(f"User found: {user_data}")
        else:
            logger.warning(f"No user found with username: {username}")
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at']
        ) if user_data else None

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email."""
        logger.info(f"Fetching user by email: {email}")
        query = "SELECT user_id, username, email, password_hash, created_at FROM users WHERE email = %s"
        params = (email,)
        user_data = self._execute_query(query, params, fetch_one=True)
        if user_data:
            logger.debug(f"User found: {user_data}")
        else:
            logger.warning(f"No user found with email: {email}")
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at']
        ) if user_data else None

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by their ID."""
        logger.info(f"Fetching user by ID: {user_id}")
        query = "SELECT user_id, username, email, password_hash, created_at FROM users WHERE user_id = %s"
        params = (user_id,)
        user_data = self._execute_query(query, params, fetch_one=True)
        if user_data:
            logger.debug(f"User found: {user_data}")
        else:
            logger.warning(f"No user found with ID: {user_id}")
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at']
        ) if user_data else None

    def create_user(self, user: User) -> int:
        """Adds a new user to the database."""
        logger.info(f"Creating new user: {user.username}")
        query = """
            INSERT INTO users (username, password_hash, email)
            VALUES (%s, %s, %s)
        """
        params = (user.username, user.password_hash, user.email)
        user_id = self._execute_query(query, params, commit=True)
        logger.info(f"User created successfully with ID {user_id}")
        return user_id
