# service/user_service.py

import mysql.connector
from utils.db_get_connection import get_connection
from dto.user import User
from exception.catalog_exception import DataNotFoundError, DatabaseConnectionError

class UserService:
    """
    Service layer for User operations, interacting with the database.
    Encapsulates business logic and abstracts database access.
    """

    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False, commit: bool = False):
        """
        Internal helper to execute database queries, manage connections,
        and handle common database exceptions.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            # Use dictionary=True for fetching rows as dictionaries
            cursor = conn.cursor(dictionary=True) if fetch_one or fetch_all else conn.cursor()
            cursor.execute(query, params or ()) # Pass params as tuple, empty if None

            if commit:
                conn.commit()
                # Return lastrowid for INSERTs, rowcount for UPDATE/DELETE
                return cursor.lastrowid if 'INSERT' in query.upper() else cursor.rowcount
            elif fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return None # For non-fetching queries that don't commit (e.g., SELECT without return)
        except mysql.connector.Error as e:
            if conn and commit: # Only rollback if transaction was intended (commit=True)
                conn.rollback()
            raise DatabaseConnectionError(f"Database error during operation: {e}")
        except Exception as e:
            # Catch unexpected errors to prevent raw exceptions from propagating
            raise Exception(f"An unexpected error occurred in service layer: {e}")
        finally:
            # Ensure resources are closed
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_user_by_username(self, username: str) -> User | None:
        """Retrieves a user by their username."""
        query = "SELECT user_id, username, email, password_hash, created_at FROM users WHERE username = %s"
        params = (username,)
        user_data = self._execute_query(query, params, fetch_one=True)
        # Manually create User object from dictionary
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at']
        ) if user_data else None

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email."""
        query = "SELECT user_id, username, email, password_hash, created_at FROM users WHERE email = %s"
        params = (email,)
        user_data = self._execute_query(query, params, fetch_one=True)
        # Manually create User object from dictionary
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at']
        ) if user_data else None

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by their ID."""
        query = "SELECT user_id, username, email, password_hash, created_at FROM users WHERE user_id = %s"
        params = (user_id,)
        user_data = self._execute_query(query, params, fetch_one=True)
        # Manually create User object from dictionary
        return User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            created_at=user_data['created_at']
        ) if user_data else None

    def create_user(self, user: User) -> int:
        """Adds a new user to the database."""
        query = """
            INSERT INTO users (username, password_hash, email)
            VALUES (%s, %s, %s)
        """
        params = (user.username, user.password_hash, user.email)
        user_id = self._execute_query(query, params, commit=True)
        return user_id