import mysql.connector
from utils.db_get_connection import get_connection
from dto.catalog import Catalog
from exception.catalog_exception import DataNotFoundError, DatabaseConnectionError

class CatalogService:
    """
    Service layer for Catalog operations, interacting with the database.
    Encapsulates business logic and abstracts database access.
    (Authorization checks removed, only authentication required for access)
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

    def create_catalog(self, catalog: Catalog, user_id: int) -> int:
        """Adds a new catalog entry to the database, associated with a user."""
        query = """
            INSERT INTO catalog (catalog_name, catalog_description, start_date, end_date, status, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (catalog.name, catalog.description, catalog.start_date, catalog.end_date, catalog.status, user_id)
        catalog_id = self._execute_query(query, params, commit=True)
        return catalog_id

    def get_catalog_by_id(self, catalog_id: int) -> dict:
        """
        Retrieves a single catalog entry by its ID.
        (No ownership check - any authenticated user can view)
        """
        query = "SELECT * FROM catalog WHERE catalog_id = %s"
        params = (catalog_id,)
        
        catalog_data = self._execute_query(query, params, fetch_one=True)
        if not catalog_data:
            raise DataNotFoundError(f"Catalog with ID {catalog_id} not found.")
        return catalog_data

    def get_all_catalog(self, search_term: str = '', status_filter: str = None, page: int = 1, per_page: int = 10) -> list:
        """
        Retrieves paginated catalog entries.
        Includes search by catalog_id or catalog_name and optional status filtering.
        """
        query = "SELECT * FROM catalog WHERE 1=1"
        params = []

        if search_term:
            # Using ILIKE for case-insensitive search (might be LIKE in MySQL depending on collation)
            # For MySQL, LIKE is case-insensitive by default on many installations, or use lower()
            query += " AND (catalog_id = %s OR catalog_name LIKE %s OR catalog_description LIKE %s)"
            params.extend([search_term, f"%{search_term}%", f"%{search_term}%"])
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        query += " ORDER BY catalog_id DESC" # Ensure consistent ordering for pagination

        # Add LIMIT and OFFSET for pagination
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        return self._execute_query(query, tuple(params), fetch_all=True)

    def count_catalogs(self, search_term: str = '', status_filter: str = None) -> int:
        """
        Counts the total number of catalog entries matching the search and filter criteria.
        """
        query = "SELECT COUNT(*) FROM catalog WHERE 1=1"
        params = []

        if search_term:
            query += " AND (catalog_id = %s OR catalog_name LIKE %s OR catalog_description LIKE %s)"
            params.extend([search_term, f"%{search_term}%", f"%{search_term}%"])
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        result = self._execute_query(query, tuple(params), fetch_one=True)
        return result['COUNT(*)'] if result else 0

    def update_catalog_by_id(self, catalog_id: int, catalog: Catalog) -> bool:
        """
        Updates an existing catalog entry identified by its ID.
        (No ownership check - any authenticated user can update)
        """
        # First, check if the catalog exists to raise DataNotFoundError if not
        self.get_catalog_by_id(catalog_id)

        query = """
            UPDATE catalog
            SET catalog_name = %s, catalog_description = %s,
                start_date = %s, end_date = %s, status = %s
            WHERE catalog_id = %s
        """
        params = (catalog.name, catalog.description, catalog.start_date, catalog.end_date, catalog.status, catalog_id)
        
        row_count = self._execute_query(query, params, commit=True)
        if row_count == 0:
            # This case should ideally not be reached if get_catalog_by_id didn't raise
            raise DataNotFoundError(f"Catalog with ID {catalog_id} not found for update (no rows affected).")
        return True

    def delete_catalog_by_id(self, catalog_id: int) -> bool:
        """
        Deletes a catalog entry by its ID.
        (No ownership check - any authenticated user can delete)
        """
        # First, check if the catalog exists to raise DataNotFoundError if not
        self.get_catalog_by_id(catalog_id)

        query = "DELETE FROM catalog WHERE catalog_id = %s"
        params = (catalog_id,)

        row_count = self._execute_query(query, params, commit=True)
        if row_count == 0:
            # This case should ideally not be reached if get_catalog_by_id didn't raise
            raise DataNotFoundError(f"Catalog with ID {catalog_id} not found for deletion (no rows affected).")
        return True