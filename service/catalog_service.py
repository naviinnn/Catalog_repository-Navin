import mysql.connector
from utils.db_get_connection import get_connection
from dto.catalog import Catalog
from exception.catalog_exception import DataNotFoundError, DatabaseConnectionError
from utils.logger import logger

class CatalogService:
    """
    Service layer for Catalog operations, interacting with the database.
    Encapsulates business logic and abstracts database access.
    Logs key actions and errors for traceability.
    """

    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False, commit: bool = False):
        """
        Internal helper to execute database queries, manage connections,
        and handle common database exceptions.
        Logs query execution results and errors.
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

    def create_catalog(self, catalog: Catalog, user_id: int) -> int:
        """
        Adds a new catalog entry to the database, associated with a user.
        Logs the creation action and the assigned catalog ID.
        """
        logger.info(f"Creating new catalog for user_id={user_id} with name='{catalog.name}'")
        query = """
            INSERT INTO catalog (catalog_name, catalog_description, start_date, end_date, status, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (catalog.name, catalog.description, catalog.start_date, catalog.end_date, catalog.status, user_id)
        catalog_id = self._execute_query(query, params, commit=True)
        logger.info(f"Catalog created successfully with ID {catalog_id}")
        return catalog_id

    def get_catalog_by_id(self, catalog_id: int) -> dict:
        """
        Retrieves a single catalog entry by its ID.
        Logs the retrieval attempt and warns if the catalog is not found.
        """
        logger.info(f"Fetching catalog with ID {catalog_id}")
        query = "SELECT * FROM catalog WHERE catalog_id = %s"
        params = (catalog_id,)
        
        catalog_data = self._execute_query(query, params, fetch_one=True)
        if not catalog_data:
            logger.warning(f"Catalog with ID {catalog_id} not found.")
            raise DataNotFoundError(f"Catalog with ID {catalog_id} not found.")
        return catalog_data

    def get_all_catalog(self, search_term: str = '', status_filter: str = None, page: int = 1, per_page: int = 10) -> list:
        """
        Retrieves paginated catalog entries with optional search and status filtering.
        Logs the retrieval request parameters.
        """
        logger.info(f"Retrieving all catalogs | search='{search_term}', status='{status_filter}', page={page}, per_page={per_page}")
        query = "SELECT * FROM catalog WHERE 1=1"
        params = []

        if search_term:
            query += " AND (catalog_id = %s OR catalog_name LIKE %s OR catalog_description LIKE %s)"
            params.extend([search_term, f"%{search_term}%", f"%{search_term}%"])
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        query += " ORDER BY catalog_id DESC"
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        return self._execute_query(query, tuple(params), fetch_all=True)

    def count_catalogs(self, search_term: str = '', status_filter: str = None) -> int:
        """
        Counts total catalog entries matching search and status filters.
        Logs the count query parameters and the resulting count.
        """
        logger.info(f"Counting catalogs | search='{search_term}', status='{status_filter}'")
        query = "SELECT COUNT(*) FROM catalog WHERE 1=1"
        params = []

        if search_term:
            query += " AND (catalog_id = %s OR catalog_name LIKE %s OR catalog_description LIKE %s)"
            params.extend([search_term, f"%{search_term}%", f"%{search_term}%"])
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        result = self._execute_query(query, tuple(params), fetch_one=True)
        count = result['COUNT(*)'] if result else 0
        logger.debug(f"Total catalogs matched: {count}")
        return count

    def update_catalog_by_id(self, catalog_id: int, catalog: Catalog) -> bool:
        """
        Updates an existing catalog entry identified by its ID.
        Logs update attempts and success or warning if no rows affected.
        """
        logger.info(f"Updating catalog ID {catalog_id}")
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
            logger.warning(f"No rows updated for catalog ID {catalog_id}")
            raise DataNotFoundError(f"Catalog with ID {catalog_id} not found for update.")
        logger.info(f"Catalog ID {catalog_id} updated successfully.")
        return True

    def delete_catalog_by_id(self, catalog_id: int) -> bool:
        """
        Deletes a catalog entry by its ID.
        Logs deletion attempts and success or warning if no rows affected.
        """
        logger.info(f"Deleting catalog ID {catalog_id}")
        self.get_catalog_by_id(catalog_id)

        query = "DELETE FROM catalog WHERE catalog_id = %s"
        params = (catalog_id,)

        row_count = self._execute_query(query, params, commit=True)
        if row_count == 0:
            logger.warning(f"No rows deleted for catalog ID {catalog_id}")
            raise DataNotFoundError(f"Catalog with ID {catalog_id} not found for deletion.")
        logger.info(f"Catalog ID {catalog_id} deleted successfully.")
        return True
