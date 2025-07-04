import mysql.connector
from configparser import ConfigParser
from exception.catalog_exception import DatabaseConnectionError
from utils.logger import logger
import os

def get_connection() -> mysql.connector.connection.MySQLConnection:
    """
    Establishes and returns a connection to the MySQL database.
    Logs the process and raises FileNotFoundError or DatabaseConnectionError on failure.
    """
    try:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config',
            'config.ini'
        )

        if not os.path.exists(config_path):
            logger.critical(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        config = ConfigParser()
        config.read(config_path)

        connection = mysql.connector.connect(
            host=config.get('mysql', 'host'),
            user=config.get('mysql', 'user'),
            password=config.get('mysql', 'password'),
            database=config.get('mysql', 'database')
        )
        logger.info("Successfully connected to the MySQL database.")
        return connection

    except mysql.connector.Error as e:
        logger.critical(f"MySQL connection failed: {e}", exc_info=True)
        raise DatabaseConnectionError(f"Database connection failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while connecting to the database: {e}", exc_info=True)
        raise DatabaseConnectionError(f"Unexpected connection error: {e}")
